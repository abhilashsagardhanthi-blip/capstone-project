"""
AI Study Pal – Flask Backend
==============================
Run:  python app.py
Open: http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import json, os, random, datetime

app = Flask(__name__)
app.secret_key = "studypal-secret-2024"
CORS(app)

# ─────────────────────────────────────────
#  FILE PATHS  (simple JSON file storage)
# ─────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

TIMETABLE_FILE = os.path.join(DATA_DIR, "timetable.json")
FEEDBACK_FILE  = os.path.join(DATA_DIR, "feedback.json")
SCORES_FILE    = os.path.join(DATA_DIR, "scores.json")


def read_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default


def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────────────────
#  QUIZ QUESTION BANK
# ─────────────────────────────────────────
QUESTIONS = {
    "math": [
        {"q": "What is 12 × 8?",                        "opts": ["96","88","104","112"],   "ans": 0, "emoji": "➕"},
        {"q": "What is 3/4 + 1/4?",                     "opts": ["1","2","0.5","1.5"],     "ans": 0, "emoji": "🔢"},
        {"q": "Area of a square with side 5?",           "opts": ["25","20","10","15"],     "ans": 0, "emoji": "📐"},
        {"q": "What is 144 ÷ 12?",                       "opts": ["12","14","11","13"],     "ans": 0, "emoji": "➗"},
        {"q": "What is 25% of 200?",                     "opts": ["50","25","75","100"],    "ans": 0, "emoji": "💯"},
        {"q": "What is 7²?",                             "opts": ["49","42","56","14"],     "ans": 0, "emoji": "🔢"},
        {"q": "Sides of a hexagon?",                     "opts": ["6","5","7","8"],         "ans": 0, "emoji": "⬡"},
        {"q": "What is 1000 - 347?",                     "opts": ["653","663","643","673"], "ans": 0, "emoji": "➖"},
        {"q": "Next prime after 7?",                     "opts": ["11","9","10","13"],      "ans": 0, "emoji": "🔢"},
        {"q": "What is 15% of 60?",                      "opts": ["9","6","12","15"],       "ans": 0, "emoji": "💯"},
    ],
    "english": [
        {"q": "Noun in: 'The cat sat on the mat'?",      "opts": ["cat","sat","the","on"],          "ans": 0, "emoji": "📚"},
        {"q": "Synonym of 'happy'?",                     "opts": ["joyful","sad","angry","tired"],   "ans": 0, "emoji": "😊"},
        {"q": "Plural of 'child'?",                      "opts": ["children","childs","childen","child"], "ans": 0, "emoji": "👦"},
        {"q": "Correct sentence?",                        "opts": ["She runs fast","She run fast","She running fast","She runned fast"], "ans": 0, "emoji": "✏️"},
        {"q": "What does prefix 'un-' mean?",            "opts": ["not","again","before","after"],  "ans": 0, "emoji": "📝"},
        {"q": "Adjective in: 'The big red ball'?",       "opts": ["big","ball","the","is"],         "ans": 0, "emoji": "📚"},
        {"q": "Vowels in 'beautiful'?",                  "opts": ["5","4","6","3"],                 "ans": 0, "emoji": "🔤"},
        {"q": "Antonym of 'ancient'?",                   "opts": ["modern","old","historic","past"],"ans": 0, "emoji": "✏️"},
        {"q": "Punctuation ending a question?",          "opts": ["?","!",".","..."],               "ans": 0, "emoji": "❓"},
        {"q": "Verb in: 'The dog barks loudly'?",        "opts": ["barks","dog","loudly","the"],    "ans": 0, "emoji": "📚"},
    ],
    "science": [
        {"q": "Gas plants absorb from air?",             "opts": ["Carbon dioxide","Oxygen","Nitrogen","Hydrogen"], "ans": 0, "emoji": "🌿"},
        {"q": "Boiling point of water?",                 "opts": ["100°C","90°C","80°C","110°C"],  "ans": 0, "emoji": "💧"},
        {"q": "Planet closest to the Sun?",              "opts": ["Mercury","Venus","Earth","Mars"], "ans": 0, "emoji": "☀️"},
        {"q": "Powerhouse of the cell?",                 "opts": ["Mitochondria","Nucleus","Ribosome","Cell wall"], "ans": 0, "emoji": "🔬"},
        {"q": "Force keeping us on ground?",             "opts": ["Gravity","Magnetism","Friction","Tension"], "ans": 0, "emoji": "🍎"},
        {"q": "Colours in a rainbow?",                   "opts": ["7","6","8","5"],                 "ans": 0, "emoji": "🌈"},
        {"q": "Bones in an adult body?",                 "opts": ["206","208","200","212"],         "ans": 0, "emoji": "🦴"},
        {"q": "What is H₂O?",                            "opts": ["Water","Salt","Sugar","Acid"],   "ans": 0, "emoji": "💧"},
        {"q": "Organ that pumps blood?",                 "opts": ["Heart","Lungs","Brain","Liver"], "ans": 0, "emoji": "❤️"},
        {"q": "Earth's orbit around Sun takes?",         "opts": ["365 days","300 days","400 days","30 days"], "ans": 0, "emoji": "🌍"},
    ],
    "history": [
        {"q": "Who built the Great Wall of China?",      "opts": ["Emperor Qin Shi Huang","Genghis Khan","Kublai Khan","Marco Polo"], "ans": 0, "emoji": "🏯"},
        {"q": "Writer of Declaration of Independence?",  "opts": ["Thomas Jefferson","George Washington","Abraham Lincoln","Benjamin Franklin"], "ans": 0, "emoji": "🗽"},
        {"q": "World War II ended in?",                  "opts": ["1945","1939","1942","1950"],     "ans": 0, "emoji": "⚔️"},
        {"q": "First President of USA?",                 "opts": ["George Washington","John Adams","Thomas Jefferson","James Madison"], "ans": 0, "emoji": "🇺🇸"},
        {"q": "Mahatma Gandhi fought for?",              "opts": ["India's independence","War victories","Monarchy","Colonisation"], "ans": 0, "emoji": "✌️"},
        {"q": "Ancient Olympics held in?",               "opts": ["Greece","Rome","Egypt","Persia"], "ans": 0, "emoji": "🏅"},
        {"q": "First woman Pharaoh of Egypt?",           "opts": ["Hatshepsut","Cleopatra","Nefertiti","Isis"], "ans": 0, "emoji": "🐍"},
        {"q": "Columbus reached America in?",            "opts": ["1492","1500","1488","1510"],     "ans": 0, "emoji": "⛵"},
        {"q": "Gandhi was born in?",                     "opts": ["Porbandar","Mumbai","Delhi","Kolkata"], "ans": 0, "emoji": "🌏"},
        {"q": "Civilization that built Pyramids?",       "opts": ["Egyptian","Greek","Roman","Persian"], "ans": 0, "emoji": "🔺"},
    ],
    "social": [
        {"q": "How many continents on Earth?",           "opts": ["7","6","5","8"],                 "ans": 0, "emoji": "🌍"},
        {"q": "Capital of India?",                       "opts": ["New Delhi","Mumbai","Chennai","Kolkata"], "ans": 0, "emoji": "🇮🇳"},
        {"q": "Largest ocean on Earth?",                 "opts": ["Pacific","Atlantic","Indian","Arctic"], "ans": 0, "emoji": "🌊"},
        {"q": "Largest country by area?",                "opts": ["Russia","Canada","USA","China"],  "ans": 0, "emoji": "🗺️"},
        {"q": "Longest river in the world?",             "opts": ["Nile","Amazon","Yangtze","Mississippi"], "ans": 0, "emoji": "🏞️"},
        {"q": "Country with most population?",           "opts": ["India","China","USA","Indonesia"],"ans": 0, "emoji": "👥"},
        {"q": "Smallest country in the world?",          "opts": ["Vatican City","Monaco","San Marino","Liechtenstein"], "ans": 0, "emoji": "⛪"},
        {"q": "Mount Everest is in?",                    "opts": ["Nepal","India","China","Bhutan"], "ans": 0, "emoji": "⛰️"},
        {"q": "Amazon Rainforest famous for?",           "opts": ["Biodiversity","Deserts","Ice caps","Volcanoes"], "ans": 0, "emoji": "🌿"},
        {"q": "Largest desert in the world?",            "opts": ["Sahara","Gobi","Arctic","Arabian"],"ans": 0, "emoji": "🏜️"},
    ],
}

# ─────────────────────────────────────────
#  AI FEEDBACK MESSAGES
# ─────────────────────────────────────────
AI_FEEDBACK = {
    "Great": {
        "easy":   ["You're a superstar! 🌟 Easy stuff is no match for you!",
                   "Amazing! You breezed through today! Keep shining! ✨"],
        "medium": ["Brilliant work! 🎉 You tackled it like a champion!",
                   "Great job! You're really getting it! 🚀"],
        "hard":   ["WOW! You found it hard but kept going — that's a HERO! 🦸",
                   "Incredible! Pushing through tough stuff makes you stronger! 💪"],
    },
    "Good": {
        "easy":   ["Good going! 👍 You're on the right track, keep it up!",
                   "Nice work! Easy days build great confidence! 😊"],
        "medium": ["Good effort! 🙌 A little more practice and you'll nail it!",
                   "Well done! Keep studying and you'll be a pro! 📚"],
        "hard":   ["Good for you for trying something hard! 🏅 Hard work pays off!",
                   "Keep at it! Hard topics become easy with practice! 💡"],
    },
    "Okay": {
        "easy":   ["That's okay! 😊 Every day is a fresh start!",
                   "Even on okay days, learning adds up! 🌱"],
        "medium": ["Okay days happen! Try reviewing the topic tomorrow. 📖",
                   "You showed up and that matters! Rest and try again! 🌙"],
        "hard":   ["Hard days with tough topics — you're brave for trying! 🦁",
                   "Even the smartest people find some things hard! 🧠"],
    },
    "Tired": {
        "easy":   ["You studied even when tired — real dedication! 🌟",
                   "Rest up! Your brain needs sleep to remember things! 💤"],
        "medium": ["Take a short break and come back refreshed! ☕",
                   "Tired but trying! You deserve a treat after this! 🍪"],
        "hard":   ["Tackling hard stuff while tired — you're amazing! 😮",
                   "Rest is important! Come back with fresh eyes tomorrow! 🌅"],
    },
    "Confused": {
        "easy":   ["That's okay to feel confused! Ask your teacher for help! 🙋",
                   "Confusion means your brain is working hard! 🤔"],
        "medium": ["Feeling confused is the first step to understanding! 💡",
                   "Don't give up! Watch a video or read again — it'll click! 🎯"],
        "hard":   ["Hard topics CAN be confusing! Break it into small pieces! 🧩",
                   "You're not alone! Everyone gets confused. Ask for help! 🤝"],
    },
}

STUDY_TIPS = {
    "math":    ["Practice sums daily for 15 minutes 📐",
                "Use graph paper to draw shapes and visualise problems 📊",
                "Check your work by reversing the operation ✅"],
    "english": ["Read a book for 20 minutes every day 📖",
                "Write 5 new words in a vocabulary notebook ✏️",
                "Practice speaking sentences aloud to build fluency 🗣️"],
    "science": ["Observe nature around you and ask 'Why?' 🔬",
                "Draw diagrams of body parts or plant cells 🌿",
                "Watch short science videos to visualise concepts 🎥"],
    "history": ["Create a timeline of important events on paper 📜",
                "Tell historical stories to a friend or family member 🗣️",
                "Use maps to trace where history happened 🗺️"],
    "social":  ["Look at a world map for 5 minutes daily 🌍",
                "Learn the capital of one new country each day 🏙️",
                "Watch news for kids to stay aware of the world 📰"],
}


# ─────────────────────────────────────────
#  ROUTES – PAGES
# ─────────────────────────────────────────

@app.route("/")
def home():
    """Serve the main HTML page."""
    return render_template("index.html")


# ─────────────────────────────────────────
#  API – QUIZ
# ─────────────────────────────────────────

@app.route("/api/quiz/<subject>", methods=["GET"])
def get_quiz(subject):
    """Return shuffled quiz questions for the given subject."""
    subject = subject.lower()
    if subject not in QUESTIONS:
        return jsonify({"error": "Subject not found. Choose from: math, english, science, history, social"}), 404

    questions = QUESTIONS[subject].copy()
    random.shuffle(questions)
    # Strip the answer before sending to client
    safe_qs = [{"q": q["q"], "opts": q["opts"], "emoji": q["emoji"]} for q in questions]
    # Store answer key in server session so we can validate
    session[f"quiz_{subject}"] = [q["ans"] for q in questions]
    return jsonify({"subject": subject, "questions": safe_qs, "total": len(safe_qs)})


@app.route("/api/quiz/<subject>/answer", methods=["POST"])
def check_answer(subject):
    """
    Check a single answer.
    Body: { "q_index": 0, "chosen": 2 }
    """
    subject = subject.lower()
    data = request.get_json()
    q_index = data.get("q_index", 0)
    chosen  = data.get("chosen", -1)

    answer_key = session.get(f"quiz_{subject}")
    if answer_key is None:
        return jsonify({"error": "Quiz session not found. Call /api/quiz/<subject> first."}), 400

    correct = answer_key[q_index]
    is_correct = (chosen == correct)
    correct_text = QUESTIONS[subject][q_index]["opts"][correct]

    return jsonify({
        "is_correct": is_correct,
        "correct_index": correct,
        "correct_text": correct_text,
        "message": "✅ Correct! Great job!" if is_correct else f"❌ Oops! The answer was: {correct_text}"
    })


@app.route("/api/quiz/<subject>/submit", methods=["POST"])
def submit_quiz(subject):
    """
    Submit entire quiz result and save score.
    Body: { "score": 7, "total": 10 }
    """
    subject = subject.lower()
    data  = request.get_json()
    score = data.get("score", 0)
    total = data.get("total", 10)
    pct   = round((score / total) * 100)

    scores = read_json(SCORES_FILE, {})
    if subject not in scores:
        scores[subject] = {"best": 0, "attempts": 0, "last": 0}
    scores[subject]["attempts"] += 1
    scores[subject]["last"]      = pct
    scores[subject]["best"]      = max(scores[subject]["best"], pct)
    write_json(SCORES_FILE, scores)

    # Determine star rating
    if pct == 100: stars, msg = 3, "🎉 PERFECT SCORE! You are a genius!"
    elif pct >= 80: stars, msg = 3, "🌟 Wonderful! You did amazing!"
    elif pct >= 60: stars, msg = 2, "👍 Good job! A little more practice!"
    elif pct >= 40: stars, msg = 1, "😊 Keep trying — you got this!"
    else:           stars, msg = 1, "💪 Don't give up! Practice makes perfect!"

    tips = random.choice(STUDY_TIPS.get(subject, ["Keep studying! 📚"]))

    return jsonify({
        "score": score, "total": total, "percentage": pct,
        "stars": stars, "message": msg, "tip": tips
    })


# ─────────────────────────────────────────
#  API – TIMETABLE
# ─────────────────────────────────────────

@app.route("/api/timetable", methods=["GET"])
def get_timetable():
    """Return saved timetable."""
    return jsonify(read_json(TIMETABLE_FILE, {}))


@app.route("/api/timetable", methods=["POST"])
def save_timetable():
    """
    Save timetable.
    Body: { "Monday-8:00 AM": "Maths", "Monday-9:00 AM": "English", ... }
    """
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid data – send a JSON object"}), 400
    write_json(TIMETABLE_FILE, data)
    return jsonify({"success": True, "message": "✅ Timetable saved!", "slots": len(data)})


@app.route("/api/timetable", methods=["DELETE"])
def clear_timetable():
    """Clear the entire timetable."""
    write_json(TIMETABLE_FILE, {})
    return jsonify({"success": True, "message": "Timetable cleared."})


@app.route("/api/timetable/summary", methods=["GET"])
def timetable_summary():
    """Return a count of hours per subject."""
    tt = read_json(TIMETABLE_FILE, {})
    summary = {}
    for subject in tt.values():
        summary[subject] = summary.get(subject, 0) + 1
    return jsonify({"summary": summary, "total_slots": len(tt)})


# ─────────────────────────────────────────
#  API – FEEDBACK
# ─────────────────────────────────────────

@app.route("/api/feedback", methods=["POST"])
def post_feedback():
    """
    Generate AI feedback and save record.
    Body: {
        "subject": "Maths",
        "difficulty": 3,       (1–5)
        "mood": "Good",
        "notes": "I learnt fractions today"
    }
    """
    data = request.get_json()
    subject    = data.get("subject", "")
    difficulty = int(data.get("difficulty", 3))
    mood       = data.get("mood", "Good")
    notes      = data.get("notes", "")

    # Map difficulty to label
    if difficulty <= 2:   diff_label = "easy"
    elif difficulty == 3: diff_label = "medium"
    else:                 diff_label = "hard"

    # Pick an AI message
    mood_pool = AI_FEEDBACK.get(mood, AI_FEEDBACK["Good"])
    ai_msg    = random.choice(mood_pool.get(diff_label, ["Great work! Keep it up! 🌟"]))

    # Personalise with subject tip
    subj_key = subject.lower()
    tip = random.choice(STUDY_TIPS.get(subj_key, ["Keep studying every day! 📚"]))

    # Save to feedback history
    history = read_json(FEEDBACK_FILE, [])
    entry = {
        "subject":    subject,
        "difficulty": difficulty,
        "mood":       mood,
        "notes":      notes,
        "ai_message": ai_msg,
        "tip":        tip,
        "timestamp":  datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    history.insert(0, entry)
    write_json(FEEDBACK_FILE, history[:50])   # keep latest 50

    return jsonify({
        "success":    True,
        "ai_message": ai_msg,
        "tip":        tip,
        "entry":      entry,
    })


@app.route("/api/feedback", methods=["GET"])
def get_feedback():
    """Return feedback history (latest 20)."""
    history = read_json(FEEDBACK_FILE, [])
    limit   = int(request.args.get("limit", 20))
    return jsonify({"feedback": history[:limit], "total": len(history)})


@app.route("/api/feedback", methods=["DELETE"])
def clear_feedback():
    """Clear all feedback history."""
    write_json(FEEDBACK_FILE, [])
    return jsonify({"success": True, "message": "Feedback history cleared."})


# ─────────────────────────────────────────
#  API – SCORES / PROGRESS
# ─────────────────────────────────────────

@app.route("/api/scores", methods=["GET"])
def get_scores():
    """Return per-subject score summary + badges earned."""
    scores = read_json(SCORES_FILE, {})

    badges = []
    subjects = ["math", "english", "science", "history", "social"]

    for subj in subjects:
        info = scores.get(subj, {})
        if info.get("best", 0) >= 80:
            labels = {"math": "Math Pro 🧠", "english": "Bookworm 📚",
                      "science": "Scientist 🔬", "history": "Historian 🏛️", "social": "Explorer 🌍"}
            badges.append(labels[subj])

    if any(scores.get(s, {}).get("best", 0) == 100 for s in subjects):
        badges.append("100% Club 🏆")
    if all(scores.get(s, {}).get("attempts", 0) >= 1 for s in subjects):
        badges.append("All Subjects 🌟")
    if any(scores.get(s, {}).get("attempts", 0) >= 5 for s in subjects):
        badges.append("Quiz Master 🔥")

    return jsonify({"scores": scores, "badges": badges})


@app.route("/api/scores", methods=["DELETE"])
def reset_scores():
    """Reset all scores."""
    write_json(SCORES_FILE, {})
    return jsonify({"success": True, "message": "Scores reset."})


# ─────────────────────────────────────────
#  API – STUDY TIPS
# ─────────────────────────────────────────

@app.route("/api/tips/<subject>", methods=["GET"])
def get_tips(subject):
    """Return all study tips for a subject."""
    subject = subject.lower()
    tips = STUDY_TIPS.get(subject)
    if tips is None:
        return jsonify({"error": "Subject not found."}), 404
    return jsonify({"subject": subject, "tips": tips, "random_tip": random.choice(tips)})


# ─────────────────────────────────────────
#  HEALTH CHECK
# ─────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "app": "AI Study Pal",
        "version": "1.0",
        "subjects": list(QUESTIONS.keys()),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })


# ─────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  [*] AI Study Pal - Flask Backend")
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
