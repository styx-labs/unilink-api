from pyairtable.orm import Model, fields as F
import os
from dotenv import load_dotenv

load_dotenv()

class Student(Model):
    name = F.TextField("Name")
    email = F.EmailField("Email")
    linkedin = F.UrlField("LinkedIn")
    github = F.UrlField("GitHub")
    website = F.UrlField("Website")
    school = F.SelectField("School")
    major = F.MultipleSelectField("Major(s)")
    graduation_time = F.SelectField("Graduation Time")
    skills = F.MultipleSelectField("Skills")
    resume = F.AttachmentsField("Resume")

    class Meta:
        base_id = os.getenv("NEW_STUDENTS_BASE")
        table_name = os.getenv("NEW_STUDENTS_TABLE")
        api_key = os.getenv("AIRTABLE_PERSONAL_TOKEN")