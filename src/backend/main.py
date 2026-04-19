# pip install langchain-google-genai
from langchain_google_genai import ChatGoogleGenerativeAI
from google.colab import userdata
import json

def draft_cover_letter_prompt(experience: str, job_description: str) -> str:
    return f"""You are an expert career strategist and technical recruiter. Your objective is to write a targeted, fact-based, and professionally polite cover letter draft by mapping a candidate's structured experience to a specific job description.

    INPUTS:
    Candidate Experience (JSON format):
    {experience}

    Target Job Description:
    {job_description}

    CRITICAL GUARDRAILS:
    1. Zero Hallucination: You must rely STRICTLY on the provided JSON data. Do NOT invent or assume any skills, metrics, or experiences. If it isn't in the JSON, it doesn't exist.
    2. Professional Etiquette: Include standard letter components such as a professional greeting (e.g., "Dear Hiring Manager," or "Hello,"), expressions of genuine interest in the role, and a polite closing (e.g., "Thank you for your time and consideration").
    3. Fact-Based Mapping: Identify the most critical needs in the Job Description and directly connect them to the candidate's achievements and hard metrics from the JSON.
    4. Balanced Tone: Maintain a tone that is professionally enthusiastic and warm, but avoid over-the-top corporate "hype." Use phrases like "I am excited to apply" or "I look forward to discussing how my background aligns with your needs."

    HOW TO STRUCTURE THE DRAFT:
    - Salutation: A professional greeting.
    - Opening: State the position you are applying for and a brief, enthusiastic summary of why you are a strong fit based on your core JSON data.
    - Body Paragraph(s): The evidence. Use specific metrics, projects, and technologies from the JSON to prove you can solve the employer's problems.
    - Closing: Reiterate interest, thank the reader for their time, and include a professional sign-off.

    Return ONLY the raw text of the cover letter draft. Do not include any introductory filler, markdown headers, explanations, or metadata.
    """


def cover_letter_evaluation_prompt(experience: str, job_description: str, draft_cover_letter: str) -> str:
    return f"""You are an expert career strategist and technical recruiter. Your task is to **evaluate a candidate's cover letter draft** against a target job description, score its alignment, highlight key strengths, and identify opportunities for improvement. The output must be in **strict JSON format**.

    INPUTS:
    Candidate Experience (JSON format):
    {experience}

    Target Job Description:
    {job_description}

    Candidate's Cover Letter Draft:
    {draft_cover_letter}

    OBJECTIVES:
    1. Fact-Based Evaluation: Identify which key skills, experiences, or achievements in the Job Description are **not addressed or underrepresented** in the cover letter, strictly based on the JSON data.
    2. Highlight Strengths: Identify any experiences, skills, or achievements that are **extremely relevant, perfectly aligned, or stand out** in the cover letter. Emphasize why these are valuable for this specific role.
    3. Scoring System: Assign a **score from 0 to 100**, where:
       - 100 = All critical skills/requirements from the job description are clearly represented in the cover letter
       - 0 = None of the key skills/experiences are represented
       Provide a short justification for the score.
    4. Improvement Opportunities: For missing or underrepresented skills, politely suggest **questions to the user** asking if they have relevant experience, metrics, or examples that could be added. Example: "Do you have experience with X? If yes, please provide details or metrics."
    5. Professional Tone: Feedback should be constructive, concise, and actionable. Avoid generic praise or fluff.
    6. Guardrails:
       - **No hallucination**: Only reference experiences or skills present in the JSON.
       - Do not rewrite the cover letter; focus on evaluation, scoring, highlighting strengths, and prompting the user for missing info.

    OUTPUT FORMAT:
    Return a JSON object with the following structure:
    {{
        'score': <integer from 0 to 10>,
        'score_justification': '<short explanation of the score>',
        'strengths': ['<list key strengths or perfectly aligned experiences>'],
        'missing_skills': ['<list skills or experiences not covered>'],
        'questions': ['<list questions to gather additional user input>']
    }}

    Return ONLY the JSON object. Do not include filler text, introductions, or explanations.
    """


