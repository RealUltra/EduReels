from dotenv import load_dotenv

load_dotenv()

import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

SystemInstructions = """
You are a dialogue generator creating conversations between a teacher and student. 
Follow these rules:
1. Teacher explains concepts clearly
3. The student will begin by asking the teacher to explain a specific topic. This topic will be derived from the provided data. The teacher will then respond by thoroughly explaining the topic in a clear and engaging manner
2. Student asks thoughtful, beginner-friendly questions. 
3. Cover all key points from the provided material
4. Use natural, conversational language
6. Mark speakers clearly with "Teacher:" and "Student:"
7. Strictly follow the following format with no additional characters:
   Teacher: ...
   Student: ...
"""

model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=SystemInstructions)

def generate_dialogue(pdf_file, additional_instructions=""):
    prompt = "Create a dialogue between teacher and student based on the attached material."

    if additional_instructions:
        prompt += f"\nAdditional Instructions: {additional_instructions}"

    uploaded_file = genai.upload_file(pdf_file)

    response = model.generate_content(prompt)

    genai.delete_file(uploaded_file.name)

    return response.text

def generate_content(pdf_file: str, additional_instructions=""):
    '''
    :param pdf_file: File path of the pdf file that will be used to generate content from.
    :return: Must return a list in the following format:
    [
        (1, "Hello! I'm Person 1"),
        (2, "And I'm Person 2!"),
        (1, "Person 1 again!!")
    ]
    '''
    raw_speech = generate_dialogue(pdf_file, additional_instructions)

    content = []

    for line in raw_speech.strip().split('\n'):
        if line.startswith("Student:"):
            studentLine = line.replace("Student:", "").strip()
            content.append((2, studentLine))
        elif line.startswith("Teacher:"):
            teacherLine = line.replace("Teacher:", "").strip()
            content.append((1, teacherLine))

    return content

