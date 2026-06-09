# 🎭 K-Drama Analytics & Recommendation System

A personal end-to-end data analytics and recommendation system project that combines my own K-drama ratings with a refreshed master dataset of **1,958 unique Korean dramas**. The project analyzes viewing preferences, compares my personal taste with global trends, and generates custom watch recommendations using standardized drama metadata, fuzzy title matching, and content-based recommendation logic.

The refreshed master dataset was created by combining the original K-drama dataset with an additional 2021–2025 dataset. After schema standardization and smart deduplication, the final dataset includes newer titles, global ratings, genres, synopsis fields, poster/image URLs, cast/lead information, and selected metadata such as writer, director, and vote counts where available.

Because the newer 2021–2025 dataset does not include streaming platform availability, missing platform values are handled honestly as `Unknown`. A separate `platform_overrides.csv` file is used to manually enrich platform information over time without hardcoding those values into the application.

The insights are delivered through a multi-page Streamlit web application with poster visuals, analytics pages, and a personalized recommendation interface.

---

## 🚀 Project Overview

This project answers questions like:

* How do my ratings compare with global audience ratings?
* Which actors and genres consistently match my personal taste?
* Which dramas should I watch next based on my preferences?
* Which shows do I rate higher or lower than public opinion?
* How can newer 2024–2025 dramas be added into the recommendation pipeline?

The result is a data-driven recommendation engine with a production-style Streamlit UI.

---

## 🧠 Key Features

✅ Data cleaning & encoding fixes

✅ Title normalization & fuzzy matching between datasets

✅ Refreshed master dataset with 1,958 unique K-dramas

✅ Smart deduplication across original and newer datasets

✅ My Rating vs Global Rating comparison

✅ Actor & Genre preference profiling

✅ Custom content-based recommendation system

✅ Multi-page Streamlit dashboard

✅ Full poster wall with manual image fallback support

✅ Manual platform override system for missing streaming/platform data

✅ Modern project structure with modular utilities and pages

---

## 🗂 Dataset Sources

### Refreshed Master Dataset — 1,958 Unique K-Dramas

The final master dataset combines:

* Original K-drama dataset through approximately 2023
* Additional 2021–2025 K-drama dataset
* Standardized schema across both datasets
* Smart deduplication using normalized drama titles

The master dataset includes:

* Title
* Start Year / End Year
* Genre
* Cast
* Main Lead 1 / Main Lead 2
* Synopsis
* Global Rating
* Network / Platform where available
* Poster URLs
* Episodes where available
* Votes where available
* Writer where available
* Director where available
* Source dataset tracking

### Personal Ratings Dataset

The personal ratings dataset includes:

* Drama Title
* My Rating out of 10
* Optional notes or watch-related fields, where available

### Platform Override Dataset

The newer 2021–2025 dataset does not include platform or streaming availability. To avoid guessing or hardcoding values, missing platform values are handled as `Unknown`.

A separate file, `platform_overrides.csv`, can be manually updated over time to add platform information for selected dramas.

---

## 📊 Dataset Refresh Summary

The dataset refresh process was completed in `notebooks/02_dataset_refresh_2021_2025.ipynb`.

Final refresh results:

* Combined dataset before deduplication: 2,155 rows
* Final master dataset after smart deduplication: 1,958 unique K-dramas
* Duplicate rows removed: 197
* Remaining duplicate normalized titles: 0
* Newer 2024–2025 dramas included
* Missing platform values handled through `platform_overrides.csv`

The refresh process included:

1. Loading the original K-drama dataset
2. Loading the newer 2021–2025 dataset
3. Comparing column schemas
4. Mapping both datasets into a shared structure
5. Normalizing drama titles
6. Combining both datasets
7. Identifying duplicate titles
8. Smart deduplication while preserving useful fields from both sources
9. Exporting the final `kdrama_master_updated.csv`
10. Creating `platform_overrides.csv` for manual platform enrichment

---

## 📁 Application Structure

```text
Kdrama_analytics/
│
├── app.py                              # Main Streamlit app entry point
│
├── data/
│   ├── kdrama_kaggle_1500.csv          # Original K-drama dataset
│   ├── kdramas_2021_2025_raw.csv       # Newer raw 2021–2025 dataset
│   ├── kdrama_master_updated.csv       # Final cleaned and deduplicated master dataset
│   ├── platform_overrides.csv          # Manual platform corrections
│   └── my_kdrama_ratings.csv           # Personal ratings dataset
│
├── missing_posters/                    # Local poster images for unmatched or fallback shows
│
├── notebooks/
│   ├── 01_eda_kdrama.ipynb             # Exploratory data analysis and initial modeling
│   └── 02_dataset_refresh_2021_2025.ipynb  # Dataset refresh and master dataset creation
│
├── pages/
│   ├── 1_Overview.py                   # Overview dashboard and poster wall
│   ├── 2_Analytics.py                  # Deep analytics and comparisons
│   └── 3_Recommendations.py            # Personalized recommendations
│
├── utils/
│   ├── loader.py                       # Data loading, cleaning, matching, and platform override logic
│   ├── helpers.py                      # Stats and poster matching helpers
│   ├── recommender.py                  # Recommendation engine
│   └── visuals.py                      # Charting logic
│
├── requirements.txt                    # Project dependencies
├── README.md                           # Project documentation
└── .gitignore                          # Ignored files and folders
```

