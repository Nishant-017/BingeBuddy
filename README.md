# 🎬 BingeBuddy – A Genre-Based Movie Discovery App in Python

**BingeBuddy** is a Python desktop app built with Tkinter that helps users discover movies by genre, view details like ratings and summaries, see posters, and manage a watchlist. Whether you're in the mood for a thriller or just feeling indecisive, BingeBuddy makes picking your next movie easy.

---

## 💡 Features

- 🎭 **Genre-Based Filtering** – Select a genre to view all matching movies.
- 🎲 **Random Movie Generator** – Can’t decide? Let the app pick one for you!
- ⭐ **Watchlist** – Add your favorite movies to a personal watchlist.
- 🖼️ **Poster Preview** – Displays poster images directly in the app.
- 📊 **Movie Info Display** – Shows rating, genre, and summary for each movie.

---

## 🛠️ Built With

- Python 3.x
- Tkinter (GUI)
- Pandas (data handling)
- Requests (to fetch images)
- Pillow (to render images)
- chardet (optional encoding detection)

---

## 📂 Project Structure

bingebuddy/
├── main.py # Main application file
├── movies_dataset.csv # Movie dataset with metadata
├── requirements.txt # Python dependencies
├── README.md # Project documentation
---
## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bingebuddy.git
cd bingebuddy

2. Install Dependencies
Make sure you have Python 3.8 or newer, then run:
pip install -r requirements.txt
3. Run the App
python main.py

📊 Dataset
The app uses a filtered dataset of movies containing:
Title
Genre(s)
Summary
Poster URL
Rating
