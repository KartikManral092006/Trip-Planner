import json

from app.llm import llm
from app.prompts.evaluator_prompt import EVALUATOR_PROMPT
from app.prompts.trip_details import format_trip_details
from app.schemas.evaluation import EvaluationResult
from app.state import TravelState


structured_llm = llm.with_structured_output(EvaluationResult)


def llm_evaluator(state: TravelState) -> dict:
    request = f"""
TRIP DETAILS:
{format_trip_details(state)}

ITINERARY:
{json.dumps(state['itinerary'], indent=1)}
"""

    result = structured_llm.invoke([
        ("system", EVALUATOR_PROMPT),
        ("human", request),
    ])

    if result is None:
        raise RuntimeError("Evaluator returned no result.")

    return {
        "approved": result.approved,
        "evaluation_feedback": result.feedback,
    }
