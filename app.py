# # import os
# # import json
# # from flask import Flask, request, jsonify, send_from_directory
# # from groq import Groq
# # from dotenv import load_dotenv

# # app = Flask(__name__, static_folder="static")

# # load_dotenv()

# # client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# # MODEL = "openai/gpt-oss-120b"


# # GENERATOR_SYSTEM = """You are the Generator Agent in an educational content pipeline.
# # Your sole responsibility is to generate draft educational content for a given grade level and topic.

# # Rules:
# # - Use simple language appropriate for the specified grade level
# # - Keep explanations engaging and easy to understand
# # - Ensure all facts are correct
# # - Generate exactly 3 multiple choice questions
# # - Each question must have exactly 4 options labelled A, B, C, D
# # - The answer field must be ONLY a single letter: A, B, C, or D
# # - You MUST respond with ONLY a valid raw JSON object
# # - Do NOT use markdown, code fences, or any text outside the JSON

# # Output format (copy this structure exactly):
# # {
# #   "explanation": "grade-appropriate explanation here",
# #   "mcqs": [
# #     {
# #       "question": "question text here",
# #       "options": ["A. option one", "B. option two", "C. option three", "D. option four"],
# #       "answer": "A"
# #     }
# #   ]
# # }"""


# # def generator_agent(grade: int, topic: str, feedback: list = None) -> dict:
# #     """Generator Agent: produces educational content. Embeds feedback if refining."""
# #     user_prompt = f"Generate educational content.\nGrade: {grade}\nTopic: {topic}"

# #     if feedback:
# #         issues = "\n".join(f"- {f}" for f in feedback)
# #         user_prompt += f"\n\nFix these issues from the previous draft:\n{issues}"

# #     response = client.chat.completions.create(
# #         model=MODEL,
# #         messages=[
# #             {"role": "system", "content": GENERATOR_SYSTEM},
# #             {"role": "user",   "content": user_prompt}
# #         ],
# #         temperature=0.7,
# #         max_tokens=1024,
# #     )

# #     raw = response.choices[0].message.content.strip()
# #     if "```" in raw:
# #         parts = raw.split("```")
# #         for p in parts:
# #             p = p.strip()
# #             if p.startswith("json"):
# #                 p = p[4:].strip()
# #             if p.startswith("{"):
# #                 raw = p
# #                 break
# #     return json.loads(raw)

# # REVIEWER_SYSTEM = """You are the Reviewer Agent in an educational content pipeline.
# # Your sole responsibility is to evaluate educational content for quality.

# # Evaluation criteria:
# # 1. Age appropriateness — Is the language right for the grade level?
# # 2. Conceptual correctness — Are all facts accurate?
# # 3. Clarity — Is the explanation easy to understand?
# # 4. MCQ quality — Are questions fair, clear, and testing the right concepts?

# # Rules:
# # - Be specific (e.g. "The word 'perpendicular' in sentence 2 is not defined")
# # - Only fail if there are real, meaningful problems
# # - You MUST respond with ONLY a valid raw JSON object
# # - Do NOT use markdown, code fences, or any text outside the JSON

# # Output format:
# # {
# #   "status": "pass",
# #   "feedback": []
# # }
# # OR
# # {
# #   "status": "fail",
# #   "feedback": ["Specific issue 1", "Specific issue 2"]
# # }"""


# # def reviewer_agent(grade: int, topic: str, content: dict) -> dict:
# #     """Reviewer Agent: evaluates Generator output, returns pass/fail + feedback."""
# #     user_prompt = (
# #         f"Review this educational content.\nGrade: {grade}\nTopic: {topic}\n\n"
# #         + json.dumps(content, indent=2)
# #     )

# #     response = client.chat.completions.create(
# #         model=MODEL,
# #         messages=[
# #             {"role": "system", "content": REVIEWER_SYSTEM},
# #             {"role": "user",   "content": user_prompt}
# #         ],
# #         temperature=0.3,
# #         max_tokens=512,
# #     )

