import os
from dotenv import load_dotenv
from github import Auth, Github

load_dotenv()

auth = Auth.Token(os.getenv("GITHUB_TOKEN"))
ul_github = Github(auth=auth)