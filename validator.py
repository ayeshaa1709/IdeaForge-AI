import requests
import json
import re


def validate_startup_idea(user_idea):

    prompt = f"""
You are IdeaForge AI, an expert startup consultant, venture capitalist, and business strategist.

Your task is to analyze startup ideas as if you were evaluating them for investment.

Evaluate the idea based on:

1. Overall Quality
2. Market Demand
3. Target Audience
4. Competition
5. Technical Difficulty
6. Revenue Potential
7. Scalability
8. Risks
9. MVP Feasibility
10. Long-Term Growth

IMPORTANT RULES

- Respond ONLY with valid JSON.
- Do NOT use markdown.
- Do NOT use ``` or ```json.
- Do NOT explain anything outside JSON.
- Return ONLY the JSON object.
- Score fields MUST be integers between 1 and 10.
- NEVER write "/10".
- NEVER write percentages.
- Be realistic. Not every startup deserves a high score.
- Give practical and professional feedback.
- Each text field should contain 2–4 sentences.

Return EXACTLY this JSON:

{{
    "idea_score": 0,
    "market_demand": 0,
    "target_audience": "",
    "competition": 0,
    "technical_difficulty": 0,
    "monetization": "",
    "strengths": "",
    "weaknesses": "",
    "mvp": "",
    "risks": "",
    "verdict": ""
}}

Scoring Guide

9-10 = Excellent startup with strong investment potential.

7-8 = Good startup with room for improvement.

5-6 = Average startup that needs refinement.

3-4 = Weak startup idea.

1-2 = Very poor startup idea.

Verdict Guide

9-10:
Excellent startup with strong investment potential.

7-8:
Promising idea with good market potential but needs refinement.

5-6:
Average startup idea. Improve differentiation and business strategy.

3-4:
Weak idea. Significant improvements are needed before launch.

1-2:
High-risk idea with very low chance of success.

Startup Idea:

{user_idea}
"""

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1",
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )

        response.raise_for_status()

        text = response.json()["response"].strip()

        # Remove markdown if the model accidentally adds it
        text = re.sub(r"```json", "", text)
        text = re.sub(r"```", "", text)
        text = text.strip()

        # Extract JSON only
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:
            text = match.group()

        data = json.loads(text)

        # Clean numeric score fields
        score_fields = [
            "idea_score",
            "market_demand",
            "competition",
            "technical_difficulty"
        ]

        for field in score_fields:

            value = str(data.get(field, "0")).strip()

            # Convert "8/10" → "8"
            if "/" in value:
                value = value.split("/")[0].strip()

            number = re.search(r"\d+", value)

            if number:
                value = int(number.group())
                value = max(1, min(10, value))
            else:
                value = 0

            data[field] = value

        # Ensure all keys exist
        defaults = {
            "idea_score": 0,
            "market_demand": 0,
            "target_audience": "Not provided.",
            "competition": 0,
            "technical_difficulty": 0,
            "monetization": "Not provided.",
            "strengths": "Not provided.",
            "weaknesses": "Not provided.",
            "mvp": "Not provided.",
            "risks": "Not provided.",
            "verdict": "No verdict."
        }

        for key, value in defaults.items():
            data.setdefault(key, value)

        return data

    except json.JSONDecodeError:

        return {
            "idea_score": 0,
            "market_demand": 0,
            "target_audience": "Unable to analyze.",
            "competition": 0,
            "technical_difficulty": 0,
            "monetization": "Unable to analyze.",
            "strengths": text if 'text' in locals() else "",
            "weaknesses": "The AI returned invalid JSON.",
            "mvp": "-",
            "risks": "-",
            "verdict": "AI returned an invalid response."
        }

    except requests.exceptions.RequestException as e:

        return {
            "idea_score": 0,
            "market_demand": 0,
            "target_audience": "Connection error.",
            "competition": 0,
            "technical_difficulty": 0,
            "monetization": "Connection error.",
            "strengths": "",
            "weaknesses": str(e),
            "mvp": "-",
            "risks": "-",
            "verdict": "Unable to connect to Ollama."
        }

    except Exception as e:

        return {
            "idea_score": 0,
            "market_demand": 0,
            "target_audience": "Unexpected error.",
            "competition": 0,
            "technical_difficulty": 0,
            "monetization": "Unexpected error.",
            "strengths": "",
            "weaknesses": str(e),
            "mvp": "-",
            "risks": "-",
            "verdict": "Unexpected server error."
        }