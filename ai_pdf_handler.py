""""
 Google Generative AI Python SDK, which is a library provided by Google to interact with their Gemini AI models.
 This package allows you to use Google's powerful AI models (like gemini-1.5-flash) in your Python programs.

"""

from dotenv import load_dotenv

load_dotenv()

import os
import google.generativeai as genai
from PyPDF2 import PdfReader

# first we need to accses the Gemni AI model, for that we need API KEY
# API is like a password or a special code that allows your program to communicate with an external service
# (in this case, Google's Gemini AI). It ensures that only authorized users can access the service.
# Without an API key, Google won't know who is making the request or whether you have permission to use their AI model.
# It acts as a security measure to prevent unauthorized access to the service.

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# we now need to set up a connection to gemni AI model, using the API key
genai.configure(api_key=GEMINI_API_KEY)

# The System Instructions tells the AI who it is and rules it should follow
# The AI in this project is a dialogue generator
SystemInstructions = """ You are a dialogue generator creating conversations between a teacher and student. Follow these rules:
1. Teacher explains concepts clearly
3. The student will begin by asking the teacher to explain a specific topic. This topic will be derived from the provided data. The teacher will then respond by thoroughly explaining the topic in a clear and engaging manner
2. Student asks thoughtful, beginner-friendly questions. 
3. Cover all key points from the provided material
4. Use natural, conversational language
6. Mark speakers clearly with "Teacher:" and "Student:
7. Use the following format:
   Teacher: ...
   Student: ...
"""

# load the gemni model
"""
It loads the Gemini AI model (gemini-1.5-flash) and applies the system instructions to it.
The model is now ready to generate responses based on the rules you defined.
"""
model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=SystemInstructions)


# create function that will get the contents of our data. This will be contents of the pdf file
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"  # extracts the text from each page. then adds a \n charachter.
    return text.strip()  # remove any leading and tralling whitespace


def generate_dialogue(pdf_content):
    chat = model.start_chat()  # returns a chat session. return a object
    # It creates a conversational interface where you can send multiple messages back and forth (like a chat).
    prompt = f"""Create a dialogue between teacher and student based on this material.
        {pdf_content[:10000]} # limit the data for now to be 10k. Can be changed in the future.
        """
    response = chat.send_message(prompt)  # based on the prompt(question) chat.send_messege will ask a reply from
    # the AI based on the prompt. The response will represented as an object.
    return response.text  # text is attribute that contains the AI response. Do not confused with the text variable in the extract_text_from_pdf method.


def generate_content(pdf_file: str):
    '''
    :param pdf_file: File path of the pdf file that will be used to generate content from.
    :return: Must return a list in the following format:
    [
        (1, "Hello! I'm Person 1"),
        (2, "And I'm Person 2!"),
        (1, "Person 1 again!!")
    ]
    '''
    pdf_data = extract_text_from_pdf(pdf_file)
    conversation = generate_dialogue(pdf_data)
    lines = conversation.strip().split(
        '\n')  # will sepreate each dilouge as a element in the list. No whitespce or \n will be in each dilouge
    data = []  # the place where will store the list of tuples in the format of (1, "Hello! I'm Person 1")
    for line in lines:
        if line.startswith("Student:"):
            studentLine = line.replace("Student:", "").strip()
            data.append((2, studentLine))
        elif line.startswith("Teacher:"):
            teacherLine = line.replace("Teacher:", "").strip()
            data.append((1, teacherLine))

    return data

# lets bring it all together
def main():
    content = generate_content("1 - Antiderivatives and Indefinite Integrals.pdf")

    for x in content:
        print(x)
        input()

main()
