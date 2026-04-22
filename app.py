from fastapi import FastAPI
from pydantic import BaseModel
import re
import os
from openai import OpenAI

app = FastAPI()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class QueryRequest(BaseModel):
    query: str
    assets: list = []

# ---------------- RULE BASED ----------------
def rule_solver(text):
    t = text.lower()

    t = re.sub(r'\b(plus|add|sum|total|and)\b', '+', t)
    t = t.replace(",", "+")

    numbers = list(map(int, re.findall(r'\d+', t)))

    if len(numbers) >= 2:
        return sum(numbers)

    return None

# ---------------- LLM FALLBACK ----------------
def llm_solver(query):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract numbers and return ONLY the sum as an integer."},
                {"role": "user", "content": query}
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip()
        return int(result)

    except:
        return None

# ---------------- MAIN API ----------------
@app.post("/")
def solve(req: QueryRequest):
    query = req.query

    # Step 1: Rule-based (fast)
    result = rule_solver(query)

    # Step 2: LLM fallback (rare)
    if result is None:
        result = llm_solver(query)

    if result is not None:
        return {"output": f"The sum is {result}."}

    return {"output": "I cannot solve this."}