# #     raw = response.choices[0].message.content.strip()
# #     if "```" in raw:
# #         parts = raw.split("```")
# #         for p in parts:
# #             p = p.strip()
# #             if p.startswith("json"):
# #                 p = p[4:].strip()
# #             if p.startswith("{"):
# #                 raw = p
# #                 break
# #     return json.loads(raw)


# # def run_pipeline(grade: int, topic: str) -> dict:
# #     """
# #     Full pipeline:
# #       1. Generator  →  draft content
# #       2. Reviewer   →  pass / fail + feedback
# #       3. Refiner    →  re-generate with feedback (ONE pass only, if failed)
# #     """
# #     result = {
# #         "input":          {"grade": grade, "topic": topic},
# #         "draft":          None,
# #         "review":         None,
# #         "refined":        None,
# #         "refined_needed": False,
# #     }

# #     result["draft"]  = generator_agent(grade, topic)
# #     result["review"] = reviewer_agent(grade, topic, result["draft"])

# #     if result["review"]["status"] == "fail":
# #         result["refined_needed"] = True
# #         result["refined"] = generator_agent(grade, topic, result["review"]["feedback"])

# #     return result

# # @app.route("/")
# # def index():
# #     return send_from_directory("static", "index.html")


# # @app.route("/api/run", methods=["POST"])
# # def api_run():
# #     data  = request.get_json()
# #     grade = int(data.get("grade", 4))
# #     topic = str(data.get("topic", "")).strip()

# #     if not topic:
# #         return jsonify({"error": "Topic is required"}), 400
# #     if not (1 <= grade <= 12):
# #         return jsonify({"error": "Grade must be 1–12"}), 400

# #     try:
# #         return jsonify(run_pipeline(grade, topic))
# #     except json.JSONDecodeError as e:
# #         return jsonify({"error": f"Model returned invalid JSON: {e}"}), 500
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500


# # if __name__ == "__main__":
# #     key = os.environ.get("GROQ_API_KEY", "")
# #     print("\n" + "="*55)
# #     print("  Eklavya AI Content Pipeline  (Groq — Free)")
# #     print("  http://localhost:5000")
# #     if not key or key == "YOUR_GROQ_API_KEY_HERE":
# #         print("\n  ⚠  Set your key:  export GROQ_API_KEY=gsk_...")
# #         print("  Get free key:    https://console.groq.com")
# #     print("="*55 + "\n")
# #     app.run(debug=True, port=5000)
# import os
# import json
# import re  # Added for robust JSON extraction
# from flask import Flask, request, jsonify, send_from_directory
# from groq import Groq
# from dotenv import load_dotenv

# app = Flask(__name__, static_folder="static")

# load_dotenv()

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# # Using the active reasoning model from Groq's catalog
# MODEL = "openai/gpt-oss-120b"


# GENERATOR_SYSTEM = """You are the Generator Agent in an educational content pipeline.
# Your sole responsibility is to generate draft educational content for a given grade level and topic.

# Rules:
# - Use simple language appropriate for the specified grade level
# - Keep explanations engaging and easy to understand
# - Ensure all facts are correct
# - Generate exactly 3 multiple choice questions
# - Each question must have exactly 4 options labelled A, B, C, D
# - The answer field must be ONLY a single letter: A, B, C, or D
# - You MUST respond with ONLY a valid raw JSON object
# - Do NOT use markdown, code fences, or any text outside the JSON

# Output format (copy this structure exactly):
# {
#   "explanation": "grade-appropriate explanation here",
#   "mcqs": [
#     {
#       "question": "question text here",
#       "options": ["A. option one", "B. option two", "C. option three", "D. option four"],
#       "answer": "A"
#     }
#   ]
# }"""

