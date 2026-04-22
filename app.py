from fastapi import FastAPI
from pydantic import BaseModel
import re
app = FastAPI()
class QueryRequest(BaseModel):
    query: str
    assets: list = []
    class Config:
        schema_extra = {
            "example": {
                "query": "What is 10 + 15?",
                "assets": []
            }
        }
@app.post("/")
def solve(req: QueryRequest):
    text = req.query.lower()
    # Normalize all possible addition words
    replacements = {
        "plus": "+",
        "add": "+",
        "sum": "+",
        "total": "+",
        "and": "+",
        ",": "+",
    }
    for word, symbol in replacements.items():
        text = text.replace(word, symbol)
    numbers = list(map(int, re.findall(r'\d+', text)))
    if len(numbers) >= 2:
        result = sum(numbers)
        return {"output": f"The sum is {result}."}
    return {"output": "I cannot solve this."}
