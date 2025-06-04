# marian_server.py

from fastapi import FastAPI, Request
from marian_manager import MarianManager

app = FastAPI()
manager = MarianManager()

@app.post("/translate")
async def getTranslation(request: Request) -> dict[str, str]:
    # Parse incoming JSON (expects {"text": "your source sentence"})
    data = await request.json()
    src_text = data.get("text", "")
    
    # Perform translation (the manager returns a list; we take the first element)
    translated_list = manager.translate(src_text)
    translated_text = translated_list[0] if translated_list else ""

    # Return a JSON object with the translation
    return {"translation": translated_text}

@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint for your model."""
    return {"message": "health ok"}
