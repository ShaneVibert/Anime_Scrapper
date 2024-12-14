import tkinter as tk
from tkinter import ttk, messagebox
import threading
from PIL import ImageTk
from .api import fetch_genres, fetch_anime, fetch_popular_anime_for_genre
from .utils import load_image
import ctypes
import platform


def set_window_to_primary_monitor(root):
    system_platform = platform.system().lower()

    if system_platform == "windows":
        # Windows-specific implementation using ctypes
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)  # Screen width
        screen_height = user32.GetSystemMetrics(1)  # Screen height
    elif system_platform == "darwin":
        # macOS-specific implementation using screeninfo
        from screeninfo import get_monitors
        monitor = get_monitors()[0]
        screen_width = monitor.width
        screen_height = monitor.height
    else:
        # Linux-specific implementation using tkinter
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

    # Set the geometry for the window: center it on the primary screen
    root.geometry(f"{screen_width}x{screen_height}")  # Position at top-left (0,0)
    root.attributes("-topmost", False)  # Remove topmost attribute if present


class AnimeFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anime Finder")

        # Set the window size to the primary monitor screen dimensions
        set_window_to_primary_monitor(self.root)

        self.genre_vars = {}
        self.genres = []
        self.instructions_frame = None  # We'll create this later
        self.submit_button_frame = None  # Will store the frame of the submit button
        self.back_button_frame = None  # Will store the frame of the back button
        self.init_ui()

    def init_ui(self):
        self.clear_screen()
        self.root.configure(bg="black")  # Set the background to solid black

        # Create a frame for the left content (genres, anime results, etc.)
        content_frame = tk.Frame(self.root, bg="black")
        content_frame.grid(row=0, column=0, sticky="nsew")

        # Create a frame for the instructions on the right side
        self.create_instructions_box()

        # Create a frame at the bottom for the submit button
        self.submit_button_frame = tk.Frame(self.root, bg="black")
        self.submit_button_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=20)
        self.submit_button = ttk.Button(self.submit_button_frame, text="Submit", command=self.on_submit)
        self.submit_button.pack(pady=10)

        # Set grid weights to make the left frame expand while keeping the instructions box fixed
        self.root.grid_rowconfigure(0, weight=1, uniform="equal")  # Content frame
        self.root.grid_rowconfigure(1, weight=0)  # Submit button frame
        self.root.grid_columnconfigure(0, weight=1)  # Left frame
        self.root.grid_columnconfigure(1, weight=0)  # Instructions frame

        # Display loading label
        loading_label = tk.Label(content_frame, text="Loading genres...", font=("Arial", 16), fg="white", bg="black")
        loading_label.pack(pady=20)

        # Start fetching genres in a separate thread
        threading.Thread(target=self.fetch_and_display_genres).start()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def fetch_and_display_genres(self):
        self.genres = fetch_genres()
        self.display_scrollable_content(self.genres, self.create_genre_widgets)

    def display_scrollable_content(self, items, widget_creator):
        """Creates a scrollable canvas for dynamic content."""
        # Ensure that we are not clearing the instructions box or the submit button
        content_frame = tk.Frame(self.root, bg="black")
        content_frame.grid(row=0, column=0, sticky="nsew")

        # Scrollable canvas
        canvas = tk.Canvas(content_frame, highlightthickness=0, bg="black")
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
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
        self.root.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))  # macOS scroll down

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_instructions_box(self):
        """Creates the instructions box on the right side of the window."""
        instructions_frame = tk.Frame(self.root, bg="#2E0000", padx=20, pady=20)
        instructions_frame.grid(row=0, column=1, sticky="nsew")

        instructions_title = tk.Label(instructions_frame, text="Instructions", font=("Arial", 16, "bold"), fg="white",
                                      bg="#2E0000")
        instructions_title.pack(pady=10)

        instructions_text = (
            "1. Select genres from the list.\n\n"
            "2. Click 'Submit' to find anime based on the selected genres.\n\n"
            "3. The results will show popular anime related to the genres.\n\n"
            "4. Click on the titles to get more information about the anime."
        )

        instructions_label = tk.Label(instructions_frame, text=instructions_text, font=("Arial", 12), fg="white",
                                      bg="#2E0000", justify="left")
        instructions_label.pack()

        # Store the instructions frame so we can hide it later
        self.instructions_frame = instructions_frame

    def create_genre_widgets(self, frame, genres):
        """Creates genre checkboxes and loads popular anime images."""
        num_columns = 6  # Genres will appear in horizontal rows with 6 in each row

        for index, genre in enumerate(genres):
            var = tk.BooleanVar()
            self.genre_vars[genre] = var

            genre_frame = tk.Frame(
                frame, pady=5, padx=5, relief="ridge", borderwidth=2,
                bg="#2E0000", width=150, height=100
            )  # Set the size for the genre frames
            row, col = divmod(index, num_columns)  # Calculate row and column for grid
            genre_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            cb = ttk.Checkbutton(genre_frame, text=genre, variable=var)
            cb.pack(anchor="n", pady=5)

            # Add "Most Popular" label
            popular_label = tk.Label(
                genre_frame, text="Most Popular", font=("Arial", 10, "italic"), fg="blue",
                bg="#2E0000"
            )
            popular_label.pack()

            img_label = tk.Label(genre_frame, text="Loading image...", bg="#2E0000", fg="white")
            img_label.pack()

            # Add a label for the anime title
            title_label = tk.Label(
                genre_frame, text="Loading title...", wraplength=150, justify="center",
                bg="#2E0000", fg="white"
            )
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

    def create_anime_widgets(self, frame, results):
        """Creates the widgets for displaying anime results."""
        for index, anime in enumerate(results):
            anime_frame = tk.Frame(
                frame, pady=10, padx=10, relief="ridge", borderwidth=2, bg="#2E0000", width=200, height=250
            )

            anime_frame.grid(row=index // 2, column=index % 2, padx=10, pady=10, sticky="nsew")

            # Display Anime title
            title = anime["title"].get("english") or anime["title"]["romaji"]
            title_label = tk.Label(anime_frame, text=title, font=("Arial", 12, "bold"), fg="white", bg="#2E0000")
            title_label.pack(pady=5)

            # Display Anime image
            img = load_image(anime["coverImage"]["medium"])
            if img:
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(anime_frame, image=photo, bg="#2E0000")
                img_label.image = photo
                img_label.pack()

            # Display Anime description (if available)
            description = anime.get("description", "No description available.")
            description_label = tk.Label(anime_frame, text=description, font=("Arial", 10), fg="white", bg="#2E0000")
            description_label.pack(pady=5)

    def on_submit(self):
        # Hide the instructions box and submit button when submit is clicked
        if self.instructions_frame:
            self.instructions_frame.grid_forget()

        self.submit_button_frame.grid_forget()  # Hide submit button frame

        # Create and show the back button
        if not self.back_button_frame:
            self.back_button_frame = tk.Frame(self.root, bg="black")
            self.back_button_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=20)
        self.back_button = ttk.Button(self.back_button_frame, text="Back", command=self.on_back)
        self.back_button.pack(pady=10)

        selected_genres = [genre for genre, var in self.genre_vars.items() if var.get()]
        if selected_genres:
            results = fetch_anime(selected_genres)
            if results:
                self.display_scrollable_content(results, self.create_anime_widgets)
            else:
                messagebox.showerror("Error", "No results found.")
        else:
            messagebox.showwarning("Warning", "Please select at least one genre.")

    def on_back(self):
        # Reset the interface to genre selection
        self.back_button_frame.grid_forget()  # Hide the back button
        self.init_ui()  # Reinitialize the interface to allow selecting genres again
