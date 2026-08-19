# CSS-to-Bootstrap Analyzer

An AI-powered API that analyzes raw CSS and suggests equivalent Bootstrap 5
utility classes. Upload a `.css` file and get back a structured analysis:
which rules map cleanly to Bootstrap, how confident the mapping is, and what
would need to stay as custom CSS.

## What it does

- Accepts a `.css` file upload via a REST endpoint
- Uses the OpenAI API to analyze each CSS rule and suggest Bootstrap 5 classes
- Returns a **structured JSON response** (not free text) with per-rule
  suggestions, match quality, confidence scores, and an overall convertibility
  estimate

## Why it's built this way

The interesting piece is **structured output**: instead of parsing free-form
text back from the model, the app defines the exact response shape with
Pydantic models and has the LLM return data that conforms to that schema. This
makes the output reliable and directly usable by other code.

## Tech stack

- **FastAPI** — REST API and file upload
- **OpenAI API** (gpt-4o-mini) with structured outputs
- **Pydantic** — typed request/response models and validation

## Running it locally

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"
uvicorn app:app --reload
```

Then open `http://localhost:8000/docs`, upload a `.css` file to the `/analyze`
endpoint, and view the structured analysis.

## Example response

```json
{
  "convertible_percentage": 100,
  "overall_difficulty": "easy",
  "suggestions": [
    {
      "selector": ".hero",
      "bootstrap_classes": ["d-flex", "justify-content-center", "w-100"],
      "match_quality": "exact",
      "confidence": 90
    }
  ],
  "custom_css_needed": []
}
```

## Possible improvements

- Response caching to avoid re-analyzing identical CSS
- A web front-end for pasting CSS directly
- Batch analysis of multiple files