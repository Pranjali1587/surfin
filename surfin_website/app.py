"""
Surfin Web Backend — Flask (Persistent Version)
Stores users and journals in JSON files
"""

import os, sys, json, random
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# ─────────────────────────────────────────────
# ML PIPELINE
# ─────────────────────────────────────────────

SURFIN_ML_PATH = os.path.join(os.path.dirname(__file__), '..', 'surfin_ml')
sys.path.insert(0, os.path.abspath(SURFIN_ML_PATH))

os.environ['USE_TF'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    from pipeline import SurfinPipeline
    pipeline = SurfinPipeline()
    ML_AVAILABLE = True
    print("✅ Surfin ML pipeline loaded")
except Exception as e:
    pipeline = None
    ML_AVAILABLE = False
    print(f"⚠️ ML not loaded: {e} — DEMO MODE")


# ─────────────────────────────────────────────
# FLASK
# ─────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = "surfin-secret"
CORS(app)


# ─────────────────────────────────────────────
# JSON STORAGE
# ─────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(___file__), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
JOURNALS_FILE = os.path.join(DATA_DIR, "journals.json")

os.makedirs(DATA_DIR, exist_ok=True)


def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# Load saved data on startup
user_sessions = load_json(USERS_FILE)
user_journals = load_json(JOURNALS_FILE)


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("mobile.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")


# ─────────────────────────────────────────────
# LOGIN (REUSES EXISTING USER)
# ─────────────────────────────────────────────

@app.route("/api/login", methods=["POST"])
def login():

    global user_sessions

    data = request.get_json()
    name = (data.get("name") or "user").strip().lower()

    # Check if user already exists
    for uid, info in user_sessions.items():
        if info["name"].lower() == name:
            return jsonify({
                "success": True,
                "user_id": uid,
                "name": info["name"]
            })

    # Create new user
    user_id = f"user_{name}"

    user_sessions[user_id] = {
        "name": name,
        "created_at": datetime.now().isoformat()
    }

    save_json(USERS_FILE, user_sessions)

    return jsonify({
        "success": True,
        "user_id": user_id,
        "name": name
    })


# ─────────────────────────────────────────────
# ANALYZE JOURNAL ENTRY
# ─────────────────────────────────────────────

@app.route("/api/analyze", methods=["POST"])
def analyze():

    global user_journals

    data = request.get_json()

    text = (data.get("text") or "").strip()
    user_id = data.get("user_id", "demo_user")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Run ML pipeline if available
    if ML_AVAILABLE and pipeline:

        try:
            r = pipeline.process_entry(user_id=user_id, text=text)

            result = {
                "user_id": r.user_id,
                "entry_number": r.entry_number,
                "top_emotion": r.top_emotion,
                "top_score": r.top_score,
                "valence": r.valence,
                "negative_ratio": r.negative_ratio,
                "all_scores": r.all_scores,
                "drift_level": r.drift_level,
                "drift_score": r.drift_score,
                "drift_message": r.drift_message,
                "drift_action": r.drift_action,
                "signals_triggered": r.signals_triggered,
                "risk_level": r.risk_level,
                "risk_score": r.risk_score,
                "crisis_message": r.crisis_message,
                "sos_trigger": r.sos_trigger,
                "resources": r.resources,
                "baseline_stable": r.baseline_stable,
                "baseline_valence_mean": r.baseline_valence_mean,
                "n_entries": r.n_entries,
                "timestamp": datetime.now().isoformat(),
                "text": text,
            }

        except Exception as e:
            print("Pipeline error:", e)
            result = mock_result(text, user_id)

    else:
        result = mock_result(text, user_id)

    # Save entry
    user_journals.setdefault(user_id, []).append(result)

    save_json(JOURNALS_FILE, user_journals)

    return jsonify(result)


# ─────────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────────

@app.route("/api/history", methods=["GET"])
def history():

    user_id = request.args.get("user_id", "demo_user")

    journals = load_json(JOURNALS_FILE)
    entries = journals.get(user_id, [])

    return jsonify({
        "user_id": user_id,
        "entries": entries,
        "count": len(entries)
    })

@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify({
        "users": list(user_sessions.keys()),
        "count": len(user_sessions)
    })
# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────

@app.route("/api/summary", methods=["GET"])
def summary():

    user_id = request.args.get("user_id", "demo_user")

    entries = user_journals.get(user_id, [])

    if not entries:
        return jsonify({"message": "No entries yet"})

    valences = [e.get("valence", 0) for e in entries]

    return jsonify({
        "user_id": user_id,
        "entries_logged": len(entries),
        "avg_valence": round(sum(valences) / len(valences), 3),
        "dominant_emotion": entries[-1].get("top_emotion", "neutral"),
        "baseline_stable": len(entries) >= 7,
    })

# ─────────────────────────────────────────────
# ALL USERS (for admin dashboard)
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# CHAT
# ─────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json()
    message = (data.get("message") or "").lower()

    crisis_words = [
        "suicide",
        "harm",
        "hurt",
        "kill myself",
        "end it",
        "want to die",
        "hurt myself"
    ]

    if any(w in message for w in crisis_words):

        return jsonify({
            "response": "Please reach out now — iCall India: 9152987821. You are not alone.",
            "sos_trigger": True
        })

    responses = [
        "I'm here with you.",
        "Tell me more about what's going on.",
        "That sounds heavy. You're not carrying it alone.",
        "What might help even a little today?"
    ]

    return jsonify({
        "response": random.choice(responses),
        "sos_trigger": False
    })


# ─────────────────────────────────────────────
# MOCK RESULT (DEMO MODE)
# ─────────────────────────────────────────────

def mock_result(text, user_id):

    valence = round(random.uniform(-0.8, 0.8), 3)

    emotion = random.choice(
        ["joy", "sadness", "fear", "anger", "neutral"]
    )

    n = len(user_journals.get(user_id, [])) + 1

    return {
        "user_id": user_id,
        "entry_number": n,
        "top_emotion": emotion,
        "top_score": round(random.uniform(0.6, 0.95), 3),
        "valence": valence,
        "negative_ratio": abs(valence),
        "all_scores": {},
        "drift_level": "NORMAL",
        "drift_score": 0.1,
        "risk_level": "SAFE",
        "timestamp": datetime.now().isoformat(),
        "text": text,
        "demo_mode": True
    }


# ─────────────────────────────────────────────
# RUN SERVER
# ─────────────────────────────────────────────

if __name__ == "__main__":

    print("\n🌊 Surfin Web Server")
    print(f"ML pipeline: {'LIVE' if ML_AVAILABLE else 'DEMO MODE'}")
    print("Open http://localhost:5000\n")

    app.run(debug=True, port=5000, host="0.0.0.0")