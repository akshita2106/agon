from fastapi import FastAPI
from pydantic import BaseModel
import re
import os
from openai import OpenAI
from sympy import sympify
from sympy.core.sympify import SympifyError

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class QueryRequest(BaseModel):
    query: str
    assets: list = []

# ---------- CLEANING ----------
def normalize(q):
    q = q.lower().strip()

    replacements = {
        "plus": "+",
        "minus": "-",
        "times": "*",
        "multiplied by": "*",
        "x": "*",
        "into": "*",
        "divide by": "/",
        "divided by": "/",
        "over": "/",
        "power of": "**",
        "to the power of": "**",
        "percent of": "*0.01*",
        "sum of": "",
        "what is": "",
        "calculate": "",
        "find": "",
    }

    for a, b in replacements.items():
        q = q.replace(a, b)

    return q

# ---------- SAFE MATH ----------
def solve_math(q):
    try:
        expr = sympify(q)
        val = float(expr)
        return val
    except:
        return None

# ---------- LLM FALLBACK ----------
def llm_interpret(query):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
Convert the user's math question into a valid math expression only.
Examples:
'half of 10 plus 3' => (10/2)+3
'25 percent of 80' => 25/100*80
Return expression only.
"""
                },
                {"role": "user", "content": query}
            ],
            temperature=0
        )

        expr = res.choices[0].message.content.strip()
        return solve_math(expr)

    except:
        return None

# ---------- FORMAT ----------
def fmt(x):
    if x is None:
        return None
    if abs(x - int(x)) < 1e-9:
        return str(int(x))
    return str(round(x, 6)).rstrip("0").rstrip(".")

# ---------- MAIN ----------
@app.post("/")
def solve(req: QueryRequest):
    q = req.query

    # 1. direct parser
    nq = normalize(q)
    ans = solve_math(nq)

    # 2. fallback llm
    if ans is None:
        ans = llm_interpret(q)

    if ans is not None:
        return {"output": f"The answer is {fmt(ans)}."}

    return {"output": "I cannot solve this."}
