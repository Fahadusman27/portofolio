"""
genetic_algo.py
---------------
Genetic Algorithm (GA) implementation for daily meal plan optimisation.

Terminology
-----------
Gene        : A single food item dict from the TKPI dataset.
Chromosome  : A list of 4 genes → one daily meal plan
              (Breakfast, Lunch, Dinner, Snack).
Population  : A list of 50 chromosomes evolved over 100 generations.

Operators
---------
Selection   : Tournament selection (k=3)
Crossover   : Single-point crossover
Mutation    : Random gene replacement from the dataset
"""

import random
from dataclasses import dataclass, field
from typing import Sequence

from app.ai.fitness import evaluate_fitness, sum_chromosome, ChromosomeTotals
from app.dataset.dataset import FoodDataset
from app.core.nutrition import NutritionTargets

# ---------------------------------------------------------------------------
# GA hyper-parameters (tunable)
# ---------------------------------------------------------------------------

POPULATION_SIZE: int = 50
NUM_GENERATIONS: int = 100
TOURNAMENT_SIZE: int = 3         # candidates per tournament
CROSSOVER_RATE: float = 0.85     # probability of crossover
MUTATION_RATE: float = 0.20      # probability of mutating each gene
CHROMOSOME_LENGTH: int = 4       # genes per chromosome (meals per day)

MEAL_SLOTS: list[str] = ["Breakfast", "Lunch", "Dinner", "Snack"]


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class GAResult:
    """
    Return value of :meth:`GeneticAlgorithm.run`.

    Attributes
    ----------
    best_chromosome : list[dict]
        The fittest list of 4 food items found.
    best_fitness : float
        Fitness score of the best chromosome (lower = better).
    generations_run : int
        Number of generations executed.
    population_size : int
        Population size used.
    totals : ChromosomeTotals
        Aggregated nutritional values of the best chromosome.
    """
    best_chromosome: list[dict]
    best_fitness: float
    generations_run: int
    population_size: int
    totals: ChromosomeTotals


# ---------------------------------------------------------------------------
# GeneticAlgorithm class
# ---------------------------------------------------------------------------

class GeneticAlgorithm:
    """
    Evolves a population of meal-plan chromosomes to minimise the difference
    between the plan's total nutrition and the user's computed targets.

    Parameters
    ----------
    dataset : FoodDataset
        Loaded TKPI dataset used for gene sampling and mutation.
    targets : NutritionTargets
        Nutritional targets computed from the user's physical profile.
    population_size : int
        Number of chromosomes per generation.
    num_generations : int
        Number of evolution cycles.
    tournament_size : int
        Number of candidates drawn per tournament selection event.
    crossover_rate : float
        Probability (0–1) that two parents produce offspring via crossover.
    mutation_rate : float
        Probability (0–1) that each gene in an offspring is randomly replaced.
    """

    def __init__(
        self,
        dataset: FoodDataset,
        targets: NutritionTargets,
        population_size: int = POPULATION_SIZE,
        num_generations: int = NUM_GENERATIONS,
        tournament_size: int = TOURNAMENT_SIZE,
        crossover_rate: float = CROSSOVER_RATE,
        mutation_rate: float = MUTATION_RATE,
    ) -> None:
        self.dataset = dataset
        self.targets = targets
        self.population_size = population_size
        self.num_generations = num_generations
        self.tournament_size = tournament_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _random_chromosome(self) -> list[dict]:
        """Create one chromosome by sampling 4 random genes."""
        return self.dataset.random_sample(CHROMOSOME_LENGTH)

    def _initialise_population(self) -> list[list[dict]]:
        """Create the initial population of random chromosomes."""
        return [self._random_chromosome() for _ in range(self.population_size)]

    def _fitness(self, chromosome: list[dict]) -> float:
        """Shorthand: evaluate fitness against stored targets."""
        return evaluate_fitness(
            chromosome,
            target_calories=self.targets.target_calories,
            target_protein_g=self.targets.target_protein_g,
            target_carbs_g=self.targets.target_carbs_g,
            target_fat_g=self.targets.target_fat_g,
        )

    def _tournament_selection(self, population: list[list[dict]]) -> list[dict]:
        """
        Tournament selection: draw ``tournament_size`` candidates at random
        and return the one with the lowest (best) fitness score.
        """
        candidates = random.sample(population, min(self.tournament_size, len(population)))
        return min(candidates, key=self._fitness)

    def _crossover(
        self, parent_a: list[dict], parent_b: list[dict]
    ) -> tuple[list[dict], list[dict]]:
        """
        Single-point crossover.

        Randomly select a crossover point and swap gene tails between parents.
        Returns two offspring. If crossover doesn't trigger, clones are returned.
        """
        if random.random() > self.crossover_rate:
            return parent_a[:], parent_b[:]

        point = random.randint(1, CHROMOSOME_LENGTH - 1)
        child_a = parent_a[:point] + parent_b[point:]
        child_b = parent_b[:point] + parent_a[point:]
        return child_a, child_b

    def _mutate(self, chromosome: list[dict]) -> list[dict]:
        """
        Random mutation: for each gene, with probability ``mutation_rate``,
        replace it with a freshly sampled random food item.
        """
        return [
            self.dataset.random_food_item() if random.random() < self.mutation_rate else gene
            for gene in chromosome
        ]

    # ------------------------------------------------------------------
    # Main evolution loop
    # ------------------------------------------------------------------

    def run(self) -> GAResult:
        """
        Execute the Genetic Algorithm and return the best meal plan found.

        Returns
        -------
        GAResult
            Contains the best chromosome, its fitness score, and metadata.
        """
        population = self._initialise_population()

        best_chromosome = min(population, key=self._fitness)
        best_fitness = self._fitness(best_chromosome)

        for generation in range(self.num_generations):
            new_population: list[list[dict]] = []

            # Elitism: carry the current best into the next generation unchanged
            new_population.append(best_chromosome[:])

            # Fill the rest of the population with offspring
            while len(new_population) < self.population_size:
                parent_a = self._tournament_selection(population)
                parent_b = self._tournament_selection(population)

                child_a, child_b = self._crossover(parent_a, parent_b)
                child_a = self._mutate(child_a)
                child_b = self._mutate(child_b)

                new_population.append(child_a)
                if len(new_population) < self.population_size:
                    new_population.append(child_b)

            population = new_population

            # Track the global best across all generations
            gen_best = min(population, key=self._fitness)
            gen_best_fitness = self._fitness(gen_best)
            if gen_best_fitness < best_fitness:
                best_fitness = gen_best_fitness
                best_chromosome = gen_best[:]

        return GAResult(
            best_chromosome=best_chromosome,
            best_fitness=best_fitness,
            generations_run=self.num_generations,
            population_size=self.population_size,
            totals=sum_chromosome(best_chromosome),
        )
