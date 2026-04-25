"""
routes.py
---------
API endpoints for the Nutritional Recommendation System.
POST /api/v1/recommend-diet  →  Full pipeline: profile → targets → GA → plan
"""

from fastapi import APIRouter, HTTPException

from app.models import (
    UserProfile,
    MealPlanResponse,
    NutritionalTargets,
    FoodItem,
    TotalMacros,
    GAMetadata,
)
from app.core.nutrition import calculate_nutrition_targets
from app.dataset.dataset import FoodDataset
from app.ai.genetic_algo import GeneticAlgorithm, MEAL_SLOTS

router = APIRouter(prefix="/api/v1", tags=["Diet Recommendation"])

# ---------------------------------------------------------------------------
# Lazy-load the dataset once at import time (shared across requests)
# ---------------------------------------------------------------------------

_dataset: FoodDataset | None = None


def get_dataset() -> FoodDataset:
    """Return the singleton FoodDataset, loading it on first call."""
    global _dataset
    if _dataset is None:
        _dataset = FoodDataset()
    return _dataset


# ---------------------------------------------------------------------------
# POST /api/v1/recommend-diet
# ---------------------------------------------------------------------------

@router.post(
    "/recommend-diet",
    response_model=MealPlanResponse,
    summary="Generate a personalised daily meal plan",
    description=(
        "Accepts a teenager's physical metrics, computes daily caloric and "
        "macronutrient targets via the Mifflin-St Jeor equation, then runs a "
        "Genetic Algorithm against the TKPI dataset to return an optimised "
        "4-meal daily plan (Breakfast, Lunch, Dinner, Snack)."
    ),
)
async def recommend_diet(profile: UserProfile) -> MealPlanResponse:
    """
    Full pipeline:
      1. Validate and parse the UserProfile.
      2. Compute nutritional targets (BMR → TDEE → Deficit → Macros).
      3. Load the TKPI dataset.
      4. Run the Genetic Algorithm.
      5. Return the best chromosome as a structured MealPlanResponse.
    """

    # ── Step 1: Compute nutritional targets ──────────────────────────────────
    try:
        targets = calculate_nutrition_targets(
            age=profile.age,
            weight=profile.weight,
            height=profile.height,
            gender=profile.gender,
            activity_level=profile.activity_level,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # ── Step 2: Load dataset ──────────────────────────────────────────────────
    try:
        dataset = get_dataset()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "TKPI dataset file not found. "
                "Please place 'tkpi_data.csv' inside 'app/dataset/'."
            ),
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"Dataset error: {exc}") from exc

    # ── Step 3: Run Genetic Algorithm ─────────────────────────────────────────
    try:
        ga = GeneticAlgorithm(dataset=dataset, targets=targets)
        result = ga.run()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"Genetic Algorithm error: {exc}"
        ) from exc

    # ── Step 4: Build response ────────────────────────────────────────────────

    nutritional_targets = NutritionalTargets(
        bmr=targets.bmr,
        tdee=targets.tdee,
        target_calories=targets.target_calories,
        deficit_percentage=targets.deficit_percentage,
        target_protein_g=targets.target_protein_g,
        target_carbs_g=targets.target_carbs_g,
        target_fat_g=targets.target_fat_g,
    )

    meal_plan = [
        FoodItem(
            meal_slot=MEAL_SLOTS[i],
            nama_bahan=str(food.get("Nama_Bahan", "Unknown")),
            porsi_g=float(food.get("Porsi_g", 0.0)),
            kalori_kal=float(food.get("Kalori_kal", 0.0)),
            karbohidrat_g=float(food.get("Karbohidrat_g", 0.0)),
            protein_g=float(food.get("Protein_g", 0.0)),
            lemak_g=float(food.get("Lemak_g", 0.0)),
            serat_g=float(food.get("Serat_g", 0.0)),
        )
        for i, food in enumerate(result.best_chromosome)
    ]

    total_macros = TotalMacros(
        total_calories=round(result.totals.calories, 2),
        total_protein_g=round(result.totals.protein_g, 2),
        total_carbs_g=round(result.totals.carbs_g, 2),
        total_fat_g=round(result.totals.fat_g, 2),
        total_fiber_g=round(result.totals.fiber_g, 2),
    )

    ga_metadata = GAMetadata(
        generations_run=result.generations_run,
        population_size=result.population_size,
        best_fitness_score=result.best_fitness,
    )

    return MealPlanResponse(
        user_profile=profile,
        nutritional_targets=nutritional_targets,
        meal_plan=meal_plan,
        total_macros=total_macros,
        ga_metadata=ga_metadata,
    )
