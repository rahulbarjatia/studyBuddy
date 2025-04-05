from groq import Groq
from json import dump, load
import json
from dotenv import dotenv_values
import sqlite3
import os

# === Paths ===
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "Data", "test_results.db")
chatlog_path = os.path.join(current_dir, "Data", "conversation.json")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# === Load API Key ===
env_vars = dotenv_values(os.path.join(current_dir, ".env"))
groq_api_key = env_vars.get("grokdikey")

# === Groq Client ===
client = Groq(api_key=groq_api_key)

# === System Prompt ===
systemchatbot = [
    {
        "role": "system",
        "content": (
            "You are a smart and helpful study assistant. Use the student’s previous test results if its required "
            "guide and assist students to learn more effectively. Answer queries clearly and supportively."
        )
    }
]

# === Fetch DB Results as String ===
def get_results_as_string():
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT question, options, correct_answer, user_answer, is_correct FROM mcq_results")
            rows = cursor.fetchall()

            if not rows:
                return "No test results found."

            result_lines = []
            for idx, row in enumerate(rows, start=1):
                question, options, correct, user, correct_flag = row
                status = "✅" if correct_flag else f"❌ (Correct: {correct})"
                result_lines.append(
                    f"Q{idx}: {question}\n{options.strip()}\nYour Answer: {user} {status}\n"
                )

            return "\n".join(result_lines)
    except sqlite3.Error as e:
        return "Error reading test results."

# === Chatbot Function ===
def chatbot(query):
    # Load previous conversation
    try:
        with open(chatlog_path, "r") as f:
            messages = load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        messages = []

    # Keep last N messages to avoid overload
    # MAX_HISTORY = 10
    # messages = messages[-MAX_HISTORY:]

    # Combine test data with query
    combined_prompt = (
        f"The data of previous tests is below. Use it if needed:\n\n"
        f"{get_results_as_string()}\n\nUser query: {query}"
    )
    messages.append({"role": "user", "content": combined_prompt})

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=systemchatbot + messages,
            temperature=0.7,
            top_p=1,
            stream=True
        )
    except Exception as e:
        return f"Chatbot error: {str(e)}"

    # Read stream response
    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    messages.append({"role": "assistant", "content": answer})

    # Save updated chat history
    with open(chatlog_path, "w") as f:
        dump(messages, f, indent=4)

    return answer

# === Main Loop ===
if __name__ == "__main__":
    while True:
        user_input = input(">> ")
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        print(chatbot(user_input))
