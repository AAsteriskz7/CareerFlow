# - python -m venv .venv
# - .venv\Scripts\Activate
# - pip install langchain-google-genai flask flask-cors python-dotenv


from langchain_google_genai import ChatGoogleGenerativeAI
import json

from flask import Flask, redirect, request, session, jsonify
from flask_cors import CORS

from prompts import draft_cover_letter_prompt, modify_cover_letter_prompt, cover_letter_evaluation_prompt

import os
from dotenv import load_dotenv


app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


@app.route('/generate_cover_letter', methods=["POST"])
def generate_cover_letter():
    data = request.get_json(silent=True)

    experience = data.get("experience", {})
    job_description = data.get("job_description", "")

    if not experience:
        return jsonify({"error": "No experience found.", "error_code": 400}), 400
    if not job_description:
        return jsonify({"error": "No job description found.", "error_code": 400}), 400
    
    llm = ChatGoogleGenerativeAI(
        model='gemini-3.1-flash-lite-preview',
        #model='gemini-3-flash-preview',
        temperature=0.7,
        google_api_key=GEMINI_API_KEY
    )
    response = llm.invoke(draft_cover_letter_prompt(experience=experience, job_description=job_description))
    cover_letter = response.content[0]['text']
    return jsonify({"cover_letter": cover_letter}), 200


@app.route('/modify_cover_letter', methods=["POST"])
def modify_cover_letter():
    data = request.get_json(silent=True)

    experience = data.get("experience", {})
    job_description = data.get("job_description", "")
    draft_cover_letter = data.get("draft_cover_letter", "")
    evaluation = data.get("evaluation", {})
    user_notes = data.get("user_notes", "")

    if not experience:
        return jsonify({"error": "No experience found.", "error_code": 400}), 400
    if not job_description:
        return jsonify({"error": "No job description found.", "error_code": 400}), 400
    if not draft_cover_letter:
        return jsonify({"error": "No draft cover letter found.", "error_code": 400}), 400
    if not evaluation:
        print("Evaluation not found.")
        evaluation = {}
    if not user_notes:
        print("User notes not found.")
        user_notes = ""

    llm = ChatGoogleGenerativeAI(
        model='gemini-3.1-flash-lite-preview',
        #model='gemini-3-flash-preview',
        temperature=0.7,
        google_api_key=GEMINI_API_KEY
    )
    response = llm.invoke(modify_cover_letter_prompt(experience=experience, job_description=job_description, draft_cover_letter=draft_cover_letter, evaluation=evaluation, user_notes=user_notes))
    cover_letter = response.content[0]['text']
    return jsonify({"cover_letter": cover_letter}), 200


@app.route('/evaluate_cover_letter', methods=["POST"])
def evaluate_cover_letter():
    data = request.get_json(silent=True)

    experience = data.get("experience", {})
    job_description = data.get("job_description", "")
    draft_cover_letter = data.get("draft_cover_letter", "")

    if not experience:
        return jsonify({"error": "No experience found.", "error_code": 400}), 400
    if not job_description:
        return jsonify({"error": "No job description found.", "error_code": 400}), 400
    if not draft_cover_letter:
        return jsonify({"error": "No cover letter found.", "error_code": 400}), 400

    llm = ChatGoogleGenerativeAI(
        model='gemini-3.1-flash-lite-preview',
        #model='gemini-3-flash-preview',
        temperature=0.7,
        google_api_key=GEMINI_API_KEY
    )
    response = llm.invoke(cover_letter_evaluation_prompt(experience=experience, job_description=job_description, draft_cover_letter=draft_cover_letter))
    evaluation = json.loads(response.content[0]['text'])
    return jsonify({"evaluation": evaluation}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

"""
Testing

cover_letter = generate_cover_letter(experience=user_experience, job_description=job_descriptions[2])
print(cover_letter)

evaluation = evaluate_cover_letter(experience=user_experience, job_description=job_descriptions[2], draft_cover_letter=cover_letter)
print(evaluation)

cover_letter = modify_cover_letter(experience=user_experience2, job_description=job_descriptions[2], draft_cover_letter=cover_letter, evaluation=evaluation, user_notes=user_notes)
print(cover_letter)

evaluation = evaluate_cover_letter(experience=user_experience, job_description=job_descriptions[2], draft_cover_letter=cover_letter)
print(evaluation)
"""