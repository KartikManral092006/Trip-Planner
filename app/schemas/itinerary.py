from pydantic import BaseModel, Field


class DayPlan(BaseModel):
    day: int = Field(description="Day number, starting at 1.")

    date: str = Field(description="Date in YYYY-MM-DD format.")

    location: str = Field(
        description="Where the travelers are, e.g. 'Goa' or 'On the train to Goa'."
    )

    is_travel_day: bool = Field(
        description="True if most of this day is spent travelling between cities."
    )

    activities: list[str] = Field(
        description="Short activity descriptions for this day, under 15 words each."
    )

    stay: str | None = Field(
        default=None,
        description=(
            "Where the travelers sleep tonight. Null if they are on an overnight "
            "train or flight, or it is the last day."
        ),
    )


class Itinerary(BaseModel):
    title: str = Field(description="Short title for the trip.")

    days: list[DayPlan] = Field(description="One entry per trip day, in date order.")

    warnings: list[str] = Field(
        description="Problems the traveler must know about, e.g. over budget or long journeys."
    )

    suggestions: list[str] = Field(
        description="Practical ways to fix the warnings, e.g. cheaper or faster options."
    )
