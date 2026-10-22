from typing import Literal

from pydantic import BaseModel, Field, model_validator


CostCategory = Literal["transport", "accommodation", "activities", "food", "other"]


class CostItem(BaseModel):
    name: str = Field(
        description="What the cost is for, e.g. 'Dehradun to Goa train, 3AC'."
    )

    category: CostCategory = Field(
        description="Which budget category this cost belongs to."
    )

    amount: float = Field(
        ge=0,
        description="Price of ONE unit in the trip currency, e.g. one night or one ticket.",
    )

    quantity: int = Field(
        default=1,
        ge=1,
        description=(
            "How many units are paid for, e.g. 3 for three hotel nights. "
            "Do not multiply by the number of travelers here."
        ),
    )

    per_person: bool = Field(
        description=(
            "True if the price is charged per traveler (e.g. a train ticket). "
            "False if charged per room or per group (e.g. a hotel room)."
        )
    )

    source_url: str | None = Field(
        default=None,
        description="URL of the page where this price was found. Null if there is no source.",
    )

    is_estimate: bool = Field(
        description="True if the price is an estimate, not taken directly from the source."
    )

    duration_hours: float | None = Field(
        default=None,
        description="For transport only: journey time in hours. Null if unknown or not transport.",
    )

    @model_validator(mode="after")
    def no_source_means_estimate(self):
        # A price without a source can never count as verified.
        if not self.source_url:
            self.is_estimate = True
        return self


class ResearchResult(BaseModel):
    summary: str = Field(
        description="Short, readable summary of the findings and the options compared."
    )

    items: list[CostItem] = Field(
        description="Cost items for the ONE recommended plan. These are added to the budget."
    )

    alternatives: list[CostItem] = Field(
        default_factory=list,
        description=(
            "Other options worth considering, e.g. a cheaper hotel or a train "
            "instead of a flight. These are NOT added to the budget."
        ),
    )