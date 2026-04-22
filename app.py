import time
from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    assets: list = []

@app.post("/")
def solve(req: QueryRequest):
    start = time.time()

    text = req.query.lower()
    numbers = list(map(int, re.findall(r'\d+', text)))

    if any(word in text for word in ["add", "sum", "+"]):
        result = sum(numbers)

        end = time.time()
        print("Execution time:", end - start)   # 👈 THIS LINE

        return {"output": f"The sum is {result}."}

    return {"output": "I cannot solve this."}
