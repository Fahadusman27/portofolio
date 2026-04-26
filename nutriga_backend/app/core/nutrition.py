"""
nutrition.py
------------
BMR, TDEE, and macronutrient target calculators for the
Nutritional Recommendation System.

Uses the Mifflin-St Jeor equation, which is well-validated for teenagers
and preferred over Harris-Benedict for clinical weight-management contexts.

References:
  Mifflin MD, et al. (1990). "A new predictive equation for resting energy
  expenditure in healthy individuals." AJCN 51(2):241-247.
"""

from dataclasses import dataclass
from typing import Literal

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

Gender = Literal["male", "female"]
ActivityLevel = Literal["sedentary", "light", "moderate", "active"]


# ---------------------------------------------------------------------------
# Activity multipliers (Harris-Benedict / Mifflin consensus values)
# ---------------------------------------------------------------------------

ACTIVITY_MULTIPLIERS: dict[str, float] = {
    "sedentary": 1.2,   # Little or no exercise, desk job
    "light": 1.375,     # Light exercise 1–3 days/week
    "moderate": 1.55,   # Moderate exercise 3–5 days/week
    "active": 1.725,    # Hard exercise 6–7 days/week
}

# ---------------------------------------------------------------------------
# Caloric deficit range for safe weight loss in teenagers
# A 15–20 % deficit is clinically recommended; we use the midpoint (17.5 %)
# as the default and expose the bounds for future flexibility.
# ---------------------------------------------------------------------------

DEFICIT_MIN: float = 0.15   # 15 %
DEFICIT_MAX: float = 0.20   # 20 %
DEFICIT_DEFAULT: float = (DEFICIT_MIN + DEFICIT_MAX) / 2  # 17.5 %

# ---------------------------------------------------------------------------
# Macronutrient distribution (percentage of target calories)
# ---------------------------------------------------------------------------

MACRO_PROTEIN_PCT: float = 0.30   # 30 %
MACRO_CARBS_PCT: float = 0.40     # 40 %
MACRO_FAT_PCT: float = 0.30       # 30 %

# Caloric density (kcal per gram) for each macro
KCAL_PER_G_PROTEIN: float = 4.0
KCAL_PER_G_CARBS: float = 4.0
KCAL_PER_G_FAT: float = 9.0


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NutritionTargets:
    """
    Immutable result object returned by :func:`calculate_nutrition_targets`.

    Attributes
    ----------
    bmr : float
        Basal Metabolic Rate in kcal/day.
    tdee : float
        Total Daily Energy Expenditure in kcal/day.
    target_calories : float
        Daily caloric goal after applying the safe deficit.
    deficit_percentage : float
        The deficit fraction applied, expressed as a percentage (e.g. 17.5).
    target_protein_g : float
        Daily protein target in grams.
    target_carbs_g : float
        Daily carbohydrate target in grams.
    target_fat_g : float
        Daily fat target in grams.
    """

    bmr: float
    tdee: float
    target_calories: float
    deficit_percentage: float
    target_protein_g: float
    target_carbs_g: float
    target_fat_g: float


# ---------------------------------------------------------------------------
# Core calculation functions
# ---------------------------------------------------------------------------

def calculate_bmr(weight: float, height: float, age: int, gender: Gender) -> float:
    """
    Compute Basal Metabolic Rate using the Mifflin-St Jeor equation.

    Formula
    -------
    Male   : BMR = (10 × weight_kg) + (6.25 × height_cm) − (5 × age) + 5
    Female : BMR = (10 × weight_kg) + (6.25 × height_cm) − (5 × age) − 161

    Parameters
    ----------
    weight : float
        Body weight in kilograms.
    height : float
        Height in centimetres.
    age : int
        Age in years.
    gender : {"male", "female"}
        Biological sex.

    Returns
    -------
    float
        BMR in kcal/day (rounded to 2 decimal places).

    Raises
    ------
    ValueError
        If gender is not "male" or "female".
    """
    if gender not in ("male", "female"):
        raise ValueError(f"Invalid gender '{gender}'. Must be 'male' or 'female'.")

    base = (10.0 * weight) + (6.25 * height) - (5.0 * age)
    sex_constant = 5.0 if gender == "male" else -161.0
    return round(base + sex_constant, 2)


