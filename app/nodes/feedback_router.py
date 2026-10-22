from app.llm import llm
from app.prompts.feedback_prompt import FEEDBACK_PROMPT
from app.schemas.feedback import FeedbackRoute
from app.state import TravelState


structured_llm = llm.with_structured_output(FeedbackRoute)


def feedback_router(state: TravelState) -> dict:
    route = structured_llm.invoke([
        ("system", FEEDBACK_PROMPT),
        ("human", f"Traveler feedback: {state['human_feedback']}"),
    ])

    target = route.target if route else "itinerary_only"

    return {
        "feedback_target": target,
        "retry_count": 0,
        "approved": False,
    }
