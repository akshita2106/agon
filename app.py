from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    assets: list = []

@app.post("/")
def solve(req: QueryRequest):
    text = req.query.lower()

    # Normalize words to +
    text = text.replace("plus", "+")
    text = text.replace("add", "+")
    text = text.replace("sum", "+")
    text = text.replace("total", "+")
    text = text.replace("and", "+")
    text = text.replace(",", "+")
    
    # Extract numbers
    numbers = list(map(int, re.findall(r'\d+', text)))

    # If multiple numbers → assume addition
    if "+" in text or len(numbers) > 1:
        result = sum(numbers)
        return {"output": f"The sum is {result}."}

    return {"output": "I cannot solve this."}
