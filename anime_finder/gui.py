import tkinter as tk
from tkinter import ttk, messagebox
import threading
from PIL import ImageTk
from .api import fetch_genres, fetch_anime, fetch_popular_anime_for_genre
from .utils import load_image


class AnimeFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anime Finder")
        self.root.geometry("1280x720")

        self.genre_vars = {}
        self.genres = []
        self.init_ui()

    def init_ui(self):
        self.clear_screen()
        self.root.configure(bg="black")  # Set the background to solid black

        loading_label = tk.Label(self.root, text="Loading genres...", font=("Arial", 16), fg="white", bg="black")
        loading_label.pack(pady=20)
        threading.Thread(target=self.fetch_and_display_genres).start()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def fetch_and_display_genres(self):
        self.genres = fetch_genres()
        self.display_scrollable_content(self.genres, self.create_genre_widgets)

    def display_scrollable_content(self, items, widget_creator):
        """Creates a scrollable canvas for dynamic content."""
        self.clear_screen()

        outer_frame = tk.Frame(self.root, bg="black")
        outer_frame.pack(fill="both", expand=True)

        # Scrollable canvas
        canvas = tk.Canvas(outer_frame, highlightthickness=0, bg="black")
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas, style="TFrame")

        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a window inside the canvas for the frame
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Dynamically create widgets inside the frame
        widget_creator(frame, items)

        # Configure the scroll region dynamically
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", configure_scroll_region)

        # Bind mouse wheel events globally to canvas
        def on_mouse_wheel(event):
            # Adjust scrolling direction for platforms
            delta = -1 * (event.delta // 120) if event.delta else event.num
            canvas.yview_scroll(delta, "units")

        # Bind scrolling to the root and canvas
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        self.root.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # macOS scroll up
        self.root.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # macOS scroll down

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        submit_button = ttk.Button(self.root, text="Submit", command=self.on_submit)
        submit_button.pack(pady=10)

    def create_genre_widgets(self, frame, genres):
        """Creates genre checkboxes and loads popular anime images."""
        num_columns = 3
        for index, genre in enumerate(genres):
            var = tk.BooleanVar()
            self.genre_vars[genre] = var

            genre_frame = tk.Frame(frame, pady=5, padx=5, relief="ridge", borderwidth=2, bg="#2E0000")  # Dark blood red
            row, col = divmod(index, num_columns)
            genre_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            cb = ttk.Checkbutton(genre_frame, text=genre, variable=var)
            cb.pack(anchor="n", pady=5)

            # Add "Most Popular" label
            popular_label = tk.Label(genre_frame, text="Most Popular", font=("Arial", 10, "italic"), fg="blue", bg="#2E0000")
            popular_label.pack()

            img_label = tk.Label(genre_frame, text="Loading image...", bg="#2E0000", fg="white")
            img_label.pack()

            # Add a label for the anime title
            title_label = tk.Label(genre_frame, text="Loading title...", wraplength=150, justify="center", bg="#2E0000", fg="white")
            title_label.pack()

            threading.Thread(
                target=self.fetch_and_display_popular_anime,
                args=(genre, img_label, title_label)
            ).start()

    def fetch_and_display_popular_anime(self, genre, img_label, title_label):
        anime = fetch_popular_anime_for_genre(genre)
        if anime:
            img = load_image(anime["coverImage"]["medium"])
            if img:
                photo = ImageTk.PhotoImage(img)
                img_label.config(image=photo, text="")
                img_label.image = photo

            # Update the title label with the anime name
            title = anime["title"].get("english") or anime["title"]["romaji"]
            title_label.config(text=title)

    def on_submit(self):
        selected_genres = [genre for genre, var in self.genre_vars.items() if var.get()]
        if selected_genres:
            results = fetch_anime(selected_genres)
            if results:
                self.display_scrollable_content(results, self.create_anime_widgets)
            else:
                messagebox.showerror("Error", "No results found.")
        else:
            messagebox.showwarning("Warning", "Please select at least one genre.")

    def create_anime_widgets(self, frame, results):
        """Creates widgets to display anime results."""
        for index, anime in enumerate(results):
            inner_frame = tk.Frame(frame, padx=10, pady=10, bg="#2E0000")  # Dark blood red
            inner_frame.grid(row=index, column=0, sticky="w", padx=10, pady=10)

            title = anime["title"].get("english") or anime["title"]["romaji"]
            tk.Label(inner_frame, text=f"{index + 1}. {title}", font=("Arial", 14, "bold"), fg="white", bg="#2E0000").pack(anchor="w")