# REVIEWER_SYSTEM = """You are the Reviewer Agent in an educational content pipeline.
# Your sole responsibility is to evaluate educational content for quality.

# Evaluation criteria:
# 1. Age appropriateness — Is the language right for the grade level?
# 2. Conceptual correctness — Are all facts accurate?
# 3. Clarity — Is the explanation easy to understand?
# 4. MCQ quality — Are questions fair, clear, and testing the right concepts?

# Rules:
# - Be specific (e.g. "The word 'perpendicular' in sentence 2 is not defined")
# - Only fail if there are real, meaningful problems
# - You MUST respond with ONLY a valid raw JSON object
# - Do NOT use markdown, code fences, or any text outside the JSON

# Output format:
# {
#   "status": "pass",
#   "feedback": []
# }
# OR
# {
#   "status": "fail",
#   "feedback": ["Specific issue 1", "Specific issue 2"]
# }"""


# def extract_and_parse_json(raw_text: str) -> dict:
#     """Safely extracts JSON structures from model outputs, even if code blocks are present."""
#     raw_text = raw_text.strip()
#     # Regex to find the text between the first '{' and the last '}'
#     match = re.search(r'(\{.*})', raw_text, re.DOTALL)
#     if match:
#         return json.loads(match.group(1))
#     return json.loads(raw_text)


# # def generator_agent(grade: int, topic: str, feedback: list = None) -> dict:
# #     """Generator Agent: produces educational content. Embeds feedback if refining."""
# #     user_prompt = f"Generate educational content.\nGrade: {grade}\nTopic: {topic}"

# #     if feedback:
# #         issues = "\n".join(f"- {f}" for f in feedback)
# #         user_prompt += f"\n\nFix these issues from the previous draft:\n{issues}"

# #     response = client.chat.completions.create(
# #         model=MODEL,
# #         messages=[
# #             {"role": "system", "content": GENERATOR_SYSTEM},
# #             {"role": "user",   "content": user_prompt}
# #         ],
# #         temperature=0.7,
# #         max_tokens=1024,
# #         response_format={"type": "json_object"}  # Enforces Groq JSON Mode
# #     )

# #     return extract_and_parse_json(response.choices[0].message.content)
# def generator_agent(grade: int, topic: str, feedback: list = None, previous_draft: dict = None) -> dict:
#     """Generator Agent: produces educational content. 
#     Accepts previous draft and feedback to perform targeted corrections."""
    
#     if feedback and previous_draft:
#         # Contextual Refinement Prompt
#         user_prompt = (
#             f"You need to fix a previously failed draft.\n"
#             f"Grade: {grade}\n"
#             f"Topic: {topic}\n\n"
#             f"--- PREVIOUS DRAFT ---\n"
#             f"{json.dumps(previous_draft, indent=2)}\n\n"
#             f"--- ISSUES TO FIX ---\n"
#         )
#         user_prompt += "\n".join(f"- {f}" for f in feedback)
#         user_prompt += "\n\nRewrite the content, addressing every issue listed above while maintaining the required JSON structure."
#     else:
#         # Initial Draft Prompt
#         user_prompt = f"Generate educational content.\nGrade: {grade}\nTopic: {topic}"

#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {"role": "system", "content": GENERATOR_SYSTEM},
#             {"role": "user",   "content": user_prompt}
#         ],
#         temperature=0.7,
#         max_tokens=1024,
#         response_format={"type": "json_object"}
#     )

#     return extract_and_parse_json(response.choices.message.content)


# def run_pipeline(grade: int, topic: str) -> dict:
#     """
#     Improved Loop Pipeline:
#       1. Generates content.
#       2. Reviews content.
#       3. If failed, it enters a refinement loop (Up to 3 attempts).
#     """
#     pipeline_summary = {
#         "input": {"grade": grade, "topic": topic},
#         "iterations": [],
#         "final_status": "fail",
#         "final_content": None
#     }

