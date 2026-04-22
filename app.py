from fastapi import FastAPI
from pydantic import BaseModel
import re
import os
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.getenv("acefab3627ca481cc868034d787bb43e"))

class QueryRequest(BaseModel):
    query: str
    assets: list = []

# --- RULE BASED FAST PATH ---
def solve_rule_based(text: str):
    t = text.lower()

    # Normalize
    replacements = {
        "plus": "+",
        "add": "+",
        "sum": "+",
        "total": "+",
        "and": "+",
        ",": "+"
    }

    for k, v in replacements.items():
        t = t.replace(k, v)

    numbers = list(map(int, re.findall(r'\d+', t)))

    if len(numbers) >= 2:
        return sum(numbers)

    return None

# --- LLM FALLBACK ---
def solve_llm(text: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract numbers from the query and return ONLY the sum as a number."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0
    )

    try:
        return int(response.choices[0].message.content.strip())
    except:
        return None

# --- MAIN API ---
@app.post("/")
def solve(req: QueryRequest):
    query = req.query

    # 1. Try rule-based first (FAST)
    result = solve_rule_based(query)

    # 2. Fallback to LLM (RARE)
    if result is None:
        result = solve_llm(query)

    if result is not None:
        return {"output": f"The sum is {result}."}

    return {"output": "I cannot solve this."}
