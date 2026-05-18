# 🌊 Surfin Website

Complete web frontend + Flask backend for the Surfin emotional drift detection app.

## Folder Structure

```
your-projects/
├── surfin_ml/              ← your existing ML pipeline
│   ├── pipeline.py
│   ├── models/
│   └── ...
└── surfin_website/         ← this folder
    ├── app.py              ← Flask backend
    ├── requirements.txt
    ├── templates/
    │   └── index.html      ← Full PC website
    └── README.md
```

## Setup

### 1. Install web dependencies
```powershell
cd C:\surfin_website
pip install flask flask-cors
```

### 2. Check the path in app.py
Open `app.py` and confirm this line points to your surfin_ml folder:
```python
SURFIN_ML_PATH = os.path.join(os.path.dirname(__file__), '..', 'surfin_ml')
```
Adjust if your folder structure is different.

### 3. Run
```powershell
python app.py
```

Open: **http://localhost:5000**

---

## What Each File Does

### `app.py` — Flask Backend
| Endpoint | Method | What it does |
|---|---|---|
| `/` | GET | Serves the website |
| `/api/login` | POST | Creates a user session |
| `/api/analyze` | POST | Runs text through full ML pipeline |
| `/api/history` | GET | Returns a user's journal history |
| `/api/summary` | GET | Returns baseline summary |
| `/api/chat` | POST | Context-aware chat responses |

### `templates/index.html` — PC Website
- **Left sidebar** — navigation, user info, streak
- **Center** — your phone app as a live mockup
- **Right dashboard** — live ML results, drift score, emotion bars, valence chart

---

## Works Without ML Too

If the ML pipeline fails to load, the backend automatically runs in **DEMO MODE**
— returning realistic mock data based on keyword detection. The website works fully.

---

## PC Layout

```
┌──────────────┬─────────────────────────┬──────────────────┐
│  Sidebar     │   Phone Mockup (live)   │  Live Dashboard  │
│  280px       │   center stage          │  400px           │
│              │                         │                  │
│ · Navigate   │  [your app here]        │ · Drift Score    │
│ · Insights   │                         │ · Emotion Bars   │
│ · Support    │                         │ · Valence Chart  │
│              │                         │ · Entry History  │
│ [User Card]  │                         │ · Crisis Panel   │
└──────────────┴─────────────────────────┴──────────────────┘
```

---

## Demo Flow for Judges

1. Open http://localhost:5000
2. Type your name → click "Ride the wave"
3. Pop a bubble (e.g. Anxious)
4. Set intensity → "See what helps"
5. Click "Write in journal" → type a journal entry → send
6. Watch the **right dashboard update live** with ML results
7. Chat with the bot in the Chat tab
