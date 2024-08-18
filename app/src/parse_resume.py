import os
from pyairtable import Api
from dotenv import load_dotenv
import io
import requests
from PyPDF2 import PdfReader
from openai import OpenAI
import json
from datastores.ul_airtable import Student
from src.constants import schools, majors, graduation_times, skills

load_dotenv()
client = OpenAI()
api = Api(os.getenv("AIRTABLE_PERSONAL_TOKEN"))
students_table = api.table(
    os.getenv("OLD_STUDENTS_BASE"), os.getenv("OLD_STUDENTS_TABLE")
)

students = students_table.all()[160:]


def extract_pdf_text(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"
    }
    response = requests.get(url=url, headers=headers, timeout=120)
    pdf_file = PdfReader(io.BytesIO(response.content))
    all_text = "".join(
        page.extract_text() for page in pdf_file.pages if page.extract_text()
    )
    return all_text


tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_resume_information",
            "description": "Extract the information from a resume to upload into a database",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the student"},
                    "email": {
                        "type": "string",
                        "description": "Email address of the student",
                    },
                    "linkedin": {
                        "type": "string",
                        "description": "LinkedIn profile URL",
                    },
                    "github": {"type": "string", "description": "GitHub profile URL"},
                    "website": {
                        "type": "string",
                        "description": "Personal website URL",
                    },
                    "school": {
                        "type": "string",
                        "description": "Name of the school the student attended",
                        "enum": schools,
                    },
                    "majors": {
                        "type": "array",
                        "description": "List of student's major field of studies. Disregard minors",
                        "items": {"type": "string", "enum": majors},
                    },
                    "graduation_time": {
                        "type": "string",
                        "description": "Expected or actual graduation semester. If no month is specified, assume Spring.",
                        "enum": graduation_times,
                    },
                    "skills": {
                        "type": "array",
                        "items": {"type": "string", "enum": skills},
                        "description": "List of technical skills",
                    },
                },
                "required": [
                    "name",
                    "email",
                    "school",
                    "majors",
                    "graduation_time",
                    "skills",   
                ],
            },
        },
    }
]


def add_student_to_new_students(all_text: str):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": all_text}],
        tools=tools,
        tool_choice="auto",
    )

    completion_json = json.loads(
        completion.choices[0].message.tool_calls[0].function.arguments
    )

    student = Student(
        name=completion_json.get("name").title(),
        email=completion_json.get("email").lower(),
        linkedin=completion_json.get("linkedin"),
        github=completion_json.get("github"),
        website=completion_json.get("website"),
        school=(
            completion_json.get("school")
            if completion_json.get("school") in schools
            else "Other"
        ),
        major=[major for major in completion_json.get("majors") if major in majors],
        graduation_time=(
            completion_json.get("graduation_time")
            if completion_json.get("graduation_time") in graduation_times
            else "Other"
        ),
        skills=[skill for skill in completion_json.get("skills") if skill in skills],
        resume=[{"url": url}],
    )

    student.save()


def is_legit(all_text: str):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", "content": "Would Steve Jobs think this person is legit? Use the highest standards",
            },
            {"role": "user", "content": all_text},
        ],
    )

    return completion.choices[0].message.content


new_students_table = api.table(
    os.getenv("NEW_STUDENTS_BASE"), os.getenv("NEW_STUDENTS_TABLE")
)

for student_record in students:
    if not student_record["fields"].get("Resume"):
        continue
    url = student_record["fields"]["Resume"][0]["url"]
    all_text = extract_pdf_text(url)
    add_student_to_new_students(all_text)