---

## ⚙️ How the System Works

### 1️⃣ Load Data

The app loads the refreshed master dataset and my personal ratings file.

The primary dataset used by the app is:

```text
data/kdrama_master_updated.csv
```

The app also supports fallback loading from the original dataset if the refreshed master dataset is unavailable.

---

### 2️⃣ Apply Platform Overrides

The app checks `platform_overrides.csv` and applies any manually filled platform values.

Only non-empty platform values are applied. Blank values remain unchanged, usually as `Unknown`.

---

### 3️⃣ Clean & Normalize Titles

The system standardizes drama titles by:

* Fixing encoding issues
* Converting titles to lowercase
* Removing punctuation
* Standardizing spacing

This creates a cleaner title field for matching and deduplication.

---

### 4️⃣ Fuzzy Title Matching

Personal watchlist titles are matched to master dataset titles using similarity scoring.

This helps handle:

* Typing differences
* Alternate title formatting
* Spacing differences
* Punctuation differences
* Minor title variations

---

### 5️⃣ Merge Datasets

The app produces a unified analysis dataset containing:

* My rating
* Global score
* Genre
* Cast
* Platform / Network where available
* Poster image
* Synopsis
* Writer / Director where available
* Source dataset information

---

### 6️⃣ Analytics Layer

The analytics layer explores:

* Distribution of my ratings
* Comparison between my ratings and global ratings
* Genre preference patterns
* Actor preference patterns
* Shows I rate higher or lower than public opinion

---

### 7️⃣ Recommendation Engine

The recommendation engine filters unwatched shows and scores candidates using:

* Genre similarity
* Preferred actors
* Global popularity
* Existing personal taste patterns

It then ranks dramas and returns personalized recommendations.

---

### 8️⃣ Streamlit Frontend

The Streamlit app includes:

* Overview dashboard
* Poster wall
* Personal rating comparisons
* Genre and actor analytics
* Recommendation ranking page
* Platform and genre filtering where available

---

## 🛠 Tech Stack

* Python
* Pandas / NumPy
* RapidFuzz for fuzzy matching
* Streamlit
* Matplotlib / Seaborn
* Jupyter Notebook
* Git / GitHub

---

## ▶️ How to Run Locally

Clone the repository:

```bash
git clone https://github.com/naringrekarchinmay/kdrama-analytics-recommendation-system.git
```

Move into the project folder:

```bash
cd Kdrama_analytics
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit app:

```bash
streamlit run app.py
```

---

## 🎯 Future Enhancements

Planned improvements:

✅ Add Gen-AI explanation layer for recommendations
Example: “Why was this drama recommended to you?”

✅ Add natural language search
Example: “Recommend me a romantic healing drama”

✅ Add user-uploaded rating support

✅ Expand platform enrichment using reliable manual or external sources

✅ Improve recommendation scoring with weighted taste profiles

✅ Add cloud deployment

✅ Add model evaluation for recommendation quality

---

## 📸 Demo

### ✅ Home page with overview

<img width="2560" height="1440" alt="Screenshot 2025-12-07 at 11 06 30 AM" src="https://github.com/user-attachments/assets/7140d847-5bdf-43ec-881e-c6812064e165" />

### ✅ Full poster wall

<img width="2560" height="1440" alt="Screenshot 2025-12-07 at 6 38 21 PM" src="https://github.com/user-attachments/assets/49579716-52e1-4729-8384-1b84a443d90f" />

### ✅ My vs Global rating analysis and preference discovery

<img width="2560" height="1440" alt="Screenshot 2025-12-07 at 6 38 28 PM" src="https://github.com/user-attachments/assets/425fa147-649d-4d64-a351-01e1d1a0fce0" />

### ✅ Curated watchlist recommendations

<img width="2560" height="1440" alt="Screenshot 2025-12-07 at 6 38 37 PM" src="https://github.com/user-attachments/assets/554ab8eb-55a3-4a1b-ac21-20b9d84e1f0e" />
