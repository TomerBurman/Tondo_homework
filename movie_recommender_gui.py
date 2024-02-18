import tkinter as tk
from tkinter import ttk, Canvas, Scrollbar, Toplevel, Label, Button
from PIL import Image, ImageTk
from scraper import scrape_genres,build_search_url,get_actor_id, scrape_movie_initial_info, scrape_movies
from io import BytesIO
import requests
from collections import OrderedDict
import webbrowser

root = tk.Tk()
root.title("Movie recommendation app")

movie_initial_info = None




def fetch_image(url):
    response = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'})
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    img = img.resize((100, 150), Image.Resampling.LANCZOS)  # Example resize, adjust as needed
    return ImageTk.PhotoImage(img)


def show_movie_details(movie):
    details_window = Toplevel(root)
    details_window.title(movie['movie_title'])
    Label(details_window, text=movie['movie_title']).pack()
    Label(details_window, text=f'Plot : {movie["plot"]}').pack()
    Label(details_window, text=f'Genres : {movie["genres"]}').pack()
    Label(details_window, text=f'Actors (Real name, Name in movie) : {movie["actors"]}',wraplength=400).pack()
    #Label(details_window, text=f'Directors : {movie["directors"]}').pack()
    
    #Button(details_window, text="Open Trailer", command=lambda: webbrowser.open(movie['trailer'])).pack()




def calculate_score(movie_info, user_preferences):
    movie_scores = {}
    for movie_dictionary in movie_info:
        for movie in movie_dictionary.values():
            score = 0
            # Check if 'genres' key exists before trying to access it
            if 'genres' in movie:
                score += len(set(movie['genres']) & set(user_preferences['genres'])) * 1.3
            else:
                print(f"'genres' key missing in movie: {movie.get('movie_title', 'Unknown')}")
            movie_title = [movie['movie_title'].lower().split('.')[1].strip()]
            print(set(movie_title), set(user_preferences['favorite_movies']))
            score += len(set(movie_title) & set(user_preferences['favorite_movies'])) * 5 # giving highest weight to title
            print(score)
            # Since actors are stored in tuples, and you're interested in the first element of each tuple
            movie_actor_names = [actor[0] for actor in movie.get('actors', [])]
            user_actor_names = user_preferences.get('actors', [])
            if user_actor_names is not False:
                score += len(set(movie_actor_names) & set(user_actor_names)) * 1.1
            # Check if 'directors' key exists
            if 'directors' in movie:
                print(len(set(movie['directors']) & set(user_preferences['directors'])))
                score += len(set(movie['directors']) & set(user_preferences['directors']))
            else:
                print(f"'directors' key missing in movie: {movie.get('movie_title', 'Unknown')}")

            movie_scores[movie['movie_link'].split('/')[2]] = score
            movie.update({"movie_score" : score})
    sorted_scores = OrderedDict(sorted(movie_scores.items(), key=lambda item: item[1], reverse=True))
    return sorted_scores


            
            


def search():
    user_preferences['favorite_movies'] = [movie.strip() for movie in other_movies_entry.get().lower().split(',')]
    selected_indices = genre_listbox.curselection()
    user_preferences['genres'] = [genre_listbox.get(i) for i in selected_indices]
    user_preferences['actors'] = [actor.strip() for actor in actors_entry.get().split(',')]
    user_preferences['directors'] = [director.strip() for director in directors_entry.get().split(',')]
    #print(user_preferences["favorite_movies"],user_preferences['genres'], user_preferences['actors'], user_preferences['directors'])
    actor_ids = [get_actor_id(actor) for actor in user_preferences['actors'] if actor]
    director_ids = [get_actor_id(director) for director in user_preferences['directors'] if director]
    search_urls = build_search_url(user_preferences['favorite_movies'],user_preferences['genres'],actor_ids,director_ids)
    print(user_preferences["favorite_movies"])
    print(search_urls)
    movie_initial_info = [scrape_movie_initial_info(url) for sublist in search_urls.values() for url in sublist]
    #print(movie_initial_info)
    (processed_movies, movies_dict) = scrape_movies(movie_initial_info)
    scores = calculate_score(movies_dict, user_preferences)
    results_window = Toplevel(root)
    canvas = Canvas(results_window)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(results_window, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    frame = tk.Frame(canvas)
    canvas.create_window((0,0), window=frame, anchor='nw')
    results_window.title("Search Results")
    current_row = 0
    flattened_movies = [(movie_id, details) for movie_dict in movies_dict for movie_id, details in movie_dict.items()]
    sorted_flattened_movies = sorted(flattened_movies, key=lambda x: x[1]['movie_score'], reverse=True)
    sorted_movies_dict = [{movie_id: details} for movie_id, details in sorted_flattened_movies]
    for movie in sorted_movies_dict:
        for movie_id, movie_details in movie.items():

            build_movie_item(movie_id, movie_details, frame, current_row)
            current_row += 3 
        #build_movie_item(movie,scores)

        # Assuming you have a placeholder image or fetch from URL


def build_movie_item(movie_id, movie_details, frame, current_row):
    img = fetch_image(movie_details['movie_img'])
    img_label = Button(frame, image=img, command=lambda: show_movie_details(movie_details))
    img_label.image = img  # Keep a reference.
    img_label.grid(row=current_row, column=0, sticky="ew", padx=10, pady=10)

    Label(frame, text=movie_details['movie_title']).grid(row=current_row, column=1, sticky='w')
    Label(frame, text=f"Rating: {movie_details['movie_score']:.2f}").grid(row=current_row + 1, column=1, sticky='w')
    Button(frame, text="Details", command=lambda: show_movie_details(movie_details)).grid(row=current_row + 2, column=1, sticky='w')





user_preferences = {
    'favorite_movies': [],
    'genres': [],
    'actors': [],
    'directors':[]
}


# title label
other_movies = ttk.Label(root, text="Other movies:")
other_movies.grid(row=0,column=0,padx=10,pady=10)

# title text
other_movies_entry = ttk.Entry(root)
other_movies_entry.grid(row=0,column=1,padx=10,pady=10)

# genre label
genre_label = ttk.Label(root, text="Genres:")
genre_label.grid(row=1,column=0,padx=10,pady=10)

# genre listbox
genre_listbox = tk.Listbox(root, selectmode='multiple')
genre_listbox.grid(row=1,column=1,padx=10,pady=10)
try:
    for genre in scrape_genres():
        genre_listbox.insert(tk.END, genre)
except Exception as e:
    print("Cannot scrape genres")
# actors label
actors_label = ttk.Label(root, text="Actors:")
actors_label.grid(row=2,column=0,padx=10,pady=10)

# actors text
actors_entry = ttk.Entry(root)
actors_entry.grid(row=2,column=1,padx=10,pady=10)

# directors label
directors_label = ttk.Label(root, text="Directors:")
directors_label.grid(row=3,column=0,padx=10,pady=10)

# directors text
directors_entry = ttk.Entry(root)
directors_entry.grid(row=3,column=1,padx=10,pady=10)


# search button
search_button = ttk.Button(root, text="Search",command=search)
search_button.grid(row=5,column=0,columnspan=2,pady=10)









root.mainloop()


