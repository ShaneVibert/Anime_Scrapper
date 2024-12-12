import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO
import platform

# Function to fetch genres from AniList
def fetch_genres():
    url = "https://graphql.anilist.co"
    query = """
    query {
      GenreCollection
    }
    """
    response = requests.post(url, json={"query": query})
    if response.status_code == 200:
        return response.json().get("data", {}).get("GenreCollection", [])
    else:
        print(f"Error fetching genres: {response.status_code}")
        return []

# Function to fetch top 10 anime based on genres
def fetch_anime(genres):
    url = "https://graphql.anilist.co"
    query = """
    query ($genres: [String]) {
      Page(page: 1, perPage: 10) {
        media(genre_in: $genres, type: ANIME, sort: POPULARITY_DESC) {
          title {
            romaji
            english
          }
          coverImage {
            medium
          }
          description
          genres
        }
      }
    }
    """
    variables = {"genres": genres}
    response = requests.post(url, json={"query": query, "variables": variables})
    if response.status_code == 200:
        return response.json().get("data", {}).get("Page", {}).get("media", [])
    else:
        print(f"Error fetching anime: {response.status_code}")
        return []

# Function to add scroll wheel functionality
def add_scroll(canvas):
    def on_mouse_wheel(event):
        delta = -1 * (event.delta // 120) if platform.system() == "Windows" else -1 * event.delta
        canvas.yview_scroll(delta, "units")

    # Bind scroll wheel to the canvas
    canvas.bind("<MouseWheel>", on_mouse_wheel)
    canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux scroll up
    canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux scroll down

# Function to display anime results
def display_anime_results(results):
    clear_screen()

    # Scrollable frame for anime results
    canvas = tk.Canvas(root)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    frame = ttk.Frame(canvas)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Add anime details to the frame
    for index, anime in enumerate(results):
        inner_frame = tk.Frame(frame, padx=10, pady=10)
        inner_frame.pack(fill="x", padx=10, pady=10)

        title = anime["title"].get("english") or anime["title"]["romaji"]
        tk.Label(inner_frame, text=f"{index+1}. {title}", font=("Arial", 14, "bold")).pack(anchor="w")

        genres = ", ".join(anime["genres"])
        tk.Label(inner_frame, text=f"Genres: {genres}", font=("Arial", 10, "italic")).pack(anchor="w")

        description = tk.Label(inner_frame, text=anime["description"], wraplength=400, justify="left")
        description.pack(anchor="w")

        image_url = anime["coverImage"]["medium"]
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            img_data = BytesIO(image_response.content)
            img = Image.open(img_data)
            img.thumbnail((100, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(inner_frame, image=photo)
            img_label.image = photo  # Keep a reference
            img_label.pack(side="right")

    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Bind scroll functionality
    add_scroll(canvas)

    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Back button
    back_button = ttk.Button(root, text="Back", command=display_genre_selection)
    back_button.pack(pady=10)

# Function to display genre selection screen
def display_genre_selection():
    clear_screen()

    # Scrollable frame for genre selection
    canvas = tk.Canvas(root)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    frame = ttk.Frame(canvas)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Add genres as checkboxes
    for genre in genres:
        var = tk.BooleanVar()
        genre_vars[genre] = var
        cb = ttk.Checkbutton(frame, text=genre, variable=var)
        cb.pack(anchor="w")

    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Bind scroll functionality
    add_scroll(canvas)

    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Submit button
    submit_button = ttk.Button(root, text="Submit", command=on_submit)
    submit_button.pack(pady=10)

# Clear all widgets from the screen
def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()

# Function triggered by Submit button
def on_submit():
    selected_genres = [genre for genre, var in genre_vars.items() if var.get()]
    if selected_genres:
        results = fetch_anime(selected_genres)
        if results:
            display_anime_results(results)
        else:
            tk.messagebox.showerror("Error", "No results found.")
    else:
        tk.messagebox.showwarning("Warning", "Please select at least one genre.")

# Create the main Tkinter window
root = tk.Tk()
root.title("Anime Finder")
root.geometry("600x600")

# Fetch genres
genres = fetch_genres()
genre_vars = {}

# Display genre selection screen initially
display_genre_selection()

# Run the Tkinter event loop
root.mainloop()
