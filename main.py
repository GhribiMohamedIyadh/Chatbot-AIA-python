from flask import Flask, render_template, request, jsonify
import time
import random
from groq import Groq
from groq import APIError, RateLimitError
from dotenv import load_dotenv
import os

# =========================
# Flask app
# =========================
app = Flask(__name__)

# =========================
# Load API KEY
# =========================
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found")

client = Groq(api_key=api_key)

historique_messages = [
    {
        "role": "system",
        "content": """
        You are an expert PC repair technician.

        Help users fix:
        - Windows problems
        - Drivers
        - Gaming issues
        - Hardware
        - Network problems
        - Performance issues
        - Blue screen
        - Software installation

        Give step-by-step solutions.
        Speak simply.
        """
    }
]

# =========================
# Retry Function
# =========================
def appel_api_avec_retry(max_retries=3):

    for tentative in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=historique_messages,
                temperature=0.7,
                max_tokens=1500
            )

            return response.choices[0].message.content

        except RateLimitError:

            if tentative < max_retries - 1:

                wait_time = 2 ** tentative
                wait_time += random.uniform(0, 0.5)

                time.sleep(wait_time)

            else:
                return "Too many requests"

        except APIError as e:
            return f"API Error: {e}"

        except Exception as e:
            return f"Error: {e}"

# =========================
# Route principale
# =========================
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"reply": "Veuillez entrer un message."})

    historique_messages.append({
        "role": "user",
        "content": user_input
    })

    reply = appel_api_avec_retry()

    historique_messages.append({
        "role": "assistant",
        "content": reply
    })

    return jsonify({"reply": reply})
# =========================
# Run app
# =========================
if __name__ == "__main__":
    app.run(debug=True)