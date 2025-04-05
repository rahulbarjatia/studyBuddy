from dotenv import dotenv_values
import asyncio
import os
from Chatbot import chatbot
from flask import Flask , render_template , redirect , url_for
# from testgen import test_mak
# Load environment variables
current_dir = os.path.join(os.path.dirname(__file__), "")
env_vars = dotenv_values(os.path.join(current_dir, ".env"))
groqapikey = env_vars.get("grokdikey")

app = Flask(__name__)
# Function handlers
def explain(query):
    return chatbot(query)
    

def test(query):
    import sqlite3
    import datetime
    import os
    import re
    from json import dump, load
    from rich import print
    from dotenv import dotenv_values
    from groq import Groq
    from Chatbot import chatbot
    # ------------------------------------------------- SETUP -----------------------

    # Keywords for intent detection (currently not used in logic, but can be extended)
    funcs = ["explain", "test", "report"]

    # Path setup
    current_dir = os.path.dirname(__file__)

    db_path = os.path.join(current_dir, "Data", "test_results.db")

    # Load environment variables
    env_vars = dotenv_values(os.path.join(current_dir, ".env"))
    groq_api_key = env_vars.get("grokdikey")

    # Initialize Groq client
    client = Groq(api_key=groq_api_key)


    # --------------------------------------------- SYSTEM PROMPT -----------------------

    system_prompt = """
    You are a test maker. You make formal test paper for the given topic.

    Points:
    - Total number of questions: 5
    - Provide multiple choice options for each question (A, B, C, D)
    - Also provide the correct answer clearly
    - All questions must be strictly related to the topic given in the command
    """

    systemchatbot = [{"role": "system", "content": system_prompt}]

    # -------------------------------------- FUNCTION: Generate Questions -----------------------

    def ques_gen(prompt: str = "test"):
        try:

            messages = []

            messages.append({"role": "user", "content": prompt})

            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=systemchatbot + messages,
                temperature=0.7,
                top_p=1,
                stream=True,
            )

            answer = ""
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content

            messages.append({"role": "assistant", "content": answer})



            return answer

        except Exception as e:
            print(f"[red]Error in ques_gen:[/red] {e}")
            return "Error generating questions."

    # -------------------------------- FUNCTION: Initialize Database -----------------------

    def init_db():
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mcq_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT,
                    options TEXT,
                    correct_answer TEXT,
                    user_answer TEXT,
                    is_correct INTEGER,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    # --------------------------------------- FUNCTION: Parse MCQs -----------------------

    def parse_mcqs(raw_text):
        pattern = re.compile(
            r"\*\*Question\s*\d+\*\*\s*(.*?)\n+"
            r"A\)\s*(.*?)\n"
            r"B\)\s*(.*?)\n"
            r"C\)\s*(.*?)\n"
            r"D\)\s*(.*?)\n"
            r"Correct Option:\s*([A-D])\).*?",
            re.DOTALL
        )

        matches = pattern.finditer(raw_text)
        questions = []

        for match in matches:
            question = match.group(1).strip()
            options = {
                "A": match.group(2).strip(),
                "B": match.group(3).strip(),
                "C": match.group(4).strip(),
                "D": match.group(5).strip(),
            }
            correct_answer = match.group(6).strip().upper()

            # Format options as multi-line string for display
            formatted_options = "\n".join([f"{key}) {value}" for key, value in options.items()])

            questions.append({
                "question": question,
                "options": formatted_options,
                "correct_answer": correct_answer
            })

        return questions


    # -------------------------------------- FUNCTION: Conduct Test -----------------------

    def test_mak(topic):

        init_db()

        print(f"\n[bold cyan]Generating MCQs on topic:[/bold cyan] {topic}")
        prompt = f"Create 5 multiple choice questions on the topic '{topic}'. Format: Question, Options (A, B, C, D), Correct Option (e.g., A)"
        generated = ques_gen(prompt)

        # print("\n[bold green]Generated Content:[/bold green]\n", generated)

        questions = parse_mcqs(generated)
        if not questions:
            print("[red]❌ No questions could be parsed. Please try again.[/red]")
            return

        score = 0
        for q in questions:
            # print(f"\n[bold yellow]Q:[/bold yellow] {q['question']}")
            print(f"\n\n\n\n\n\n\n\n\n\n\n\n\n[bold yellow]Q:[/bold yellow] {q['question']}")
            print(q['options'])

            user_ans = input("Your Answer (A/B/C/D): ").strip().upper()
            is_correct = int(user_ans == q['correct_answer'])

            # Save to DB
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO mcq_results (question, options, correct_answer, user_answer, is_correct, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    q['question'],
                    q['options'],
                    q['correct_answer'],
                    user_ans,
                    is_correct,
                    datetime.datetime.now().isoformat()
                ))
                conn.commit()

            if is_correct:
                print("[green]✅ Correct![/green]")
                score += 1
            else:
                print(f"[red]❌ Wrong. Correct Answer: {q['correct_answer']}[/red]")

        print(f"\n[bold blue]Test Completed. Your Score: {score}/{len(questions)}[/bold blue]")

    # ----------------------------- PRINT DATASET DATA -----------------------


    def print_all_results():
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mcq_results")
            rows = cursor.fetchall()

            if not rows:
                print("No records found in the database.")
                return

            print("\n[📊] Stored MCQ Test Results:\n")
            # for row in rows:
            #     print(f"ID: {row[0]}")
            #     print(f"Question: {row[1]}")
            #     print(f"Options:\n{row[2]}")
            #     print(f"Correct Answer: {row[3]}")
            #     print(f"User Answer: {row[4]}")
            #     print(f"Correct?: {'✅' if row[5] else '❌'}")
            #     print(f"Timestamp: {row[6]}")
            #     print("-" * 60)
            return(rows)

    def get_results_as_string():
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

    # ----------------------- MAIN ENTRY -----------------------

    test_mak(query)

    return get_results_as_string()


   


def report(query):
    return f"Report generated for: {query}"
    


# Async helper to execute commands
async def translateandexec(commands: list[str]):
    func = []

    for command in commands:
        if command.startswith("explain"):
            fun = asyncio.to_thread(explain, command.removeprefix("explain "))
            func.append(fun)

        elif command.startswith("test"):
            fun = asyncio.to_thread(test, command.removeprefix("test "))
            func.append(fun)


        elif command.startswith("report"):
            fun = asyncio.to_thread(report, command.removeprefix("report "))
            func.append(fun)

        else:
            print(f"No function found for {command}")

    results = await asyncio.gather(*func)
    return results


# Main automation function
async def automation(commands: list[str]):
    results = await translateandexec(commands)
    return results
