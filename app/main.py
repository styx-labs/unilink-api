from fastapi import FastAPI
from pydantic import BaseModel
from .src.rate_github import rate_github
from .src.rate_portfolio import rate_portfolio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

allowed_origins = [
    "http://localhost:63342",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["X-Requested-With", "Content-Type"],
)

class RateGithubRequest(BaseModel):
    github_url: str
    
class RatePortfolioRequest(BaseModel):
    portfolio_url: str

@app.get("/")
async def root():
    return {"message": "UniLink API"}

@app.post("/rate_github")
async def rate_github_endpoint(request: RateGithubRequest) -> dict:
    return rate_github(request.github_url)

@app.post("/rate_portfolio")
async def rate_portfolio_endpoint(request: RatePortfolioRequest) -> dict:
    return rate_portfolio(request.portfolio_url)