def modify_cover_letter_prompt(experience: str, job_description: str, draft_cover_letter: str, evaluation: str, user_notes: str) -> str:
    return f"""You are an expert career strategist and technical recruiter. Your objective is to **improve and refine an existing cover letter draft** by incorporating user updates, addressing evaluation feedback, and strengthening alignment with the job description.

    INPUTS:
    Candidate Experience (JSON format):
    {experience}

    Target Job Description:
    {job_description}

    Current Cover Letter Draft:
    {draft_cover_letter}

    Evaluation Feedback (JSON format):
    {evaluation}

    User Notes / Updates:
    {user_notes}

    CRITICAL GUARDRAILS:
    1. Zero Hallucination: You must rely STRICTLY on the provided JSON data, evaluation feedback, and user notes. Do NOT invent or assume any skills, metrics, or experiences. If it isn't in the JSON or explicitly provided by the user, it does not exist.
    2. Preserve Strong Content: Do NOT unnecessarily rewrite the entire cover letter. Retain existing content that is already strong, relevant, and well-written, especially areas identified as strengths in the evaluation.
    3. Apply User Updates Faithfully: Carefully incorporate all user notes, edits, or additions into the cover letter. If the user provides new experience, metrics, or phrasing, integrate it naturally and accurately.
    4. Address Evaluation Feedback:
      - Strengthen or add content for missing or underrepresented skills identified in the evaluation, ONLY if supported by the JSON or user notes.
      - Reinforce and highlight strengths identified in the evaluation where appropriate.
      - Improve areas that contributed to a lower score.
    5. Fact-Based Improvement: Strengthen alignment between the candidate's experience and the job description by improving clarity, relevance, and use of metrics where appropriate.
    6. Professional Etiquette: Ensure the letter maintains standard professional structure, including a proper greeting, clear body paragraphs, and a polite closing.
    7. Balanced Tone: Maintain a tone that is professionally enthusiastic and warm, while avoiding excessive hype or generic phrasing.
    8. Minimal Necessary Changes: Only modify parts of the letter that require improvement or where user updates or evaluation feedback apply. Avoid unnecessary rewording.

    HOW TO MODIFY THE DRAFT:
    - Keep the original structure unless there is a clear improvement to be made.
    - Use the evaluation feedback to guide what to improve, expand, or clarify.
    - Strengthen weak or vague sections using specific details from the JSON.
    - Improve transitions, clarity, and conciseness where needed.
    - Ensure the most relevant experiences are clearly connected to the job requirements.
    - Incorporate user-provided updates in a natural and cohesive way.

    OUTPUT:
    Return ONLY the improved cover letter text. Do not include any introductory filler, markdown headers, explanations, or metadata.
    """


def generate_cover_letter(experience, job_description):
    if not experience:
        return "Error: No experience found."
    if not job_description:
        return "Error: No job description found."
    
    llm = ChatGoogleGenerativeAI(
        model='gemini-3.1-flash-lite-preview',
        #model='gemini-3-flash-preview',
        temperature=0.7,
        google_api_key=userdata.get('GEMINI_API_KEY')
    )
    response = llm.invoke(draft_cover_letter_prompt(experience=experience, job_description=job_description))
    cover_letter = response.content[0]['text']
    return cover_letter


def modify_cover_letter(experience, job_description, draft_cover_letter, evaluation, user_notes):
    if not experience:
        return "Error: No experience found."
    if not job_description:
        return "Error: No job description found."
    if not draft_cover_letter:
        return generate_cover_letter(expereince=experience, job_description=job_description)
    if not evaluation:
        evaluation = {}
    if not user_notes:
        user_notes = ""

    llm = ChatGoogleGenerativeAI(
        model='gemini-3.1-flash-lite-preview',
        #model='gemini-3-flash-preview',
        temperature=0.7,
        google_api_key=userdata.get('GEMINI_API_KEY')
    )
    response = llm.invoke(modify_cover_letter_prompt(experience=experience, job_description=job_description, draft_cover_letter=draft_cover_letter, evaluation=evaluation, user_notes=user_notes))
    cover_letter = response.content[0]['text']
    return cover_letter


def evaluate_cover_letter(experience, job_description, draft_cover_letter):
    if not experience:
        return "Error: No experience found."
    if not job_description:
        return "Error: No job description found."
    if not draft_cover_letter:
        return "Error: No cover letter found."

    llm = ChatGoogleGenerativeAI(
        model='gemini-3.1-flash-lite-preview',
        #model='gemini-3-flash-preview',
        temperature=0.7,
        google_api_key=userdata.get('GEMINI_API_KEY')
    )
    response = llm.invoke(cover_letter_evaluation_prompt(experience=experience, job_description=job_description, draft_cover_letter=draft_cover_letter))
    evaluation = json.loads(response.content[0]['text'])
    return evaluation



cover_letter = generate_cover_letter(experience=user_experience, job_description=job_descriptions[2])
print(cover_letter)

evaluation = evaluate_cover_letter(experience=user_experience, job_description=job_descriptions[2], draft_cover_letter=cover_letter)
print(evaluation)

cover_letter = modify_cover_letter(experience=user_experience2, job_description=job_descriptions[2], draft_cover_letter=cover_letter, evaluation=evaluation, user_notes=user_notes)
print(cover_letter)

evaluation = evaluate_cover_letter(experience=user_experience, job_description=job_descriptions[2], draft_cover_letter=cover_letter)
print(evaluation)