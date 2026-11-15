"""
UniOS — Assessment & Mastery Evaluation Prompt Builders (AI/ML KIE)
Provides structured, boundary-enforced prompts for:
  - Assessment Generation (POST /api/v1/kie/assessments/generate)
  - Mastery Evaluation & Delta Calculation (POST /api/v1/kie/mastery/evaluate)
"""

import json
from app.schemas.assessment import AssessmentGenerateRequest, MasteryEvaluateRequest


def build_assessment_generation_prompt(request: AssessmentGenerateRequest) -> str:
    """Builds a schema-constrained prompt for synthesizing assessment questions with answer keys."""
    q_type = request.preferred_type or "mcq"
    q_count = request.question_count or 5
    difficulty = request.difficulty or "PROFICIENT"

    return f"""You are the UniOS Assessment Generation Engine (AI/ML-2 KIE).
Synthesize a comprehensive, curriculum-aligned assessment tailored to the following specifications:

### Target Specifications:
- Topic: {request.topic}
- Session ID: {request.session_id or 'N/A'}
- Lesson ID: {request.lesson_id or 'N/A'}
- Learner ID: {request.learner_id}
- Preferred Question Type: {q_type}
- Question Count: {q_count}
- Target Difficulty: {difficulty}

### AI Implementation Rules:
1. STRICT TOPIC & DISCIPLINE GROUNDING:
   - Every single question, choice option, and explanation MUST be authentically and strictly grounded in '{request.topic}' and its discipline.
   - Under NO circumstances generate generic Computer Science or Database questions (e.g. 'Storage Manager & Buffer Pool', 'Query Compiler & Parser', 'SQL', 'Buffer paging') unless the topic itself is Computer Science, Database Management, or Software Engineering!
   - For Entrepreneurship & Business topics (e.g. 'ENTREPRENEURSHIP DEVELOPMENT', 'Business Management'): assess venture creation, business models, bootstrapping vs venture capital, market validation, MVP, customer discovery, unit economics, and risk mitigation.
   - For Commerce & Finance topics: assess balance sheets, ledger entries, accounting standards, financial ratios, fiscal policy, and cash flow.
   - For Law & Governance topics: assess statutes, constitutional provisions, legal doctrines, judicial precedent, and regulatory compliance.
   - For Science & Engineering topics: assess domain-specific theories, formulas, experimental methodology, and technical problem-solving.
2. DIVERSITY & DEDUPLICATION:
   - Every question must test a distinctly different concept. Do not generate repetitive or paraphrased variants of the same question.
3. ALWAYS PROVIDE ANSWER KEYS / RUBRICS:
   - For 'mcq': Each question must have 'options' with stable IDs ('opt-1', 'opt-2', 'opt-3', 'opt-4') and a 'correct_option_id' matching one of the options, plus an 'explanation'.
   - For 'coding': Provide initial starter 'code', 'language' (e.g. 'python', 'sql', 'javascript'), and 'rubric' containing 'required_clauses' and 'ideal_solution'.
   - For 'subjective' / 'viva' / 'case-study': Provide 'rubric' with 'ideal_solution' and 'criteria'.
4. STABLE IDENTIFIERS:
   - Use stable IDs for questions: 'q1', 'q2', 'q3', etc.
   - Use stable IDs for options: 'opt-1', 'opt-2', 'opt-3', 'opt-4'.
5. SCORING & RUBRIC:
   - 'rubric' object must contain 'total_points' (float/number) and 'passing_threshold' (e.g. 0.70).
6. OUTPUT FORMAT:
   - Output strictly valid JSON. No conversational preamble, markdown backticks, or trailing notes. Respond with valid JSON.

### Expected JSON Schema:
{{
  "title": "{request.topic} Assessment",
  "type": "{q_type}",
  "instructions": "Answer all questions to test your understanding.",
  "questions": [
    {{
      "id": "q1",
      "type": "mcq",
      "question": "Question text here...",
      "options": [
        {{ "id": "opt-1", "text": "Option A" }},
        {{ "id": "opt-2", "text": "Option B" }},
        {{ "id": "opt-3", "text": "Option C" }},
        {{ "id": "opt-4", "text": "Option D" }}
      ],
      "correct_option_id": "opt-1",
      "explanation": "Detailed explanation why opt-1 is correct."
    }}
  ],
  "rubric": {{
    "total_points": {float(q_count)},
    "passing_threshold": 0.70
  }}
}}
"""


def build_mastery_evaluation_prompt(request: MasteryEvaluateRequest) -> str:
    """Builds a prompt for evaluating submitted assessment answers and computing mastery deltas."""
    answers_formatted = []
    for a in request.answers:
        answers_formatted.append({
            "question_id": a.question_id,
            "answer": a.answer,
            "hints_used": a.hints_used,
            "time_spent_seconds": a.time_spent_seconds,
        })

    return f"""You are the UniOS Mastery Evaluation Engine (AI/ML-2 KIE).
Evaluate the learner's submitted assessment answers, compute normalized scoring, and determine hierarchical mastery graph updates.

### Assessment Submission Details:
- Learner ID: {request.learner_id}
- Assessment ID: {request.assessment_id or 'N/A'}
- Topic: {request.topic}
- Total Time Spent: {request.total_time_spent_seconds} seconds
- Submitted Answers:
{json.dumps(answers_formatted, indent=2)}

### Evaluation Guidelines & Invariants:
1. Normalized Score: Return an overall 'score' as a float between 0.0 and 1.0.
2. Question Evaluations:
   - For each submitted question answer, return:
     * 'question_id': matching the submitted ID.
     * 'is_correct': boolean.
     * 'score': float between 0.0 and 1.0.
     * 'feedback': constructive qualitative feedback highlighting correctness or misconceptions.
3. Hierarchical Mastery Updates:
   - Must strictly follow the structure:
     "mastery_updates": {{
       "<Subject>": {{
         "<Topic or Sub-skill>": {{
           "score": float (0.0 to 1.0),
           "status": "NOVICE" | "DEVELOPING" | "PROFICIENT" | "MASTERED",
           "delta": float (e.g. +0.15 or -0.05),
           "reason": "Specific reason for the score adjustment"
         }}
       }}
     }}
4. Actionable Overall Feedback:
   - Provide encouragement, validate effort, and specify targeted next steps.
5. Output strictly valid JSON matching this schema:
{{
  "score": 0.85,
  "feedback": "Actionable overall feedback on the learner's performance.",
  "question_evaluations": [
    {{
      "question_id": "q1",
      "is_correct": true,
      "score": 1.0,
      "feedback": "Correct reasoning on BST complexity."
    }}
  ],
  "mastery_updates": {{
    "{request.topic}": {{
      "Core Concepts": {{
        "score": 0.85,
        "status": "PROFICIENT",
        "delta": 0.15,
        "reason": "Demonstrated solid understanding."
      }}
    }}
  }}
}}
"""
