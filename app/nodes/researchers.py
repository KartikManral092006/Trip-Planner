import logging

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

from app.llm import llm
from app.prompts.researcher_prompts import (
    ACCOMMODATION_PROMPT,
    ACTIVITIES_PROMPT,
    TRANSPORT_PROMPT,
)
from app.prompts.trip_details import format_trip_details
from app.schemas.cost import ResearchResult
from app.state import TravelState
from app.tools.web_search import web_search


logger = logging.getLogger(__name__)


def make_agent(system_prompt: str):
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt=system_prompt,
        response_format=ToolStrategy(ResearchResult),
    )


transport_agent = make_agent(TRANSPORT_PROMPT)
accommodation_agent = make_agent(ACCOMMODATION_PROMPT)
activities_agent = make_agent(ACTIVITIES_PROMPT)


def run_research(agent, state: TravelState, tasks: list[str], previous: dict | None = None) -> dict:
    task_text = "\n".join(f"- {task}" for task in tasks)

    request = f"""
TRIP DETAILS:
{format_trip_details(state)}

RESEARCH TASKS:
{task_text}
"""

    if state["human_feedback"]:
        request += f"""
TRAVELER FEEDBACK ON THE PREVIOUS PLAN (address this first):
{state['human_feedback']}
"""

    try:
        response = agent.invoke({"messages": [{"role": "user", "content": request}]})
        result = response["structured_response"]
    except Exception as error:
        logger.exception("Research agent failed")
        if previous:
            return {
                **previous,
                "summary": f"{previous['summary']}\n\nUpdate failed ({error}). "
                "This is the previous research.",
            }
        result = ResearchResult(
            summary=f"Research failed ({error}). This information is unavailable.",
            items=[],
        )

    return result.model_dump()


def transport_researcher(state: TravelState) -> dict:
    tasks = state["research_plan"]["transport_tasks"]
    return {"transport_research": run_research(transport_agent, state, tasks, state["transport_research"])}


def accommodation_researcher(state: TravelState) -> dict:
    tasks = state["research_plan"]["accommodation_tasks"]
    return {"accommodation_research": run_research(accommodation_agent, state, tasks, state["accommodation_research"])}


def activities_researcher(state: TravelState) -> dict:
    tasks = state["research_plan"]["activities_tasks"]
    return {"activities_research": run_research(activities_agent, state, tasks, state["activities_research"])}