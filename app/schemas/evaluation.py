from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    approved: bool = Field(
        description="True only if the itinerary fits the traveler's preferences and is realistic."
    )

    feedback: str = Field(
        description="Specific problems and how to fix them. Empty if approved."
    )
