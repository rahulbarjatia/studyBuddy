from dotenv import dotenv_values
from asyncio import run
import threading
import os

from Chatbot import chatbot
from decision import firstlayerdmm
from Automation import automation
from speechtotext import speechReco

from flask import Flask , jsonify , render_template

app = Flask(__name__)








current_dir = os.path.join(os.path.dirname(__file__), "")

env_vars = dotenv_values(os.path.join(current_dir, ".env"))
groq_api_key = env_vars.get("grokdikey")

funcs = ["explain", "test", "report"]


input_file = os.path.join(current_dir, "Data", "input.txt")

# Background thread for speech recognition
# def query_imp_speech_thread():
#     while True:
#         q = speechReco()
#         if q:
#             with open(input_file, "w", encoding="utf-8") as f:
#                 f.write(q)



@app.route('/')
def index():
    return render_template("index.html")  # Ensure index.html is inside 'templates' folder
    # return render_template("journey.html")  # Ensure index.html is inside 'templates' folder





@app.route('/work/<string:query>')
def main_exe(query):
    # Process query using first-layer decision making
    Decision = firstlayerdmm(query)
    print("\nDecision:", Decision, "\n")

    # Check if any automation-related commands exist
    E = any(i.startswith("explain") for i in Decision)
    T = any(i.startswith("test") for i in Decision)
    R = any(i.startswith("report") for i in Decision)

    if E or T or R:
        for queries in Decision:
            if any(queries.startswith(func) for func in funcs):
                return jsonify({"message": run(automation(Decision))})
            
    else:
        return jsonify(chatbot(Decision))
    return jsonify({"message": chatbot(Decision)})


@app.route('/journey')
def journey():
        return render_template("journey.html")  # Ensure index.html is inside 'templates' folder


@app.route('/get-question', methods=['GET'])
def get_question():
    question = "What is the capital of France?"
    return jsonify({'question': question})



@app.route('/testsh')
def testsh():
    return render_template("testme.html")

if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5000, debug=True)
