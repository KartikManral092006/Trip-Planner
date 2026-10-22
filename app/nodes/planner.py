from app.llm import llm
from app.prompts.planner_prompt import PLANNER_PROMPT
from app.prompts.trip_details import format_trip_details
from app.schemas.research_plan import ResearchPlan
from app.state import TravelState


structured_llm = llm.with_structured_output(ResearchPlan)


def planner(state: TravelState) -> dict:
    plan = structured_llm.invoke([
        ("system", PLANNER_PROMPT),
        ("human", format_trip_details(state)),
    ])

    if plan is None:
        raise RuntimeError("Planner returned no research plan.")

    return {"research_plan": plan.model_dump()}