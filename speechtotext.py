from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
# import mtranslate as mt
current_dir = os.path.dirname(__file__) + "//"

link = rf"{current_dir}/Data/Voice.html"

env_vars = dotenv_values(rf"{current_dir}.env")



HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>

    <script>
        const output = document.getElementById('output');
        let recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        
        recognition.lang = 'en-IN';
        recognition.continuous = true;
        
        recognition.onresult = (event) => {
            const transcript = event.results[event.results.length - 1][0].transcript;
            output.textContent += transcript;
        };

        recognition.onend = () => {
            if (recognition && recognition.continuous) recognition.start(); // Restart if still active
        };

        function startRecognition() {
            if (!recognition) return; // Ensure recognition is initialized
            recognition.start();
        }

        function stopRecognition() {
            if (recognition) {
                recognition.onend = null; // Prevent auto-restart
                recognition.stop();
            }
            output.textContent = ""; // Clear output only if needed
        }
    </script>
</body>
</html>'''





with open(rf"{current_dir}Data\Voice.html" , "w")as fl:
        fl.write(HtmlCode)


chrome_options = Options()
# user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
# chrome_options.add_argument(f'user-agent = {user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--window-position=-10000,0")  # Move the window off-screen
chrome_options.add_argument("--headless=new")


service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service,options=chrome_options)

tempDirpath = rf"{current_dir}/Frontend/Files"

def setassistantstatus(status):
    with open(rf"{tempDirpath}/Status.data" , "w" , encoding="utf-8") as fl:
            fl.write(status)

# def querymodifier(query):
#         new_query = ""
#         new_query = query.lower().strip()
#         query_words = new_query.split()
#         question_w = ["how","what" , "who" , "where", "when" , "why", "which" , "whose", "whom" , "can you", "what's" , "where's", "how's" , "can you"]

#         if any(word + " " in new_query for word in question_w):
#             if query_words[-1][-1] in ['.' , '?' , '!' ]:
#                 new_query = new_query[:-1] + "?"
#             else:
#                 new_query += "."

#         else:
#             if query_words[-1][-1] in ['.' , '?' , '!' ]:
#                 new_query = new_query[:-1] + "."
#             else:
#                 new_query += "."

#         return new_query.capitalize()

# def UniversalTranslator(text):
#     engtrans = mt.translate(text , "en" , "auto")
#     return engtrans.capitalize()

def speechReco():
     
    driver.get("file:///" + link)

    driver.find_element(by=By.ID , value="start").click()

    while True:
        try:
            text = driver.find_element(by=By.ID , value="output").text

            if text:
                driver.find_element(by=By.ID , value="end").click()
                return (text)
                # else:
                #     setassistantstatus("Translating ...")
                #     return querymodifier(UniversalTranslator(text))
        except:
            pass
                 
     
     



if __name__ == "__main__":
    while True:
        q = speechReco()
        print(q)