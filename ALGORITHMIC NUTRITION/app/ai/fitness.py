"""
fitness.py
----------
Fitness function evaluator for the Genetic Algorithm.

A chromosome is a list of 4 food-item dicts (Breakfast, Lunch, Dinner, Snack).
The fitness score represents the total weighted deviation from the user's
nutritional targets. **Lower score = better chromosome.**
"""

from dataclasses import dataclass
from typing import Sequence

# Weights for each nutritional dimension in the fitness sum.
# Calories carry the most weight because they are the primary constraint.
WEIGHT_CALORIES: float = 2.0
WEIGHT_PROTEIN: float = 1.5
WEIGHT_CARBS: float = 1.0
WEIGHT_FAT: float = 1.0

# Penalty multiplier applied when total calories EXCEED the target.
# Overages are penalised more harshly than underages to prevent
# the GA from converging on high-calorie meal plans.
EXCESS_CALORIE_PENALTY: float = 3.0


@dataclass(frozen=True)
class ChromosomeTotals:
    """Aggregated nutritional totals for one chromosome."""
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float


def sum_chromosome(chromosome: Sequence[dict]) -> ChromosomeTotals:
    """
    Sum the nutritional values across all food items in a chromosome.

    Parameters
    ----------
    chromosome : list[dict]
        4-item list of food-item dicts from the TKPI dataset.

    Returns
    -------
    ChromosomeTotals
        Frozen dataclass with aggregated values.
    """
    return ChromosomeTotals(
        calories=sum(item.get("Kalori_kal", 0.0)    for item in chromosome),
        protein_g=sum(item.get("Protein_g", 0.0)   for item in chromosome),
        carbs_g=sum(item.get("Karbohidrat_g", 0.0) for item in chromosome),
        fat_g=sum(item.get("Lemak_g", 0.0)          for item in chromosome),
        fiber_g=sum(item.get("Serat_g", 0.0)        for item in chromosome),
    )


def evaluate_fitness(
    chromosome: Sequence[dict],
    target_calories: float,
    target_protein_g: float,
    target_carbs_g: float,
    target_fat_g: float,
) -> float:
    """
    Compute the fitness score for a single chromosome.

    Formula
    -------
    score = Σ (weight_i × |actual_i − target_i|)
            + EXCESS_PENALTY × max(0, actual_calories − target_calories)

    A lower score means the meal plan is closer to the nutritional targets.

    Parameters
    ----------
    chromosome : list[dict]
        4-item list of food-item dicts.
    target_calories : float
        Daily caloric target (kcal).
    target_protein_g : float
        Daily protein target (g).
    target_carbs_g : float
        Daily carbohydrate target (g).
    target_fat_g : float
        Daily fat target (g).

    Returns
    -------
    float
        Fitness score (non-negative; lower = better).
    """
    totals = sum_chromosome(chromosome)

    # Base weighted absolute deviations
    score = (
        WEIGHT_CALORIES * abs(totals.calories  - target_calories)
        + WEIGHT_PROTEIN  * abs(totals.protein_g - target_protein_g)
        + WEIGHT_CARBS    * abs(totals.carbs_g   - target_carbs_g)
        + WEIGHT_FAT      * abs(totals.fat_g     - target_fat_g)
    )

    # Heavy penalty for exceeding caloric target (unsafe for weight loss)
    calorie_excess = max(0.0, totals.calories - target_calories)
    score += EXCESS_CALORIE_PENALTY * calorie_excess

    return round(score, 4)
