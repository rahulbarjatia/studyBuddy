from groq import Groq
from json import dump, load
from rich import print
from dotenv import dotenv_values
import os

# Define the command keywords that the assistant should recognize
funcs = ["explain", "test", "report"]

# Determine the current directory path
current_dir = os.path.dirname(__file__)

# Load environment variables from the .env file
env_vars = dotenv_values(os.path.join(current_dir, ".env"))
groq_api_key = env_vars.get("grokdikey")

# Initialize the Groq client
client = Groq(api_key=groq_api_key)

# Define the system instructions for the assistant
system = """
You are a decision maker. You decide what type of command is given.

- If it is a command is for making a test "I wanna test my knowledge in matrices , make a test " reply with "test matrices" , if its asking for "make a test on linear algebra" reply with "test linear algebra".
- If it is a command for explaining a topic like "explain me this topic", reply with "explain topic name".
- If it is a command like "what does it do", reply with "explain what does it do".
- If it is a command like "provide a report card for this student", reply with "report student name".

- for example if command is "hi" then reply with "explain hi"
"""

systemchatbot = [{"role": "system", "content": system}]

# Path to the chat log
chatlog_path = os.path.join(current_dir, "Data", "Chatlog.json")

# Ensure chat log file exists
# if not os.path.exists(os.path.dirname(chatlog_path)):
#     os.makedirs(os.path.dirname(chatlog_path))

# if not os.path.exists(chatlog_path):
#     with open(chatlog_path, "w") as fl:
#         dump([], fl, indent=4)

# Ensure chat log file exists and is valid JSON
if not os.path.exists(os.path.dirname(chatlog_path)):
    os.makedirs(os.path.dirname(chatlog_path))

if not os.path.exists(chatlog_path) or os.stat(chatlog_path).st_size == 0:
    with open(chatlog_path, "w") as fl:
        dump([], fl, indent=4)

# Main decision-making function
def firstlayerdmm(prompt: str = "test"):
    # try:
        # Load existing messages
        with open(chatlog_path, "r") as fl:
            messages = load(fl)

        messages.append({"role": "user", "content": prompt})

        # Send the chat to the Groq API using streaming
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

        # Clean the answer
        clean_answer = answer.replace("\n", "")
        split_answer = [i.strip() for i in clean_answer.split(",")]

        # Extract responses matching known function keywords
        responses = [task for task in split_answer if any(task.startswith(f) for f in funcs)]

        # Append assistant response to messages
        messages.append({"role": "assistant", "content": answer})

        # Save updated messages back to the file
        with open(chatlog_path, "w") as fl:
            dump(messages, fl, indent=4)

        return responses if responses else [f"explain {prompt}"]

    # except Exception as e:
    #     print(f"[red]Error:[/red] {e}")
    #     return ["(error occurred)"]

# Run in loop
if __name__ == "__main__":
    while True:
        user_input = input(">> ")
        output = firstlayerdmm(user_input)
        print("[bold green]Output:[/bold green]", output)
