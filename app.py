import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import requests
from PIL import Image, ImageTk
from io import BytesIO
import random
import chardet
import os
import json

class BingeBuddy:
    def __init__(self, root):
        self.root = root
        self.root.title("BingeBuddy - Movie Recommender")
        self.root.geometry("1100x750")
        self.root.configure(bg="#1a1a1a")
        
        # Initialize variables
        self.df = None
        self.shows_db = {}
        self.movies_db = {}  # New dictionary to store complete movie info
        self.watchlist = self.load_watchlist()
        
        # Load dataset
        self.load_dataset()
        
        # UI Setup
        self.create_widgets()
        self.center_window()
        
        # Set initial placeholder
        self.show_placeholder("Select a genre to browse movies")

    def load_watchlist(self):
        """Load watchlist from JSON file"""
        try:
            if os.path.exists("watchlist.json"):
                with open("watchlist.json", "r") as f:
                    return json.load(f)
            return []
        except Exception as e:
            messagebox.showerror("Watchlist Error", f"Failed to load watchlist:\n{str(e)}")
            return []

    def save_watchlist(self):
        """Save watchlist to JSON file"""
        try:
            with open("watchlist.json", "w") as f:
                json.dump(self.watchlist, f)
        except Exception as e:
            messagebox.showerror("Watchlist Error", f"Failed to save watchlist:\n{str(e)}")

    def add_to_watchlist(self, movie):
        """Add a movie to the watchlist"""
        if movie not in self.watchlist:
            self.watchlist.append(movie)
            self.save_watchlist()
            messagebox.showinfo("Watchlist", f"{movie['title']} added to watchlist!")
        else:
            messagebox.showinfo("Watchlist", f"{movie['title']} is already in your watchlist!")

    def remove_from_watchlist(self, movie):
        """Remove a movie from the watchlist"""
        self.watchlist = [m for m in self.watchlist if m['title'] != movie['title']]
        self.save_watchlist()
        self.show_watchlist()  # Refresh watchlist view

    def create_watchlist_item(self, parent, movie):
        """Create a watchlist item widget"""
        item_frame = tk.Frame(
            parent,
            bg="#2a2a2a",
            padx=10,
            pady=10,
            relief=tk.RAISED,
            bd=1
        )
        item_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Title and Info
        genres_text = " | ".join(movie.get('genres', ['Unknown']))
        tk.Label(
            item_frame,
            text=f"{movie['title']} (⭐ {movie['score']:.1f}, {movie['year'] if pd.notna(movie.get('year')) else 'Unknown'}, 🏷️ {genres_text})",
            font=("Helvetica", 12),
            fg="white",
            bg="#2a2a2a",
            anchor="w"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Remove button
        tk.Button(
            item_frame,
            text="❌ Remove",
            command=lambda: self.remove_from_watchlist(movie),
            font=("Helvetica", 10),
            bg="#e74c3c",
            fg="white",
            relief=tk.FLAT
        ).pack(side=tk.RIGHT, padx=5)

    def show_watchlist(self):
        """Display the watchlist in a new window"""
        if not self.watchlist:
            messagebox.showinfo("Watchlist", "Your watchlist is empty!")
            return

        watchlist_window = tk.Toplevel(self.root)
        watchlist_window.title("Your Watchlist")
        watchlist_window.geometry("800x600")
        watchlist_window.configure(bg="#1a1a1a")

        # Create scrollable canvas
        canvas = tk.Canvas(watchlist_window, bg="#1a1a1a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(watchlist_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add title
        tk.Label(
            scrollable_frame,
            text="Your Watchlist",
            font=("Helvetica", 16, "bold"),
            fg="#e50914",
            bg="#1a1a1a"
        ).pack(pady=10)

        # Add watchlist items
        for movie in self.watchlist:
            self.create_watchlist_item(scrollable_frame, movie)

        # Center the window
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 400
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 300
        watchlist_window.geometry(f'+{x}+{y}')

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

    def detect_encoding(self, file_path):
        """Automatically detect file encoding"""
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read(10000))
        return result['encoding']

    def load_dataset(self):
        """Load and process the movie dataset"""
        csv_path = "MovieGenre.csv"
        if not os.path.exists(csv_path):
            messagebox.showerror("File Missing", f"Could not find {csv_path} in the current directory")
            return

        try:
            # Try detecting encoding first
            encoding = self.detect_encoding(csv_path)
            
            # Try reading with detected encoding
            try:
                self.df = pd.read_csv(
                    csv_path,
                    encoding=encoding,
                    usecols=['Title', 'IMDB Score', 'Genre', 'Poster']
                )
            except:
                # Fallback through common encodings
                encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
                for enc in encodings:
                    try:
                        self.df = pd.read_csv(
                            csv_path,
                            encoding=enc,
                            usecols=['Title', 'IMDB Score', 'Genre', 'Poster']
                        )
                        break
                    except:
                        continue
            
            # Verify data loaded successfully
            if not hasattr(self, 'df') or self.df.empty:
                raise ValueError("Could not read CSV file with any encoding")
            
            # Data Cleaning
            self.df = self.df.dropna(subset=['Poster', 'IMDB Score'])
            self.df['IMDB Score'] = pd.to_numeric(self.df['IMDB Score'], errors='coerce')
            self.df['Year'] = self.df['Title'].str.extract(r'\((\d{4})\)')
            self.df['Genres'] = self.df['Genre'].str.split('|')
            
            # Build genre database and movie database with all genres
            self.shows_db = {}
            self.movies_db = {}
            
            for _, row in self.df.iterrows():
                if not isinstance(row['Genres'], list):
                    continue
                
                # Create movie entry
                title = row['Title']
                if title not in self.movies_db:
                    self.movies_db[title] = {
                        'title': title,
                        'score': row['IMDB Score'],
                        'year': row['Year'],
                        'poster': row['Poster'],
                        'genres': []  # Store all genres for this movie
                    }
                
                for genre in row['Genres']:
                    genre = genre.strip()
                    # Add to genre database
                    if genre not in self.shows_db:
                        self.shows_db[genre] = []
                    self.shows_db[genre].append(self.movies_db[title])
                    
                    # Add to movie's genre list if not already there
                    if genre not in self.movies_db[title]['genres']:
                        self.movies_db[title]['genres'].append(genre)
                    
        except Exception as e:
            messagebox.showerror("Loading Error",
                f"Failed to load data:\n{str(e)}\n\n"
                "Please ensure:\n"
                "1. File is named 'MovieGenre1.csv'\n"
                "2. Contains required columns\n"
                "3. Is in the same folder")
            self.shows_db = {}
            self.movies_db = {}

    def create_widgets(self):
        """Create all UI components"""
        # Header
        header = tk.Frame(self.root, bg="#141414", height=80)
        header.pack(fill=tk.X)
        
        tk.Label(
            header, 
            text="BINGEBUDDY", 
            font=("Helvetica", 24, "bold"), 
            fg="#e50914",
            bg="#141414"
        ).pack(pady=20)
        
        # Control Frame
        control_frame = tk.Frame(self.root, bg="#1a1a1a")
        control_frame.pack(pady=10, fill=tk.X, padx=20)
        
        # Genre Selection
        tk.Label(
            control_frame, 
            text="Select Genre:", 
            font=("Helvetica", 12), 
            fg="white", 
            bg="#1a1a1a"
        ).pack(side=tk.LEFT, padx=10)
        
        self.genre_var = tk.StringVar()
        self.genre_menu = ttk.Combobox(
            control_frame, 
            textvariable=self.genre_var, 
            values=sorted(self.shows_db.keys()) if self.shows_db else ["No genres found"], 
            state="readonly",
            font=("Helvetica", 12),
            width=25
        )
        self.genre_menu.pack(side=tk.LEFT)
        self.genre_menu.bind("<<ComboboxSelected>>", self.load_movies)
        
        # Random Button
        tk.Button(
            control_frame, 
            text="🎲 Random Pick", 
            command=self.random_movie,
            font=("Helvetica", 12),
            bg="#e50914",
            fg="white",
            relief=tk.FLAT,
            padx=15
        ).pack(side=tk.LEFT, padx=20)

        # Watchlist Button
        tk.Button(
            control_frame, 
            text="📋 Watchlist", 
            command=self.show_watchlist,
            font=("Helvetica", 12),
            bg="#2ecc71",
            fg="white",
            relief=tk.FLAT,
            padx=15
        ).pack(side=tk.LEFT, padx=10)
        
        # Search Entry
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            control_frame,
            textvariable=self.search_var,
            font=("Helvetica", 12),
            width=30
        )
        self.search_entry.pack(side=tk.LEFT, padx=20)
        self.search_entry.bind("<Return>", self.search_movies)
        
        tk.Button(
            control_frame, 
            text="🔍 Search", 
            command=lambda: self.search_movies(None),
            font=("Helvetica", 12),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=15
        ).pack(side=tk.LEFT)
        
        # Main Content Canvas
        self.canvas = tk.Canvas(self.root, bg="#1a1a1a", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#1a1a1a")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=20)
        self.scrollbar.pack(side="right", fill="y")

    def load_movies(self, event=None):
        """Load movies for selected genre"""
        genre = self.genre_var.get()
        if not genre or genre not in self.shows_db:
            return
            
        self.show_placeholder("Loading movies...")
        self.root.after(100, lambda: self._load_movies_async(genre))

    def _load_movies_async(self, genre):
        """Async loading of movies"""
        try:
            # Clear previous movies
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            # Load movies for selected genre
            for movie in self.shows_db[genre]:
                self.create_movie_card(movie)
                
            if not self.scrollable_frame.winfo_children():
                self.show_placeholder("No movies found for this genre")
                
        except Exception as e:
            self.show_placeholder(f"Error loading movies: {str(e)}")

    def create_movie_card(self, movie):
        """Create a movie card widget with genre information"""
        card = tk.Frame(
            self.scrollable_frame, 
            bg="#2a2a2a", 
            padx=15, 
            pady=15,
            relief=tk.RAISED,
            bd=0
        )
        card.pack(fill=tk.X, pady=8)
        
        # Poster Frame (left side)
        poster_frame = tk.Frame(card, bg="#2a2a2a")
        poster_frame.pack(side=tk.LEFT)
        
        # Poster Loading Placeholder
        poster_placeholder = tk.Label(
            poster_frame, 
            text="Loading...", 
            bg="#2a2a2a", 
            fg="white",
            width=10,  
            height=8   
        )
        poster_placeholder.pack()
        
        # Load poster async
        self.root.after(100, lambda: self.load_poster(poster_frame, movie['poster']))
        
        # Movie Info Frame (right side)
        info_frame = tk.Frame(card, bg="#2a2a2a")
        info_frame.pack(side=tk.LEFT, padx=15, fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(
            info_frame, 
            text=movie['title'], 
            font=("Helvetica", 14, "bold"),  
            fg="white", 
            bg="#2a2a2a",
            anchor="w",
            wraplength=500  
        ).pack(fill=tk.X)
        
        # Metadata Frame (score, year, genres)
        meta_frame = tk.Frame(info_frame, bg="#2a2a2a")
        meta_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Score
        tk.Label(
            meta_frame, 
            text=f"⭐ {movie['score']:.1f}", 
            fg="#FFD700",
            bg="#2a2a2a",
            font=("Helvetica", 10)
        ).pack(side=tk.LEFT)
        
        # Year
        tk.Label(
            meta_frame, 
            text=f"  📅 {movie['year'] if pd.notna(movie['year']) else 'Unknown'}", 
            fg="#aaaaaa", 
            bg="#2a2a2a",
            font=("Helvetica", 10)
        ).pack(side=tk.LEFT)
        
        # Genres 
       
        genres_text = movie.get('genres',[])
        tk.Label(
            meta_frame, 
            text=f"  🏷️ {genres_text}", 
            fg="#aaaaaa", 
            bg="#2a2a2a",
            font=("Helvetica", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        # Watchlist Button (right side)
        button_frame = tk.Frame(info_frame, bg="#2a2a2a")
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Button(
            button_frame,
            text="➕ Watchlist",
            command=lambda: self.add_to_watchlist(movie),
            font=("Helvetica", 10),
            bg="#2ecc71",
            fg="white",
            relief=tk.FLAT
        ).pack(side=tk.RIGHT, padx=5)

    def load_poster(self, frame, url):
        """Load and display movie poster (smaller size)"""
        try:
            # Clear placeholder
            for widget in frame.winfo_children():
                widget.destroy()
            
            # Download and resize image (smaller size)
            response = requests.get(url, timeout=10)
            img = Image.open(BytesIO(response.content))
            img = img.resize((90, 135), Image.LANCZOS)  # Smaller size
            photo = ImageTk.PhotoImage(img)
            
            # Display image
            label = tk.Label(frame, image=photo, bg="#2a2a2a")
            label.image = photo
            label.pack()
            
        except Exception as e:
            # Show placeholder if error
            for widget in frame.winfo_children():
                widget.destroy()
            tk.Label(
                frame, 
                text="Poster\nNot Available", 
                bg="#333333",
                fg="white",
                width=10,
                height=8
            ).pack()

    def random_movie(self):
        """Recommend a random movie"""
        if not self.movies_db:
            messagebox.showwarning("No Data", "No movies loaded!")
            return
            
        # Pick random movie
        movie = random.choice(list(self.movies_db.values()))
        self.show_movie_popup(movie)

    def show_movie_popup(self, movie):
        """Show movie details in popup (with smaller poster)"""
        popup = tk.Toplevel(self.root)
        popup.title("Your Random Pick")
        popup.geometry("450x450")  
        popup.configure(bg="#1a1a1a")
        popup.resizable(False, False)
        
        # Center popup
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 225
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 225
        popup.geometry(f'+{x}+{y}')
        
        # Content Frame
        content_frame = tk.Frame(popup, bg="#1a1a1a")
        content_frame.pack(pady=15, padx=15, fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(
            content_frame, 
            text="🎉 Your Random Pick", 
            font=("Helvetica", 16, "bold"),  
            fg="#e50914", 
            bg="#1a1a1a"
        ).pack(pady=(0, 10))
        
        # Poster Frame
        poster_frame = tk.Frame(content_frame, bg="#1a1a1a")
        poster_frame.pack(pady=10)
        
        # Try loading poster 
        try:
            response = requests.get(movie['poster'], timeout=5)
            img = Image.open(BytesIO(response.content))
            img = img.resize((150, 225), Image.LANCZOS)  
            photo = ImageTk.PhotoImage(img)
            tk.Label(
                poster_frame, 
                image=photo, 
                bg="#1a1a1a"
            ).pack()
            popup.photo = photo
        except:
            tk.Label(
                poster_frame, 
                text="Poster\nNot Available", 
                bg="#333333",
                fg="white",
                width=15,
                height=10
            ).pack()
        
        # Movie details
        tk.Label(
            content_frame, 
            text=movie['title'], 
            font=("Helvetica", 12, "bold"),  
            fg="white", 
            bg="#1a1a1a",
            wraplength=400  
        ).pack(pady=5)
        
        # Score, Year and Genres
        genres_text = movie.get('genres', [])
        tk.Label(
            content_frame, 
            text=f"⭐ {movie['score']:.1f} | 📅 {movie['year'] if pd.notna(movie['year']) else 'Unknown'} | 🏷️ {genres_text}", 
            font=("Helvetica", 10),  
            fg="#aaaaaa", 
            bg="#1a1a1a"
        ).pack(pady=5)
        
        # Add to Watchlist button
        tk.Button(
            content_frame, 
            text="Add to Watchlist", 
            command=lambda: self.add_to_watchlist(movie),
            font=("Helvetica", 10),
            bg="#2ecc71",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=3
        ).pack(pady=5)
        
        # Close button
        tk.Button(
            content_frame, 
            text="Close", 
            command=popup.destroy,
            font=("Helvetica", 10),  
            bg="#e50914",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=3
        ).pack(pady=5)

    def search_movies(self, event):
        """Search movies by title"""
        query = self.search_var.get().lower()
        if not query:
            return
            
        # Clear previous movies
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Search across all movies
        found_movies = []
        
        for movie in self.movies_db.values():
            if query in movie['title'].lower():
                found_movies.append(movie)

        # Display results
        if found_movies:
            for movie in found_movies:
                self.create_movie_card(movie)
        else:
            self.show_placeholder(f"No movies found for '{query}'")

    def show_placeholder(self, text):
        """Show placeholder text when no movies are displayed"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.scrollable_frame, 
            text=text, 
            font=("Helvetica", 14), 
            fg="white", 
            bg="#1a1a1a"
        ).pack(pady=50)

if __name__ == "__main__":
    root = tk.Tk()
    app = BingeBuddy(root)
    root.mainloop()