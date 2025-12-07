🎭 K-Drama Analytics & Recommendation System

A personal end-to-end data analytics and recommendation system project that combines my own K-drama ratings with a Kaggle dataset of 1,500+ Korean dramas to analyze viewing preferences, compare personal taste with global trends, and generate custom watch recommendations.
The insights are delivered through a multi-page Streamlit web application with full poster visuals.

🚀 Project Overview

This project answers questions like:
How do my ratings compare with global audience ratings?
Which actors and genres consistently match my personal taste?
Which dramas should I watch next based on my preferences?
Which shows do I rate higher or lower than public opinion?

The result is a data-driven recommendation engine with a production-style UI.

🧠 Key Features

✅ Data cleaning & encoding fixes
✅ Title normalization & fuzzy matching between datasets
✅ My Rating vs Global Rating comparison
✅ Actor & Genre preference profiling
✅ Custom content-based recommendation system
✅ Multi-page Streamlit dashboard
✅ Full poster wall with manual image fallback system
✅ Modern project structure (modular utilities & pages)

🗂 Dataset Sources

Kaggle Dataset (1500+ K-Dramas)
Includes:

Title, Year
Genre
Cast
Synopsis
Global Score
Network
Poster URLs

Personal Ratings Dataset (49 Shows)
Includes:

Drama Title
My Rating (out of 10)
Optional Notes / Watch Year

Some recent 2024+ dramas are not present in Kaggle — these are handled using a local poster fallback system.

Application Structure
Kdrama_analytics/
  │
  ├── app.py                     # Main Streamlit app entry point (landing page)
  │
  ├── data/
  │   ├── kdrama_kaggle_1500.csv  # Kaggle dataset
  │   └── my_kdrama_ratings.csv  # Personal ratings
  │
  ├── missing_posters/           # Local poster images for unmatched/newer shows
  │
  ├── notebooks/
  │   └── 01_eda_kdrama.ipynb    # Full exploratory data analysis & model building
  │
  ├── pages/
  │   ├── 1_Overview.py         # Overview + Poster Wall
  │   ├── 2_Analytics.py        # Deep analytics & comparisons
  │   └── 3_Recommendations.py # Personalized recommendations
  │
  ├── utils/
  │   ├── loader.py             # Data loading, cleaning & matching logic
  │   ├── helpers.py            # Stats + poster matching helpers
  │   ├── recommender.py        # Recommendation engine
  │   └── visuals.py            # All charting logic

⚙️ How the System Works (High-Level Flow)

1️⃣ Load Data

Reads Kaggle dataset + personal ratings CSV

2️⃣ Clean & Normalize Titles

Fixes encoding issues
Converts to lowercase
Removes punctuation
Standardizes spacing

3️⃣ Fuzzy Title Matching

Matches personal titles to Kaggle titles using similarity scoring
Handles typos, phrasing differences, and spacing issues

4️⃣ Merge Datasets

Produces a unified dataset with:
My rating
Global score
Genre
Cast
Platform
Poster image

5️⃣ Analytics Layer

Distribution of my ratings
Comparison with global ratings
Actor preference scoring
Genre bias analysis

6️⃣ Recommendation Engine

Filters unwatched shows
Scores candidates using:
Genre similarity
Preferred actors
Global popularity
Ranks top recommendations

7️⃣ Streamlit Frontend

Overview dashboard with poster wall
Analytics page with plots
Recommendation ranking page
Local poster overrides for missing shows

🛠 Tech Stack

Python
Pandas / NumPy
Fuzzy Matching (RapidFuzz)
Streamlit
Matplotlib / Seaborn
Jupyter Notebook (EDA)
Git / GitHub

▶️ How to Run Locally

Clone the repository:

git clone https://github.com/naringrekarchinmay/kdrama-analytics-recommendation-system.git)cd Kdrama_analytics


Install dependencies:
pip install -r requirements.txt


Run the app:

streamlit run app.py

🎯 Future Enhancements (Planned)

✅ Add Gen-AI explanation layer for recommendations:
“Why was this drama recommended to you?”

✅ Natural language search:
“Recommend me a romantic healing drama”

✅ User-uploaded rating support

✅ Cloud deployment

📸 Demo

✅ Home page with overview 
<img width="2560" height="1440" alt="Screenshot 2025-12-07 at 11 06 30 AM" src="https://github.com/user-attachments/assets/7140d847-5bdf-43ec-881e-c6812064e165" />

✅ Full poster wall
<img width="2560" height="1440" alt="Screenshot 2025-12-07 at 6 38 21 PM" src="https://github.com/user-attachments/assets/49579716-52e1-4729-8384-1b84a443d90f" />

✅ My vs Global rating analysis, preference discovery
<img width="2560" height="1440" alt="Screenshot 2025-12-07 at 6 38 28 PM" src="https://github.com/user-attachments/assets/425fa147-649d-4d64-a351-01e1d1a0fce0" />

✅ Curated watchlist recommendations
<img width="2560" height="1440" alt="Screenshot 2025-12-07 at 6 38 37 PM" src="https://github.com/user-attachments/assets/554ab8eb-55a3-4a1b-ac21-20b9d84e1f0e" />





