from fastapi import FastAPI
from pydantic import BaseModel
import re
import os
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class QueryRequest(BaseModel):
    query: str
    assets: list = []

# ---------- RULE BASED ----------
def rule_solver(text):
    t = text.lower()

    # Normalize words
    t = re.sub(r'\b(plus|add|sum|total|and)\b', '+', t)
    t = t.replace(",", "+")

    # Extract numbers (handles ints, decimals, negatives)
    numbers = re.findall(r'-?\d+\.?\d*', t)

    try:
        nums = [float(n) for n in numbers]
    except:
        return None

    if len(nums) >= 2:
        return sum(nums)

    return None

# ---------- LLM FALLBACK ----------
def llm_solver(query):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Extract all numbers (including fractions, decimals, negatives) and return ONLY their sum as a number."
                },
                {"role": "user", "content": query}
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip()
        return float(result)

    except:
        return None

# ---------- FORMAT OUTPUT ----------
def format_number(num):
    # remove .0 for integers
    if num == int(num):
        return str(int(num))
    return str(round(num, 5))

# ---------- MAIN ----------
@app.post("/")
def solve(req: QueryRequest):
    query = req.query

    # Rule-based first (fast)
    result = rule_solver(query)

    # LLM fallback (only if needed)
    if result is None:
        result = llm_solver(query)

    if result is not None:
        return {"output": f"The sum is {format_number(result)}."}

    return {"output": "I cannot solve this."}
