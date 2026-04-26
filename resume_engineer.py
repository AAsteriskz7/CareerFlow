"""
Task: Build the Resume Tailor node.

Focus: Use PydanticAI to enforce strict JSON outputs. Write the prompts that prevent the LLM from hallucinating skills.

Input/Output: Takes the target job description and a base resume; returns a highly structured, tailored JSON resume.
"""

#Takes  resume3
from pydantic_ai import Agent #for the ai parsing
from pypdf import PdfReader
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
load_dotenv()


class ResumeSchema(BaseModel):
    name: str
    contact: str
    experience: List[str]
    education: List[str]
    skills: List[str]
    projects: List[str]
    achievements: List[str]



reader = PdfReader("Adarsh_Setty_Resume.pdf")
full_text = ""
for i, page in enumerate(reader.pages):
    full_text += page.extract_text() + "\n"

agent = Agent(
  'google-gla:gemini-3.1-flash-lite-preview',
  system_prompt='Extract the content from the provided resume text.',
  output_type=ResumeSchema  
)

result = agent.run_sync(full_text)
print(result.output.model_dump_json(indent=2))





# from pydantic import BaseModel

# class SkillSection(BaseModel):
#     category: str
#     skills: list[str]

# class ResumeStructure(BaseModel):
#     name: str
#     contact_email: str
#     technical_skills: list[SkillSection]


# from pydantic_ai import Agent

# # 1. Initialize the Agent
# # You tell it which model to use (e.g., an OpenAI or Gemini model)
# # You tell it the exact Pydantic model it MUST return using `result_type`
# agent = Agent(
#     'openai:gpt-4o', 
#     result_type=ResumeStructure 
# )


# agent = Agent(
#     'openai:gpt-4o',
#     result_type=ResumeStructure,
#     system_prompt=(
#         "You are an expert, highly strictly Resume Engineer. "
#         "Your job is to tailor a Base Resume to match a Job Description. "
#         "CRITICAL RULES: "
#         "1. You may ONLY include skills that are explicitly stated in the Base Resume. "
#         "2. DO NOT invent, infer, or hallucinate skills just because they are in the Job Description. "
#         "3. You may reorder or highlight existing skills to better match the Job Description, but you cannot create new ones."
#     )
# )


# # Create your prompt containing the specific inputs
# user_prompt = f"""
# Here is the Target Job Description:
# {job_description_text}

# Here is the Base Resume:
# {base_resume_text}
# """

# # Run the agent
# result = agent.run_sync(user_prompt)

# # Access the structured data
# print(result.data.name)
# print(result.data.technical_skills)


# import os
# from dotenv import load_dotenv
# from pydantic_ai import Agent

# # This magically loads the variables from your .env file into your computer's memory
# load_dotenv()

# # Now, when you initialize PydanticAI, it automatically finds the API key!
# agent = Agent('google-gla:gemini-1.5-flash') 