#     max_attempts = 3
#     attempt = 0
#     current_draft = None
#     current_feedback = None

#     while attempt < max_attempts:
#         attempt += 1
        
#         # 1. Generate (or Refine if feedback exists)
#         current_content = generator_agent(grade, topic, feedback=current_feedback, previous_draft=current_draft)
        
#         # 2. Review
#         review_result = reviewer_agent(grade, topic, current_content)
        
#         # Store execution details for history tracking
#         pipeline_summary["iterations"].append({
#             "attempt": attempt,
#             "content": current_content,
#             "review": review_result
#         })

#         # 3. Evaluate Status
#         if review_result["status"] == "pass":
#             pipeline_summary["final_status"] = "pass"
#             pipeline_summary["final_content"] = current_content
#             break
#         else:
#             # Set up parameters for the next correction loop
#             current_draft = current_content
#             current_feedback = review_result["feedback"]

#     # Fallback if it never passes after max attempts
#     if pipeline_summary["final_status"] == "fail":
#         pipeline_summary["final_content"] = current_content

#     return pipeline_summary


# def reviewer_agent(grade: int, topic: str, content: dict) -> dict:
#     """Reviewer Agent: evaluates Generator output, returns pass/fail + feedback."""
#     user_prompt = (
#         f"Review this educational content.\nGrade: {grade}\nTopic: {topic}\n\n"
#         + json.dumps(content, indent=2)
#     )

#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {"role": "system", "content": REVIEWER_SYSTEM},
#             {"role": "user",   "content": user_prompt}
#         ],
#         temperature=0.3,
#         max_tokens=512,
#         response_format={"type": "json_object"}  # Enforces Groq JSON Mode
#     )

#     return extract_and_parse_json(response.choices[0].message.content)


# # def run_pipeline(grade: int, topic: str) -> dict:
# #     """
# #     Full pipeline:
# #       1. Generator  →  draft content
# #       2. Reviewer   →  pass / fail + feedback
# #       3. Refiner    →  re-generate with feedback (ONE pass only, if failed)
# #     """
# #     result = {
# #         "input":          {"grade": grade, "topic": topic},
# #         "draft":          None,
# #         "review":         None,
# #         "refined":        None,
# #         "refined_needed": False,
# #     }

# #     result["draft"]  = generator_agent(grade, topic)
# #     result["review"] = reviewer_agent(grade, topic, result["draft"])

# #     if result["review"]["status"] == "fail":
# #         result["refined_needed"] = True
# #         result["refined"] = generator_agent(grade, topic, result["review"]["feedback"])

# #     return result

# @app.route("/")
# def index():
#     return send_from_directory("static", "index.html")


# @app.route("/api/run", methods=["POST"])
# def api_run():
#     data  = request.get_json()
#     grade = int(data.get("grade", 4))
#     topic = str(data.get("topic", "")).strip()

#     if not topic:
#         return jsonify({"error": "Topic is required"}), 400
#     if not (1 <= grade <= 12):
#         return jsonify({"error": "Grade must be 1–12"}), 400

#     try:
#         return jsonify(run_pipeline(grade, topic))
#     except json.JSONDecodeError as e:
#         return jsonify({"error": f"Model returned invalid JSON structure: {e}"}), 500
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# if __name__ == "__main__":
#     key = os.environ.get("GROQ_API_KEY", "")
#     print("\n" + "="*55)
#     print("  Eklavya AI Content Pipeline  (Groq — Free)")
#     print("  http://localhost:5000")
#     if not key or key == "YOUR_GROQ_API_KEY_HERE":
#         print("\n  ⚠  Set your key:  export GROQ_API_KEY=gsk_...")
#         print("  Get free key:    https://console.groq.com")
#     print("="*55 + "\n")
#     app.run(debug=True, port=5000)


import os
import json
import re  
from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
from dotenv import load_dotenv

app = Flask(__name__, static_folder="static")

