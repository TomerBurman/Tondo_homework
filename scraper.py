import requests
from bs4 import BeautifulSoup
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed



session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

def scrape_genres():
    url = 'https://www.imdb.com/search'
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}) # included a user agent because imdb didn't authorize my request

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting genre for the genre drop-box
        genres = soup.find('div', id='genreAccordion') # finding the genre accordion
        genres_list = genres.find_all('button')
        genres = [button.find('span').text for button in genres_list]
        return genres
        # 1996-03-01,2023-02-01 date, Sci-Fi,Drama genre, The$20Godfather title
    except Exception as e:
        print(f'Error while scraping genres : {e}')


def build_search_url(titles, genres, actors, directors):
    ''' building url dictionary based on user preferences, returns the url dictionary '''
    base_url = f'https://www.imdb.com/search/?&title_type=feature'
    urls = {"titles" : [], "genres": [], "actors": [], "directors": []}
    urls["titles"] = [base_url + f'&title={title.replace(" ", "%20")}' for title in titles if title]
    urls["genres"] = [base_url + f'&genres={genre}' for genre in genres]
    urls["actors"] = [base_url + f'&role={actor_id}' for actor_id in actors]
    urls["directors"] = [base_url + f'&role={director_id}' for director_id in directors]
    return urls


def scrape_movie_initial_info(url):
    movies = {}
    try:
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # extracting movie div
        movie_list = soup.select_one('div.ipc-page-grid--bias-left.ipc-page-grid__item--span-2')
        # extracting movie list
        movie_data = movie_list.select('li.ipc-metadata-list-summary-item') if movie_list else []
        
        # extracting movie link, movie title, movie id and movie img
        for movie in movie_data[:7]:
            movie_link_element = movie.select_one('a[href]')
            movie_link = movie_link_element['href'].split('/?')[0] if movie_link_element else None
            movie_id = movie_link.split('/')[2] if movie_link else None
            movie_title_element = movie.select_one('h3')
            movie_title = movie_title_element.text if movie_title_element else None
            movie_img_element = movie.select_one('img[src]')
            movie_img = movie_img_element['src'] if movie_img_element else None
            
            if movie_id and movie_title:
                movies[movie_id] = {"movie_title": movie_title, "movie_link": movie_link, "movie_img": movie_img}

        
        return movies
    except Exception as e:
        print(f'Error scraping movie link: {e}')
        return None




def scrape_movie(movie):
    simple_url = 'https://www.imdb.com'
    try:
        response = session.get(simple_url + movie["movie_link"])
        soup = BeautifulSoup(response.text, 'html.parser')

        # extracting header of movie
        movie_info = soup.select_one('div.sc-69e49b85-0')
        movie_header_tag = movie_info.select_one('ul') if movie_info else None
        # extracting timeline information
        movie_timeline_tag = movie_header_tag.select('li') if movie_header_tag else []
        
        # extract release date and movie time with checks
        release_date = movie_timeline_tag[0].select_one('a').text
        if movie_timeline_tag[2].text is not None and len(movie_timeline_tag) == 3:
            movie_time = movie_timeline_tag[2].text

        # extracting genres
        movie_genres = [genre.text for genre in soup.select('div.ipc-chip-list__scroller a span')]

        # extracting plot
        plot = soup.select_one('p.sc-466bb6c-3 span').text if soup.select_one('p.sc-466bb6c-3 span') else None

        # Extract actors and directors, actors have their name and their movie name in the a tags
        actor_tags = soup.select('a[class*="sc-bfec09a1"]')
        actors = [(actor_tags[i].text, actor_tags[i + 1].select_one('span').text) for i in range(0, len(actor_tags) - 1, 2)]
        cast_section = soup.find('section', {'data-testid': 'title-cast', 'class': 'ipc-page-section'})
        row_tags = cast_section.find_all('li')
        directors = []
        for row in row_tags:
            if hasattr(row, 'span') and row.find('span', text="Directors"):
                director_links = row.find_all('a')
                directors = [link.text for link in director_links]
        #directors = [director.text for director in soup.select('div.ipc-metadata-list-item__content-container a')]
        #trailer_tag = soup.select_one('a.aria-labelWatch Blu-ray Version')
        #trailer_url = f'{simple_url}{trailer_tag["href"]}'

        # Update the movie dictionary
        movie.update({
            "release_date": release_date,
            "movie_time": movie_time,
            "actors": actors,
            "directors": directors,
            "plot": plot,
            "genres": movie_genres,
            #"trailer": trailer_url
        })

        return movie
    except Exception as e:
        print(f'Error while scraping movie : {e}')
        return None



def scrape_movies(movie_dictionary_list):
    processed_movies = set()
    futures = []
    # 
    with ThreadPoolExecutor(max_workers=10) as executor:
        for movie_dict in movie_dictionary_list:
            for movie_info in movie_dict.values():
                processed_movies.add(movie_info['movie_link'].split('/')[2])
                future = executor.submit(scrape_movie, movie_info)
                futures.append(future)
            for future in as_completed(futures):
                movie = future.result()
                if movie is not None:
                    processed_movies.add(movie['movie_link'].split('/')[2]) # movie title is in form of '1. Animal', keeping only name
        return processed_movies, movie_dictionary_list





def get_actor_id(name):
    name = name.lower().replace(' ', '%20')
    response = session.get(f'https://v3.sg.media-imdb.com/suggestion/names/x/{name}.json')
    data = response.json()
    return data['d'][0]['id']