from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.state import AccommodationType, FoodPreference, Pace


MAX_TRIP_DAYS = 14

TransportMode = Literal["train", "flight", "bus", "car"]


class TripRequest(BaseModel):
    origin: str = Field(min_length=2, max_length=100)
    destination: str = Field(min_length=2, max_length=100)
    start_date: date
    end_date: date
    budget: float = Field(gt=0, le=10_000_000)
    travelers: int = Field(ge=1, le=20)
    interests: list[str] = Field(min_length=1, max_length=10)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    accommodation_type: AccommodationType = "any"
    transport_preference: list[TransportMode] = Field(min_length=1)
    food_preference: FoodPreference = "no preference"
    pace: Pace = "moderate"
    special_requirements: str = Field(default="", max_length=500)

    @field_validator("origin", "destination", "special_requirements")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("currency")
    @classmethod
    def upper_currency(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("interests")
    @classmethod
    def clean_interests(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values if value.strip()]
        if not cleaned:
            raise ValueError("Add at least one interest.")
        return list(dict.fromkeys(cleaned))

    @field_validator("transport_preference")
    @classmethod
    def unique_modes(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))

    @model_validator(mode="after")
    def check_trip(self):
        if self.origin.casefold() == self.destination.casefold():
            raise ValueError("Origin and destination must be different.")
        if self.start_date < date.today():
            raise ValueError("Start date cannot be in the past.")
        if self.end_date < self.start_date:
            raise ValueError("End date must be on or after the start date.")
        if (self.end_date - self.start_date).days + 1 > MAX_TRIP_DAYS:
            raise ValueError(f"Trips can be at most {MAX_TRIP_DAYS} days long.")
        return self

    def to_trip(self) -> dict:
        trip = self.model_dump()
        trip["start_date"] = self.start_date.isoformat()
        trip["end_date"] = self.end_date.isoformat()
        return trip


class ApprovalRequest(BaseModel):
    approved: bool
    feedback: str = Field(default="", max_length=1000)
