import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List
from ..datastores.ul_openai import client

async def scrape_website(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract links to other pages on the site
    links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True) 
             if urljoin(url, a['href']).startswith(url)]
    
    return {
        'url': url,
        'content': html,
        'links': links
    }

async def scrape_portfolio(base_url: str) -> list:
    visited = set()
    to_visit = [base_url]
    pages = []

    while to_visit:
        url = to_visit.pop(0)
        if url not in visited:
            page = await scrape_website(url)
            pages.append(page)
            visited.add(url)
            to_visit.extend([link for link in page['links'] if link not in visited])
    return pages

async def extract_text(pages: List[dict]) -> List[str]:
    texts = []
    for page in pages:
        soup = BeautifulSoup(page['content'], 'html.parser')
        texts.append(soup.get_text(separator=' ', strip=True))
    return texts

def evaluate_portfolio(texts: List[str]) -> dict:
    # Combine all texts into one string, limiting to a reasonable length to avoid token limits
    combined_text = " ".join(texts)[:100000]  # Limiting to 10000 characters, adjust as needed

    prompt = f"""
    Analyze and rate this portfolio based on the following text extracted from the website:

    {combined_text}

    Please provide:
    1. An overall analysis of the portfolio
    2. Identify and list the main projects mentioned (if any)
    3. Identify and list the key skills mentioned (if any)
    4. A rating out of 10 for each of these categories: Project Diversity, Skill Breadth, Presentation
    5. An overall score out of 10
    6. Specific comments or suggestions for improvement
    7. A brief summary of the portfolio's strengths and weaknesses

    Format your response as a JSON object with the following keys:
    "overall_analysis", "projects", "skills", "ratings", "overall_score", "comments", "summary"

    In the "ratings" object, include "project_diversity", "skill_breadth", and "presentation".
    """
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert at evaluating software developer portfolios. Provide detailed, constructive feedback based on the given text."},
            {"role": "user", "content": prompt}
        ],
        response_format={ "type": "json_object" }
    )

    # Parse the response
    analysis_result = completion.choices[0].message.content

    return analysis_result

# Example usage
async def rate_portfolio(url: str) -> dict:
    pages = await scrape_portfolio(url)
    texts = await extract_text(pages)
    result = evaluate_portfolio(texts)
    return result