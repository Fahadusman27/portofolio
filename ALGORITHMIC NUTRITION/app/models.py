"""
models.py
---------
Pydantic schemas for the Nutritional Recommendation System API.
Defines request (UserProfile) and response (MealPlan) data contracts.
"""

from typing import Literal, List
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums / Literal types
# ---------------------------------------------------------------------------

ActivityLevel = Literal["sedentary", "light", "moderate", "active"]
Gender = Literal["male", "female"]


# ---------------------------------------------------------------------------
# Request Schema
# ---------------------------------------------------------------------------

class UserProfile(BaseModel):
    """
    Physical metrics submitted by the user.
    Used to compute BMR, TDEE, and target macros before running the GA.
    """

    age: int = Field(
        ...,
        ge=10,
        le=19,
        description="Age of the teenager in years (10–19).",
        examples=[15],
    )
    weight: float = Field(
        ...,
        gt=0,
        description="Body weight in kilograms.",
        examples=[75.0],
    )
    height: float = Field(
        ...,
        gt=0,
        description="Height in centimetres.",
        examples=[165.0],
    )
    gender: Gender = Field(
        ...,
        description="Biological sex: 'male' or 'female'.",
        examples=["male"],
    )
    activity_level: ActivityLevel = Field(
        ...,
        description=(
            "Physical activity level:\n"
            "  - sedentary  : little or no exercise\n"
            "  - light      : light exercise 1–3 days/week\n"
            "  - moderate   : moderate exercise 3–5 days/week\n"
            "  - active     : hard exercise 6–7 days/week"
        ),
        examples=["light"],
    )

    @field_validator("weight")
    @classmethod
    def weight_reasonable(cls, v: float) -> float:
        if v < 20 or v > 300:
            raise ValueError("Weight must be between 20 kg and 300 kg.")
        return v

    @field_validator("height")
    @classmethod
    def height_reasonable(cls, v: float) -> float:
        if v < 100 or v > 250:
            raise ValueError("Height must be between 100 cm and 250 cm.")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "age": 16,
                "weight": 80.0,
                "height": 168.0,
                "gender": "male",
                "activity_level": "light",
            }
        }
    }


# ---------------------------------------------------------------------------
# Nested response schemas
# ---------------------------------------------------------------------------

class NutritionalTargets(BaseModel):
    """Computed daily nutritional targets for the user."""

    bmr: float = Field(..., description="Basal Metabolic Rate (kcal/day).")
    tdee: float = Field(..., description="Total Daily Energy Expenditure (kcal/day).")
    target_calories: float = Field(
        ..., description="Target calories after applying caloric deficit (kcal/day)."
    )
    deficit_percentage: float = Field(
        ..., description="Caloric deficit percentage applied (e.g. 17.5 means 17.5 %)."
    )
    target_protein_g: float = Field(..., description="Target protein in grams.")
    target_carbs_g: float = Field(..., description="Target carbohydrates in grams.")
    target_fat_g: float = Field(..., description="Target fat in grams.")


class FoodItem(BaseModel):
    """A single food item from the TKPI dataset (one gene in the GA chromosome)."""

    meal_slot: str = Field(
        ...,
        description="Meal slot this item fills: Breakfast, Lunch, Dinner, or Snack.",
    )
    nama_bahan: str = Field(..., description="Name of the food ingredient (Nama_Bahan).")
    porsi_g: float = Field(..., description="Serving size in grams.")
    kalori_kal: float = Field(..., description="Calories (kcal).")
    karbohidrat_g: float = Field(..., description="Carbohydrates in grams.")
    protein_g: float = Field(..., description="Protein in grams.")
    lemak_g: float = Field(..., description="Fat in grams.")
    serat_g: float = Field(..., description="Dietary fibre in grams.")


class TotalMacros(BaseModel):
    """Aggregate nutritional totals for the recommended meal plan."""

    total_calories: float = Field(..., description="Sum of calories across all meals.")
    total_protein_g: float = Field(..., description="Sum of protein across all meals.")
    total_carbs_g: float = Field(..., description="Sum of carbohydrates across all meals.")
    total_fat_g: float = Field(..., description="Sum of fat across all meals.")
    total_fiber_g: float = Field(..., description="Sum of dietary fibre across all meals.")


class GAMetadata(BaseModel):
    """Diagnostic information from the Genetic Algorithm run."""

    generations_run: int = Field(..., description="Number of generations executed.")
    population_size: int = Field(..., description="Population size used.")
    best_fitness_score: float = Field(
        ...,
        description=(
            "Best fitness score achieved (lower = better; "
            "represents the total weighted deviation from targets)."
        ),
    )


# ---------------------------------------------------------------------------
# Top-level Response Schema
# ---------------------------------------------------------------------------

class MealPlanResponse(BaseModel):
    """
    Full API response for the /recommend-diet endpoint.
    Contains computed targets, the recommended meal plan, and GA metadata.
    """

    user_profile: UserProfile = Field(..., description="Echoed input profile.")
    nutritional_targets: NutritionalTargets = Field(
        ..., description="Calculated daily nutritional targets."
    )
    meal_plan: List[FoodItem] = Field(
        ...,
        description="List of 4 recommended food items (Breakfast, Lunch, Dinner, Snack).",
    )
    total_macros: TotalMacros = Field(
        ..., description="Aggregated nutritional values of the meal plan."
    )
    ga_metadata: GAMetadata = Field(
        ..., description="Diagnostic information from the GA run."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_profile": {
                    "age": 16,
                    "weight": 80.0,
                    "height": 168.0,
                    "gender": "male",
                    "activity_level": "light",
                },
                "nutritional_targets": {
                    "bmr": 1825.4,
                    "tdee": 2513.0,
                    "target_calories": 2075.0,
                    "deficit_percentage": 17.5,
                    "target_protein_g": 155.6,
                    "target_carbs_g": 207.5,
                    "target_fat_g": 69.2,
                },
                "meal_plan": [
                    {
                        "meal_slot": "Breakfast",
                        "nama_bahan": "Nasi Putih",
                        "porsi_g": 100.0,
                        "kalori_kal": 175.0,
                        "karbohidrat_g": 40.0,
                        "protein_g": 3.0,
                        "lemak_g": 0.5,
                        "serat_g": 0.2,
                    }
                ],
                "total_macros": {
                    "total_calories": 2060.0,
                    "total_protein_g": 152.0,
                    "total_carbs_g": 200.0,
                    "total_fat_g": 68.0,
                    "total_fiber_g": 12.0,
                },
                "ga_metadata": {
                    "generations_run": 100,
                    "population_size": 50,
                    "best_fitness_score": 14.7,
                },
            }
        }
    }
