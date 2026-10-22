from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    transport_tasks: list[str] = Field(
        description=(
            "2 to 4 research tasks for the transport agent. Cover the "
            "outbound journey from the departure city and the return "
            "journey, using only the traveler's preferred transport modes."
        )
    )

    accommodation_tasks: list[str] = Field(
        description=(
            "2 to 4 research tasks for the accommodation agent, matching "
            "the accommodation type, every night of the stay, the number "
            "of guests, and the budget."
        )
    )

    activities_tasks: list[str] = Field(
        description=(
            "2 to 4 research tasks for the activities agent, matching the "
            "interests, pace, food preference, and special requirements."
        )
    )