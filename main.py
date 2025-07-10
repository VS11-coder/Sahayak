# import os
# from flask import Flask, request, jsonify, render_template
# import google.generativeai as genai
# from PIL import Image # Pillow library to handle images
# import io

# app = Flask(__name__)

# # --- Configure the Gemini API with your key ---
# # It's best practice to set this as an environment variable,
# # but for speed tonight, you can paste it directly.
# YOUR_API_KEY = "AIzaSyBs3sfIvPppnhcYn7TBCWAXzOCG0Y8BEfs"
# genai.configure(api_key=YOUR_API_KEY)

# # Configure the Gemini Model
# model = genai.GenerativeModel("gemini-2.5-pro")

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/generate_worksheets', methods=['POST'])
# def generate_worksheets():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     # Open the image file using Pillow
#     img = Image.open(file.stream)

#     # The Magic Prompt! (This stays the same)
#     prompt = """
#     You are an expert Indian teaching assistant for a multi-grade classroom.
#     Analyze the provided textbook page image.
#     Based on the content, generate three distinct worksheets in English for different learning levels.
#     The output must be a valid JSON object with three keys: "grade3", "grade5", and "grade7".
#     Each key's value should be the text content for that worksheet.

#     - "grade3": A simple worksheet with 5 fill-in-the-blank questions.
#     - "grade5": A worksheet with 4 short-answer questions that require reasoning.
#     - "grade7": A worksheet with 2 problem-solving activities or higher-order thinking questions.
#     """

#     # Call the model with the image and prompt
#     response = model.generate_content([prompt, img])

#     # Extract and return the JSON
#     cleaned_json_string = response.text.replace("```json", "").replace("```", "").strip()
#     return cleaned_json_string



# @app.route('/generate_story', methods=['POST'])
# def generate_story():
#     try:
#         user_prompt = request.json['prompt']
#         if not user_prompt:
#             return jsonify({'error': 'Prompt cannot be empty'}), 400

#         # The Magic Prompt for this feature
#         final_prompt = f"""
#         You are a helpful teaching assistant in India. The user has asked for a story or an explanation.
#         Generate a simple, culturally relevant response in Hinglish (a mix of Hindi and English) based on the following topic.
#         The response should be easy for a 10-year-old to understand.
#         Topic: "{user_prompt}"
#         """

#         # Call the model (text-only this time)
#         # Note: We are re-using the same 'model' object we defined earlier
#         response = model.generate_content(final_prompt)
        
#         return jsonify({'story': response.text})

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500



# if __name__ == '__main__':
#     app.run(debug=True)



from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image
import os # We'll use os to get the key safely

app = Flask(__name__)
CORS(app)

# --- SAFER: Configure the Gemini API with an Environment Variable ---
# For a quick fix, you can paste your NEW key here, but this is the better way.
# Set an environment variable named GOOGLE_API_KEY with your key.
try:
    # BEST PRACTICE:
    # genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

    # QUICK HACKATHON FIX (Use your NEW key, not the old one):
    genai.configure(api_key="AIzaSyDttMk51PjA4YUJJ-jd5Wz23aaX01Yxjjw")

except AttributeError:
    print("ERROR: GOOGLE_API_KEY environment variable not set.")
    exit()


# Configure the Gemini Model with the CORRECT name
model = genai.GenerativeModel("gemini-2.5-pro")

@app.route('/generate_worksheets', methods=['POST'])
def generate_worksheets():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        img = Image.open(file.stream)
        prompt = """
        You are an expert Indian teaching assistant for a multi-grade classroom.
        Analyze the provided textbook page image. Based on the content, generate three distinct worksheets in English for different learning levels. The output must be a valid JSON object with three keys: "grade3", "grade5", and "grade7". Each key's value should be the text content for that worksheet.
        - "grade3": A simple worksheet with 5 fill-in-the-blanks questions.
        - "grade5": A worksheet with 4 short-answer questions that require reasoning.
        - "grade7": A worksheet with 2 problem-solving activities or higher-order thinking questions.
        """
        response = model.generate_content([prompt, img])
        cleaned_json_string = response.text.replace("```json", "").replace("```", "").strip()
        return cleaned_json_string
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Failed to process the request.'}), 500


@app.route('/generate_story', methods=['POST'])
def generate_story():
    try:
        user_prompt = request.json['prompt']
        if not user_prompt:
            return jsonify({'error': 'Prompt cannot be empty'}), 400

        final_prompt = f"""
        You are a helpful teaching assistant in India. The user has asked for a story or an explanation. Generate a simple, culturally relevant response in Hinglish based on the following topic. The response should be easy for a 10-year-old to understand.
        Topic: "{user_prompt}"
        """
        response = model.generate_content(final_prompt)
        return jsonify({'story': response.text})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Failed to process the request.'}), 500




@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    try:
        data = request.json
        topic = data.get('topic')
        duration = data.get('duration')

        if not topic or not duration:
            return jsonify({'error': 'Topic and duration are required.'}), 400

        # This is a detailed prompt to get a structured response
        final_prompt = f"""
        You are an expert curriculum designer for Indian schools.
        Create a structured, day-by-day lesson plan for the following topic.

        Topic: "{topic}"
        Duration: "{duration}"

        Your response must be formatted in Markdown.
        For each day, provide these three sections:
        1.  **Objective:** What is the learning goal for the day?
        2.  **Classroom Activity:** A simple, engaging activity to do in class.
        3.  **Homework:** A short assignment to reinforce the day's learning.

        Example for one day:
        ### Day 1: Introduction to the Topic
        * **Objective:** Students will be able to define the key terms.
        * **Classroom Activity:** Group discussion on what students already know about the topic.
        * **Homework:** Read the first two pages of the chapter and write down three new words they learned.
        """

        response = model.generate_content(final_prompt)
        return jsonify({'plan': response.text})

    except Exception as e:
        print(f"An error occurred in plan generation: {e}")
        return jsonify({'error': 'Failed to generate the lesson plan.'}), 500









# This starts the server when you run "python main.py"
if __name__ == '__main__':
    app.run(debug=True, port=5000)