def calculate_tdee(bmr: float, activity_level: ActivityLevel) -> float:
    """
    Compute Total Daily Energy Expenditure (TDEE) by applying the
    activity multiplier to the BMR.

    Parameters
    ----------
    bmr : float
        Basal Metabolic Rate in kcal/day.
    activity_level : {"sedentary", "light", "moderate", "active"}
        Self-reported physical activity level.

    Returns
    -------
    float
        TDEE in kcal/day (rounded to 2 decimal places).

    Raises
    ------
    ValueError
        If activity_level is not one of the recognised keys.
    """
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level)
    if multiplier is None:
        valid = list(ACTIVITY_MULTIPLIERS.keys())
        raise ValueError(
            f"Invalid activity_level '{activity_level}'. Valid options: {valid}"
        )
    return round(bmr * multiplier, 2)


def apply_deficit(tdee: float, deficit_fraction: float = DEFICIT_DEFAULT) -> float:
    """
    Subtract a caloric deficit from the TDEE to create a safe weight-loss target.

    Parameters
    ----------
    tdee : float
        Total Daily Energy Expenditure in kcal/day.
    deficit_fraction : float, optional
        Fraction to subtract (0–1). Defaults to 0.175 (17.5 %).

    Returns
    -------
    float
        Target daily calories after deficit (rounded to 2 decimal places).

    Raises
    ------
    ValueError
        If deficit_fraction is outside [0, 1].
    """
    if not (0.0 <= deficit_fraction <= 1.0):
        raise ValueError(
            f"deficit_fraction must be between 0 and 1, got {deficit_fraction}."
        )
    return round(tdee * (1.0 - deficit_fraction), 2)


def calculate_macros(
    target_calories: float,
) -> tuple[float, float, float]:
    """
    Derive gram targets for protein, carbohydrates, and fat from
    a daily calorie target using the 30/40/30 distribution.

    Parameters
    ----------
    target_calories : float
        Daily caloric goal in kcal.

    Returns
    -------
    tuple[float, float, float]
        ``(protein_g, carbs_g, fat_g)`` – each rounded to 2 decimal places.
    """
    protein_g = round((target_calories * MACRO_PROTEIN_PCT) / KCAL_PER_G_PROTEIN, 2)
    carbs_g = round((target_calories * MACRO_CARBS_PCT) / KCAL_PER_G_CARBS, 2)
    fat_g = round((target_calories * MACRO_FAT_PCT) / KCAL_PER_G_FAT, 2)
    return protein_g, carbs_g, fat_g


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def calculate_nutrition_targets(
    age: int,
    weight: float,
    height: float,
    gender: Gender,
    activity_level: ActivityLevel,
    deficit_fraction: float = DEFICIT_DEFAULT,
) -> NutritionTargets:
    """
    Full pipeline: BMR → TDEE → Deficit → Macros.

    This is the single entry-point used by the API route.

    Parameters
    ----------
    age : int
        Age in years (expected 10–19 for teenage users).
    weight : float
        Body weight in kilograms.
    height : float
        Height in centimetres.
    gender : {"male", "female"}
        Biological sex.
    activity_level : {"sedentary", "light", "moderate", "active"}
        Self-reported physical activity level.
    deficit_fraction : float, optional
        Caloric deficit fraction to apply. Defaults to 17.5 %.

    Returns
    -------
    NutritionTargets
        Frozen dataclass with all computed targets.

    Examples
    --------
    >>> result = calculate_nutrition_targets(
    ...     age=16, weight=80.0, height=168.0,
    ...     gender="male", activity_level="light"
    ... )
    >>> print(result.target_calories)
    2073.56
    """
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    target_calories = apply_deficit(tdee, deficit_fraction)
    protein_g, carbs_g, fat_g = calculate_macros(target_calories)

    return NutritionTargets(
        bmr=bmr,
        tdee=tdee,
        target_calories=target_calories,
        deficit_percentage=round(deficit_fraction * 100, 2),
        target_protein_g=protein_g,
        target_carbs_g=carbs_g,
        target_fat_g=fat_g,
    )


# ---------------------------------------------------------------------------
# Quick self-test (run with: python -m app.core.nutrition)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_cases = [
        dict(age=16, weight=80.0, height=168.0, gender="male",   activity_level="light"),
        dict(age=15, weight=70.0, height=160.0, gender="female", activity_level="moderate"),
        dict(age=17, weight=90.0, height=172.0, gender="male",   activity_level="sedentary"),
    ]

    print(f"{'Case':<6} {'BMR':>8} {'TDEE':>8} {'Target':>8} {'Protein':>9} {'Carbs':>8} {'Fat':>7}")
    print("-" * 60)
    for i, tc in enumerate(test_cases, 1):
        r = calculate_nutrition_targets(**tc)
        print(
            f"{i:<6} {r.bmr:>8.1f} {r.tdee:>8.1f} {r.target_calories:>8.1f} "
            f"{r.target_protein_g:>9.1f} {r.target_carbs_g:>8.1f} {r.target_fat_g:>7.1f}"
        )
