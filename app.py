from typing import Literal
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI

app = FastAPI()
client = OpenAI()  # reads OPENAI_API_KEY from your environment

class TestModel(BaseModel):
    name: str


@app.get("/")
def home():
    return {"message": "It works!"}

@app.post("/analyze")

async def analyze_css(file: UploadFile = File(...)):
    filename = file.filename or ""
    if not filename.endswith(".css"):
        raise HTTPException(status_code=400, detail="Please upload a CSS file.")

    contents = await file.read()
    css_text = contents.decode("utf-8")

    analysis = analyze_with_llm(css_text)
    return analysis


    
        
    
    
class BootstrapSuggestion(BaseModel):
    selector: str
    original_css: str
    bootstrap_classes: list[str]
    match_quality: Literal["exact", "approximate", "none"]
    confidence: int = Field(ge=0, le=100)
    explanation: str


class CSSAnalysis(BaseModel):
    convertible_percentage: int = Field(ge=0, le=100)
    overall_difficulty: Literal["easy", "medium", "hard"]
    estimated_manual_minutes: int = Field(ge=0)
    suggestions: list[BootstrapSuggestion]
    custom_css_needed: list[str]
    
from fastapi import HTTPException

def analyze_with_llm(css_text: str) -> CSSAnalysis:
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert front-end engineer."
                 " Analyze the given CSS and suggest equivalent Bootstrap 5 utility classes. "
                 "For each CSS rule, give the closest Bootstrap classes, rate match quality, give a confidence score, and explain."
                 " Flag anything with no Bootstrap equivalent in custom_css_needed. Estimate overall convertibility."},
                {"role": "user", "content": f"Analyze and convert this CSS:\n\n{css_text}"},
            ],
            response_format=CSSAnalysis,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {str(e)}")