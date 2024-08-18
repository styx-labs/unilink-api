from ..datastores.ul_github import ul_github
from ..datastores.ul_openai import client
import json

def get_all_files(repo):
    files = []
    try:
        contents = repo.get_contents("")
    except Exception as e:
        if e.status == 404:
            # Skip empty repositories
            return files
        else:
            raise e
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir" and file_content.name not in [
            "node_modules",
            "venv",
            "__pycache__",
            "dist",
            "build",
            "target",
            "bin",
            "obj",
        ]:
            contents.extend(repo.get_contents(file_content.path))
        elif (
            file_content.name in ["package-lock.json", "package.json"]
            or file_content.name.startswith(".")
            or "config" in file_content.name
        ):
            # Skip package-lock.json, package.json, and hidden files
            continue
        elif file_content.type == "file" and file_content.name.endswith(
            (
                ".py",  # Python
                ".js",  # JavaScript
                ".html",  # HTML
                ".css",  # CSS
                ".java",  # Java
                ".cpp",  # C++
                ".c",  # C
                ".cs",  # C#
                ".rb",  # Ruby
                ".php",  # PHP
                ".ts",  # TypeScript
                ".go",  # Go
                ".rs",  # Rust
                ".swift",  # Swift
                ".kt",  # Kotlin
                ".m",  # Objective-C
                ".scala",  # Scala
                ".sh",  # Shell script
                ".r",  # R
                ".pl",  # Perl
                ".sql",  # SQL
                ".xml",  # XML
                ".json",  # JSON
                ".yml",  # YAML
                ".yaml",  # YAML
            )
        ):
            files.append(file_content)
    return files


def get_top_repos(repos, criteria="stars", top_n=5):
    sorted_repos = sorted(repos, key=lambda x: x.get(criteria, 0), reverse=True)
    return sorted_repos[:top_n]


def list_repos(github_url: str):
    try:
        repos = []
        if github_url:
            username = github_url.split("/")[-1]
            user = ul_github.get_user(username)
            for repo in user.get_repos():
                repos.append(
                    {
                        "name": repo.name,
                        "description": repo.description,
                        "url": repo.html_url,
                        "stars": repo.stargazers_count,
                        "forks": repo.forks_count,
                        "language": repo.language,
                        "contents": get_all_files(repo),
                    }
                )
        return repos
    except Exception as e:
        print(f"Error fetching repositories: {str(e)}")
        return []


def analyze_languages(repos):
    language_usage = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            language_usage[lang] = language_usage.get(lang, 0) + 1
    return language_usage


def estimate_proficiency(language_usage):
    total_repos = sum(language_usage.values())
    proficiency = {}
    for lang, count in language_usage.items():
        percentage = (count / total_repos) * 100
        if percentage > 50:
            proficiency[lang] = "Advanced"
        elif percentage > 25:
            proficiency[lang] = "Intermediate"
        else:
            proficiency[lang] = "Beginner"
    return proficiency


tools = [
    {
        "type": "function",
        "function": {
            "name": "rate_repo",
            "description": "Evaluate a GitHub repository on a scale from 1 to 10 based on the following criteria: (1: Represents beginner-level code, demonstrating basic understanding and practice. 10: Represents outstanding code quality, comparable to that written by a principal engineer at Google, showcasing mastery, innovation, and top-tier proficiency (top 0.01% of Googlers).",
            "parameters": {
                "type": "object",
                "properties": {
                    "complexity_rating": {
                        "type": "integer",
                        "description": "Code complexity: Analyze the sophistication and intricacy of the codebase, including the use of advanced algorithms, design patterns, and architecture.",
                    },
                    "quality_rating": {
                        "type": "integer",
                        "description": "Code Quality: Assess adherence to coding best practices, including readability, maintainability, and thorough documentation. Look for clean, efficient, and well-structured code.",
                    },
                    "impact_rating": {
                        "type": "integer",
                        "description": "Impact: Measure the significance and influence of the code on the project and its broader contribution to the community. Consider factors such as usage, stars, forks, and community engagement.",
                    },
                    "comments": {
                        "type": "string",
                        "description": "Detailed comments on the repository, including strengths, weaknesses, and suggestions for improvement.",
                    },
                },
            },
            "requried": [
                "complexity_rating",
                "quality_rating",
                "impact_rating",
                "comments",
            ],
        },
    },
]


def rate_repo(repo):
    code_snippets = [
        file.decoded_content.decode("utf-8")
        for file in repo["contents"]
        if file.content
    ]
    code = "\n".join(code_snippets[:5])  # Limit to first 5 files to avoid token limit
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"Repository: {repo['name']}\n\nCode:\n{code}",
            },
        ],
        tools=tools,
        tool_choice="auto",
    )
    return {
        "repo_name": repo["name"],
        "analysis": completion.choices[0].message.tool_calls[0].function.arguments,
    }


def rate_github(github_url: str):
    repos = list_repos(github_url)
    top_repos = get_top_repos(repos)
    language_proficiency = estimate_proficiency(analyze_languages(repos))

    analysis_results = []
    for repo in top_repos:
        analysis_results.append(rate_repo(repo))
        
    sum = 0
    for analysis in analysis_results:
        result = json.loads(analysis["analysis"])
        sum += result["complexity_rating"]
        sum += result["quality_rating"]
        sum += result["impact_rating"]
    sum = sum / len(analysis_results) / 3

    return {
        "overall_score": sum,
        "language_proficiency": language_proficiency,
        "top_repos_analysis": analysis_results,
    }