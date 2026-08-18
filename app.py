from typing import Literal
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from openai import OpenAI

app = FastAPI()
client = OpenAI()  # reads OPENAI_API_KEY from your environment




@app.get("/")
def home():
    return {"message": "It works!"}

@app.post("/analyze")
@app.post("/analyze", response_class=PlainTextResponse)
async def analyze_css(file: UploadFile = File(...)):
    filename = file.filename or ""
    if not filename.endswith(".css"):
        raise HTTPException(status_code=400, detail="Please upload a CSS file.")

    contents = await file.read()

    try:
        css_text = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text.")

    if not css_text.strip():
        raise HTTPException(status_code=400, detail="The CSS file is empty.")

    analysis = analyze_with_llm(css_text)
    return annotate_css(analysis)   # ← returns the annotated CSS text

        
    
    
class BootstrapSuggestion(BaseModel):
    selector: str
    original_css: str
    bootstrap_classes: list[str]
    match_quality: Literal["exact", "approximate", "none"]
    confidence: int = Field(ge=0, le=100)
    explanation: str


class PropertyMapping(BaseModel):
    property: str          # e.g. "display: flex"
    bootstrap_class: str | None   # e.g. "d-flex", or None if no equivalent
    convertible: bool
    note: str | None = None       # why it can't convert, if applicable

class RuleAnalysis(BaseModel):
    selector: str
    properties: list[PropertyMapping]

class CSSAnalysis(BaseModel):
    rules: list[RuleAnalysis]
    convertible_percentage: int = Field(ge=0, le=100)
    overall_difficulty: Literal["easy", "medium", "hard"]

def analyze_with_llm(css_text: str) -> CSSAnalysis:
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                    {"role": "system", "content": (
                        "You are an expert front-end engineer. For the given CSS, analyze it "
                        "property by property within each rule. For each individual property, "
                        "provide the equivalent Bootstrap 5 utility class, or mark it as not "
                        "convertible with a short note explaining why. Not every property has a "
                        "Bootstrap equivalent — be accurate about which convert and which don't. "
                        "Also estimate the overall convertible percentage and difficulty."
                    )},
                    {"role": "user", "content": f"Analyze and convert this CSS:\n\n{css_text}"},
                ],
            response_format=CSSAnalysis,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {str(e)}")
    
def annotate_css(analysis: CSSAnalysis) -> str:
    lines = []
    for rule in analysis.rules:
        lines.append(f"{rule.selector} {{")
        for prop in rule.properties:
            if prop.convertible:
                comment = f"/* ❌ Change to: {prop.bootstrap_class} */"
            else:
                reason = prop.note or "no Bootstrap equivalent"
                comment = f"/* ✅ {reason} — keep as custom CSS */"
            lines.append(f"    {prop.property};  {comment}")
        lines.append("}")
        lines.append("")  # blank line between rules
    return "\n".join(lines)