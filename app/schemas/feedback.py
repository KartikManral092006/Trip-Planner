from typing import Literal

from pydantic import BaseModel, Field


FeedbackTarget = Literal["transport", "accommodation", "activities", "itinerary_only"]


class FeedbackRoute(BaseModel):
    target: FeedbackTarget = Field(
        description=(
            "Which part of the plan must change. 'transport', 'accommodation', or "
            "'activities' if new research is needed for that part; 'itinerary_only' "
            "if the existing research is enough and only the day plan must change."
        )
    )

    reason: str = Field(description="One short sentence explaining the choice.")
