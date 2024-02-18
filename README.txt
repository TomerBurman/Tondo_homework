Dependencies:
install these modules via pip install
pip install requests
pip install beautifulsoup4
pip install Pillow

Functions description:
fetch_image(url) - receives url of an image, sends a get request to scrape it,
compresses the photo to 100 in width and 150 in height and returns ImageTk object

show_movie_details(movie) -  Opens a new window displaying detailed information about the movies, I couldn't finish the trailer on time. it shows movie name, plot, genres, actors, need to add directors

calculate_score(movie_info, user_preferences) -
movie_info - list of dictionaries, keys are movie ids and the values are movie title, genre, plot, directors, actors.
movie_title : {movie_title, genres, actors, directors, plot, release_date, movie_time movie_img, }
user_preferences - users prefernce input, a dictionary with users prefernces.
keys are genres, actors, directors, other_movies
 calculates the sum of unique words that the user entered, it is basically the recommendation system, it gives higher weight to other movies, it gives middle weight to genres and small weight to actors. returns a sorted dictionary of movie scores 
I thought of using bag of words and utilize sklearn library but I didn't have that much data, because the scraping process was really slow, so I limited the numbers of searches and utilized threadpool

search() -constructs url list and fetches movie data based on the user's preferences  entered in the GUI.it then calculates scores for these movies and finally displays results
utilizes canvas to display movie photo in the results.





build_movie_item(movie_id,movie_details,frame,current_row) - 
movie_id - movie_id
movie_details - dictionary of movie details
frame - the frame it should be on 
current_row - current row in the frame
creates a movie item in the GUI, displaying the movies image, title rating and a button for more details

get_actor_id(name) fetches the IMDb ID of an actor or director based on their name, ID is used to build search URLs

scrape_genres() Scrapes a list of movies genres from IMDb. this list is used to populate a dropdown or listbox in the GUI

build_search_url(titles, genres, actors, directors) - builds search URLs for IMDb based on user's prefernce. these URLs are used to fetch movies that match these preferences. it builds a URL for each element in the lists.

scrape_movie_initial_info(url) scrapes initial information about movies from a search URL. this includes movie title, movie link, movie id and movie image URL


scrape_movie(movie) scrapes detailed information about a specific movie, such as its release date, movietime, actors, directors, plot and genres

scrape_movies(movie_dictionary_list)
movie_dictionary_list - a list of dictionaries with keys as movie ids and the values are dictionaries containing genres, movie title, movie img url, plot, actors and directors
utilizes threadpool because the scraping process took to long by itself, so I thought of utilizing threads to scrape pages more efficiently. 