load_dotenv()

# Initialize the Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Asymmetric model scaling for maximum cost/speed efficiency on Groq
GENERATOR_MODEL = "openai/gpt-oss-20b"   # Fast drafting
REVIEWER_MODEL  = "openai/gpt-oss-120b"  # Deep, strict quality evaluation

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


def extract_and_parse_json(raw_text: str) -> dict:
    """Safely extracts JSON structures from model outputs, handling conversational text noise."""
    raw_text = raw_text.strip()
    match = re.search(r'(\{.*})', raw_text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    return json.loads(raw_text)


def generator_agent(grade: int, topic: str, feedback: list = None, previous_draft: dict = None) -> dict:
    """Produces educational content. Injects previous attempts to allow intelligent modifications."""
    if feedback and previous_draft:
        user_prompt = (
            f"CORRECTION REQUEST FOR A FAILED DRAFT:\n"
            f"Target Grade Level: {grade}\n"
            f"Target Subject: {topic}\n\n"
            f"Here is the bad draft that failed review:\n"
            f"{json.dumps(previous_draft, indent=2)}\n\n"
            f"Please regenerate this completely, making sure to fix these specific issues:\n"
        )
        user_prompt += "\n".join(f"- {f}" for f in feedback)
        user_prompt += "\n\nRewrite the content, fixing all listed issues while preserving a valid JSON layout."
    else:
        user_prompt = f"Generate new educational content.\nGrade Level: {grade}\nTopic: {topic}"

    response = client.chat.completions.create(
        model=GENERATOR_MODEL,
        messages=[
            {"role": "system", "content": GENERATOR_SYSTEM},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1024
    )
    return extract_and_parse_json(response.choices[0].message.content)


def reviewer_agent(grade: int, topic: str, content: dict) -> dict:
    """Reviewer Agent: evaluates Generator output, returns pass/fail + feedback."""
    user_prompt = (
        f"Review this educational content draft.\n"
        f"Target Grade: {grade}\n"
        f"Target Topic: {topic}\n\n"
        f"Draft Content to evaluate:\n"
        f"{json.dumps(content, indent=2)}"
    )

    response = client.chat.completions.create(
        model=REVIEWER_MODEL,
        messages=[
            {"role": "system", "content": REVIEWER_SYSTEM},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=0.1,  
        max_tokens=512
    )
    return extract_and_parse_json(response.choices[0].message.content)


def run_pipeline(grade: int, topic: str) -> dict:
    """Executes a loop-based refinement architecture with history compilation up to 3 tries."""
    pipeline_summary = {
        "input": {"grade": grade, "topic": topic},
        "iterations": [],
        "final_status": "fail",
        "final_content": None
    }

    max_attempts = 3
    attempt = 0
    current_draft = None
    current_feedback = None

    while attempt < max_attempts:
        attempt += 1
        
        current_content = generator_agent(grade, topic, feedback=current_feedback, previous_draft=current_draft)
        review_result = reviewer_agent(grade, topic, current_content)
        
        pipeline_summary["iterations"].append({
            "attempt": attempt,
            "content": current_content,
            "review": review_result
        })

        if review_result.get("status") == "pass":
            pipeline_summary["final_status"] = "pass"
            pipeline_summary["final_content"] = current_content
            break
        else:
            current_draft = current_content
            current_feedback = review_result.get("feedback", [])

    if pipeline_summary["final_status"] == "fail":
        pipeline_summary["final_content"] = current_content

    return pipeline_summary


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
        return jsonify({"error": f"Model returned invalid JSON structure: {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    key = os.environ.get("GROQ_API_KEY", "")
    print("\n" + "="*55)
   
    if not key or key == "YOUR_GROQ_API_KEY_HERE":
        print("\n  ⚠  Warning: Set your environment key: export GROQ_API_KEY=gsk_...")
    print("="*55 + "\n")
  
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )