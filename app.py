import os
import json
from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
from dotenv import load_dotenv

app = Flask(__name__, static_folder="static")

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"  

GENERATOR_SYSTEM = """You are the Generator Agent in an educational content pipeline.
Your sole responsibility is to generate draft educational content for a given grade level and topic.

Rules:
- Use simple language appropriate for the specified grade level
- Keep explanations engaging and easy to understand
- Ensure all facts are correct
- Generate exactly 3 multiple choice questions
- Each question must have exactly 4 options labelled A, B, C, D
- The answer field must be ONLY a single letter: A, B, C, or D
- You MUST respond with ONLY a valid raw JSON object
- Do NOT use markdown, code fences, or any text outside the JSON

Output format (copy this structure exactly):
{
  "explanation": "grade-appropriate explanation here",
  "mcqs": [
    {
      "question": "question text here",
      "options": ["A. option one", "B. option two", "C. option three", "D. option four"],
      "answer": "A"
    }
  ]
}"""


def generator_agent(grade: int, topic: str, feedback: list = None) -> dict:
    """Generator Agent: produces educational content. Embeds feedback if refining."""
    user_prompt = f"Generate educational content.\nGrade: {grade}\nTopic: {topic}"

    if feedback:
        issues = "\n".join(f"- {f}" for f in feedback)
        user_prompt += f"\n\nFix these issues from the previous draft:\n{issues}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": GENERATOR_SYSTEM},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1024,
    )

    raw = response.choices[0].message.content.strip()
    if "```" in raw:
        parts = raw.split("```")
        for p in parts:
            p = p.strip()
            if p.startswith("json"):
                p = p[4:].strip()
            if p.startswith("{"):
                raw = p
                break
    return json.loads(raw)

REVIEWER_SYSTEM = """You are the Reviewer Agent in an educational content pipeline.
Your sole responsibility is to evaluate educational content for quality.

Evaluation criteria:
1. Age appropriateness — Is the language right for the grade level?
2. Conceptual correctness — Are all facts accurate?
3. Clarity — Is the explanation easy to understand?
4. MCQ quality — Are questions fair, clear, and testing the right concepts?

Rules:
- Be specific (e.g. "The word 'perpendicular' in sentence 2 is not defined")
- Only fail if there are real, meaningful problems
- You MUST respond with ONLY a valid raw JSON object
- Do NOT use markdown, code fences, or any text outside the JSON

Output format:
{
  "status": "pass",
  "feedback": []
}
OR
{
  "status": "fail",
  "feedback": ["Specific issue 1", "Specific issue 2"]
}"""


def reviewer_agent(grade: int, topic: str, content: dict) -> dict:
    """Reviewer Agent: evaluates Generator output, returns pass/fail + feedback."""
    user_prompt = (
        f"Review this educational content.\nGrade: {grade}\nTopic: {topic}\n\n"
        + json.dumps(content, indent=2)
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": REVIEWER_SYSTEM},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=512,
    )

    raw = response.choices[0].message.content.strip()
    if "```" in raw:
        parts = raw.split("```")
        for p in parts:
            p = p.strip()
            if p.startswith("json"):
                p = p[4:].strip()
            if p.startswith("{"):
                raw = p
                break
    return json.loads(raw)


def run_pipeline(grade: int, topic: str) -> dict:
    """
    Full pipeline:
      1. Generator  →  draft content
      2. Reviewer   →  pass / fail + feedback
      3. Refiner    →  re-generate with feedback (ONE pass only, if failed)
    """
    result = {
        "input":          {"grade": grade, "topic": topic},
        "draft":          None,
        "review":         None,
        "refined":        None,
        "refined_needed": False,
    }

    result["draft"]  = generator_agent(grade, topic)
    result["review"] = reviewer_agent(grade, topic, result["draft"])

    if result["review"]["status"] == "fail":
        result["refined_needed"] = True
        result["refined"] = generator_agent(grade, topic, result["review"]["feedback"])

    return result

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/run", methods=["POST"])
def api_run():
    data  = request.get_json()
    grade = int(data.get("grade", 4))
    topic = str(data.get("topic", "")).strip()

    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    if not (1 <= grade <= 12):
        return jsonify({"error": "Grade must be 1–12"}), 400

    try:
        return jsonify(run_pipeline(grade, topic))
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Model returned invalid JSON: {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    key = os.environ.get("GROQ_API_KEY", "")
    print("\n" + "="*55)
    print("  Eklavya AI Content Pipeline  (Groq — Free)")
    print("  http://localhost:5000")
    if not key or key == "YOUR_GROQ_API_KEY_HERE":
        print("\n  ⚠  Set your key:  export GROQ_API_KEY=gsk_...")
        print("  Get free key:    https://console.groq.com")
    print("="*55 + "\n")
    app.run(debug=True, port=5000)
