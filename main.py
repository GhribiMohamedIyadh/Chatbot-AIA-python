import time
import random
from groq import Groq
from groq import APIError, RateLimitError
from dotenv import load_dotenv
import os

# تحميل API KEY من .env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

# إنشاء client
client = Groq(api_key=api_key)


# =========================
# 🔁 Function with Retry
# =========================
def appel_api_avec_retry(prompt, max_retries=3):

    for tentative in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=historique_messages,
                temperature=0.7,
                max_tokens=300,
                stream=False
            )

            return response.choices[0].message.content

        # =========================
        # 🚨 Rate Limit Error
        # =========================
        except RateLimitError:
            if tentative < max_retries - 1:
                wait_time = 2 ** tentative  # backoff exponentiel
                wait_time += random.uniform(0, 0.5)  # jitter صغير

                print(f"⚠️ Rate limit reached, waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                raise Exception("❌ Too many requests, try again later")

        # =========================
        # ❌ API Error
        # =========================
        except APIError as e:
            print("❌ API Error:", e)
            raise

        # =========================
        # ❌ Other errors
        # =========================
        except Exception as e:
            print("❌ Unexpected error:", e)
            raise

def ajouter_message(role, content):
    historique_messages.append({
        "role": role,
        "content": content
    })

def afficher_historique():
    for msg in historique_messages:
        print(f"{msg['role']}: {msg['content']}")

# =========================
# ▶️ Chat loop
# =========================
historique_messages = []
if __name__ == "__main__":
    print("🤖 Chatbot démarré !")
    print("Tapez 'quitter' pour sortir\n")

    while True:
        user_input = input("👤 You: ")
        user_input = user_input.strip()

        if user_input.lower() == "exit" or user_input.lower() == "quitter" or user_input.lower() == "bye":
            print("Au revoir ! 👋")
            break

        ajouter_message("user", user_input)
        reply = appel_api_avec_retry(user_input, max_retries=3)
        ajouter_message("assistant", reply)

        print("🤖 AI:", reply)
