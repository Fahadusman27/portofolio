"""
data/dataset.py
Handles loading, cleaning, categorisation, and sampling of the TKPI food dataset.

CSV columns expected
--------------------
No              : int    – original row index
Nama_Bahan      : str    – food name (Indonesian)
Porsi_g         : int    – serving size in grams (default 100 g)
Kalori_kal      : float  – calories (kcal per serving)
Karbohidrat_g   : float  – carbohydrates (g)
Protein_g       : float  – protein (g)
Lemak_g         : float  – fat (g)
Serat_g         : float  – dietary fibre (g)
"""
from __future__ import annotations

import logging
import random
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

import pandas as pd
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Path resolution
# ─────────────────────────────────────────────

_HERE = Path(__file__).resolve()                          # …/app/data/dataset.py
_PROJECT_ROOT = _HERE.parent.parent.parent                # …/skripsi/
DEFAULT_CSV_PATH = _PROJECT_ROOT / "dataset" / "tkpi_data.csv"


# ─────────────────────────────────────────────
# Pydantic schema for a single food item
# ─────────────────────────────────────────────

class FoodRecord(BaseModel):
    """
    Represents one food item from the TKPI dataset.
    All nutritional values are per-serving (default: 100 g).
    """
    id:          int    = Field(..., description="Original row number from the dataset (No column).")
    name:        str    = Field(..., description="Food name in Indonesian (Nama_Bahan).")
    serving_g:   int    = Field(..., description="Serving size in grams (Porsi_g).")
    calories:    float  = Field(..., description="Calories in kcal (Kalori_kal).")
    carbs:       float  = Field(..., description="Carbohydrates in grams (Karbohidrat_g).")
    protein:     float  = Field(..., description="Protein in grams (Protein_g).")
    fats:        float  = Field(..., description="Fat in grams (Lemak_g).")
    fiber:       float  = Field(..., description="Dietary fibre in grams (Serat_g).")
    category:    str    = Field(..., description="Inferred nutritional category (see CATEGORY_RULES).")
    meal_tag:    str    = Field(..., description="Suggested meal slot: breakfast / lunch / dinner / snack.")

    def to_api_dict(self) -> dict:
        """Lightweight dict for embedding in MealPlan API responses."""
        return {
            "id":       self.id,
            "name":     self.name,
            "category": self.category,
            "calories": self.calories,
            "protein":  self.protein,
            "carbs":    self.carbs,
            "fats":     self.fats,
        }


# ─────────────────────────────────────────────
# Keyword-based categorisation rules
# ─────────────────────────────────────────────
# Each entry: (category_label, meal_tag, [keywords_that_trigger_it])
# Rules are evaluated in ORDER – first match wins.
# All keywords are matched case-insensitively against Nama_Bahan.

_CATEGORY_RULES: list[tuple[str, str, list[str]]] = [
    # ── Proteins ──────────────────────────────────────────────────────────────
    ("protein",     "lunch",     ["ayam", "daging", "sapi", "kambing", "bebek", "kalkun",
                                   "ikan", "udang", "cumi", "kepiting", "kerang", "tuna",
                                   "salmon", "lele", "gurame", "mujair", "bandeng", "cakalang",
                                   "telur", "tempe", "tahu", "kacang kedelai", "edamame"]),

    # ── Complex Carbohydrates ──────────────────────────────────────────────────
    ("carbohydrate", "lunch",    ["nasi", "beras", "bihun", "mi ", "mie ", "makaroni",
                                   "kentang", "singkong", "ubi", "talas", "jagung",
                                   "ketan", "roti", "sagu", "tepung", "oat", "havermut",
                                   "pasta", "misoa", "kwetiau", "cereal"]),

    # ── Vegetables ────────────────────────────────────────────────────────────
    ("vegetable",   "lunch",    ["bayam", "kangkung", "sawi", "brokoli", "wortel",
                                   "tomat", "labu", "terong", "buncis", "kacang panjang",
                                   "timun", "mentimun", "kubis", "kol", "selada",
                                   "daun", "lobak", "pare", "gambas", "oyong",
                                   "rebung", "pakis", "genjer", "pepaya muda"]),

    # ── Fruits ────────────────────────────────────────────────────────────────
    ("fruit",       "snack",    ["apel", "pisang", "jeruk", "mangga", "pepaya", "semangka",
                                   "melon", "nanas", "anggur", "strawberry", "jambu",
                                   "rambutan", "durian", "salak", "alpukat", "kiwi",
                                   "pir", "buah", "leci", "markisa", "nangka"]),

    # ── Dairy & Eggs ──────────────────────────────────────────────────────────
    ("dairy",       "breakfast", ["susu", "keju", "yogurt", "yoghurt", "kefir",
                                   "mentega", "butter", "krim", "cream", "keju"]),

    # ── Breakfast foods & Snacks ──────────────────────────────────────────────
    ("snack",       "snack",    ["biskuit", "kue", "roti tawar", "cereal", "granola",
                                   "pudding", "puding", "jelly", "agar", "kolak",
                                   "onde", "klepon", "lemper", "nagasari",
                                   "kerupuk", "keripik", "crackers", "permen",
                                   "cokelat", "coklat", "es krim", "ice cream"]),

    # ── Legumes & Nuts ────────────────────────────────────────────────────────
    ("legume",      "snack",    ["kacang", "almond", "mete", "kenari", "kedelai",
                                   "lentil", "chickpea", "polong", "buncis mentah"]),

    # ── Beverages ─────────────────────────────────────────────────────────────
    ("beverage",    "snack",    ["teh", "kopi", "jus", "juice", "sirup", "minuman",
                                   "sari buah", "air kelapa"]),

    # ── Oils & Fats ───────────────────────────────────────────────────────────
    ("fat_oil",     "snack",    ["minyak", "santan", "margarin", "margarine",
                                   "lemak", "gajih"]),

    # ── Condiments & Spices (low-calorie) ─────────────────────────────────────
    ("condiment",   "snack",    ["garam", "gula", "kecap", "saos", "saus", "cuka",
                                   "bumbu", "rempah", "kunyit", "jahe", "bawang",
                                   "cabai", "cabe", "lada", "merica", "terasi"]),
]

# Meal-slot assignment for the GA chromosome
# The GA needs: 1 breakfast + 1 lunch + 1 dinner + 1 snack
# We use a simplified rule: protein/carb/veg → lunch & dinner; snack foods → snack; dairy → breakfast
_MEAL_SLOT_MAP: dict[str, str] = {
    "carbohydrate": "lunch",
    "protein":      "lunch",
    "vegetable":    "dinner",
    "fruit":        "snack",
    "dairy":        "breakfast",
    "snack":        "snack",
    "legume":       "snack",
    "beverage":     "snack",
    "fat_oil":      "snack",
    "condiment":    "snack",
    "other":        "snack",
}


def _infer_category(name: str) -> str:
    """Return the nutritional category string for a food name (Indonesian)."""
    name_lower = name.lower()
    for category, _meal_tag, keywords in _CATEGORY_RULES:
        if any(kw in name_lower for kw in keywords):
            return category
    return "other"


def _infer_meal_tag(category: str) -> str:
    """Return the meal slot tag based on the food category."""
    return _MEAL_SLOT_MAP.get(category, "snack")


# ─────────────────────────────────────────────
# Dataset loader class
# ─────────────────────────────────────────────

class FoodDataset:
    """
    Loads and manages the TKPI food composition dataset.

    Parameters
    ----------
    csv_path : Path or str
        Absolute or relative path to `tkpi_data.csv`.
        Defaults to ``<project_root>/dataset/tkpi_data.csv``.

    Usage
    -----
    >>> ds = FoodDataset()
    >>> ds.summary()
    >>> sample = ds.get_random_foods(n=10)
    >>> breakfast_items = ds.get_by_meal_tag("breakfast")
    """

    # Internal column name mapping (CSV name → internal name)
    _COL_MAP = {
        "No":             "id",
        "Nama_Bahan":     "name",
        "Porsi_g":        "serving_g",
        "Kalori_kal":     "calories",
        "Karbohidrat_g":  "carbs",
        "Protein_g":      "protein",
        "Lemak_g":        "fats",
        "Serat_g":        "fiber",
    }

    # Numeric columns that may contain NaN → fill with 0.0
    _NUMERIC_COLS = ["calories", "carbs", "protein", "fats", "fiber"]

    def __init__(self, csv_path: Path | str | None = None) -> None:
        self._path = Path(csv_path) if csv_path else DEFAULT_CSV_PATH
        self._df: pd.DataFrame = self._load_and_clean()
        self._records: list[FoodRecord] = self._build_records()
        logger.info(
            "FoodDataset loaded: %d records from '%s'",
            len(self._records), self._path,
        )

    # ── Public interface ─────────────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self._records)

    @property
    def records(self) -> list[FoodRecord]:
        """All food records as a list of FoodRecord Pydantic models."""
        return self._records

    @property
    def dataframe(self) -> pd.DataFrame:
        """Cleaned Pandas DataFrame (renamed columns, categories added)."""
        return self._df.copy()

    def get_by_category(self, category: str) -> list[FoodRecord]:
        """
        Return all records whose nutritional category matches `category`.

        Parameters
        ----------
        category : str
            One of: carbohydrate | protein | vegetable | fruit | dairy |
                    snack | legume | beverage | fat_oil | condiment | other
        """
        return [r for r in self._records if r.category == category]

    def get_by_meal_tag(self, meal_tag: str) -> list[FoodRecord]:
        """
        Return all records tagged for a specific meal slot.

        Parameters
        ----------
        meal_tag : str
            One of: breakfast | lunch | dinner | snack
        """
        return [r for r in self._records if r.meal_tag == meal_tag]

    def get_random_foods(self, n: int, seed: int | None = None) -> list[FoodRecord]:
        """
        Randomly sample `n` food items from the full dataset.
        Used by the GA to seed the initial population.

        Parameters
        ----------
        n    : Number of food items to sample.
        seed : Optional random seed for reproducibility.
        """
        if n > len(self._records):
            raise ValueError(
                f"Requested {n} items but dataset only has {len(self._records)} records."
            )
        rng = random.Random(seed)
        return rng.sample(self._records, n)

    def get_random_by_meal_tag(
        self, meal_tag: str, n: int = 1, seed: int | None = None
    ) -> list[FoodRecord]:
        """
        Randomly sample `n` food items filtered by meal_tag.
        Falls back to the full dataset if the tag has fewer than `n` items.

        Parameters
        ----------
        meal_tag : Target meal slot.
        n        : Number of items to sample.
        seed     : Optional random seed.
        """
        pool = self.get_by_meal_tag(meal_tag)
        if len(pool) < n:
            logger.warning(
                "meal_tag '%s' has only %d items; falling back to full dataset.",
                meal_tag, len(pool),
            )
            pool = self._records
        rng = random.Random(seed)
        return rng.sample(pool, min(n, len(pool)))

    def find_by_name(self, query: str) -> list[FoodRecord]:
        """Case-insensitive substring search on food names."""
        q = query.lower()
        return [r for r in self._records if q in r.name.lower()]

    def summary(self) -> None:
        """Print a concise summary of the dataset to stdout."""
        print(f"\n{'=' * 50}")
        print(f"  TKPI Dataset Summary")
        print(f"{'=' * 50}")
        print(f"  Total records  : {len(self._records)}")
        print(f"  Source file    : {self._path}")
        print(f"\n  Records by category:")
        cats = {}
        for r in self._records:
            cats[r.category] = cats.get(r.category, 0) + 1
        for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
            print(f"    {cat:<18} {count:>5}")
        print(f"\n  Records by meal tag:")
        tags: dict[str, int] = {}
        for r in self._records:
            tags[r.meal_tag] = tags.get(r.meal_tag, 0) + 1
        for tag, count in sorted(tags.items(), key=lambda x: -x[1]):
            print(f"    {tag:<18} {count:>5}")
        print(f"{'=' * 50}\n")

    # ── Private helpers ──────────────────────────────────────────────────────

    def _load_and_clean(self) -> pd.DataFrame:
        """Load CSV and apply all cleaning steps."""
        if not self._path.exists():
            raise FileNotFoundError(
                f"Dataset not found at '{self._path}'. "
                "Please place tkpi_data.csv in the /dataset folder."
            )

        df = pd.read_csv(self._path)

        # 1. Rename columns to internal names
        df = df.rename(columns=self._COL_MAP)

        # 2. Fill NaN in numeric nutritional columns with 0.0
        for col in self._NUMERIC_COLS:
            if col in df.columns:
                df[col] = df[col].fillna(0.0)

        # 3. Ensure serving_g has a sane default (100 g)
        if "serving_g" in df.columns:
            df["serving_g"] = df["serving_g"].fillna(100).astype(int)

        # 4. Drop rows where the food name is missing
        df = df.dropna(subset=["name"]).reset_index(drop=True)

        # 5. Strip whitespace from food names
        df["name"] = df["name"].str.strip()

        # 6. Infer category and meal_tag
        df["category"] = df["name"].apply(_infer_category)
        df["meal_tag"] = df["category"].apply(_infer_meal_tag)

        logger.debug("Dataset cleaned: %d rows retained.", len(df))
        return df

    def _build_records(self) -> list[FoodRecord]:
        """Convert cleaned DataFrame rows into FoodRecord Pydantic models."""
        records: list[FoodRecord] = []
        for _, row in self._df.iterrows():
            try:
                records.append(
                    FoodRecord(
                        id=int(row["id"]),
                        name=str(row["name"]),
                        serving_g=int(row["serving_g"]),
                        calories=float(row["calories"]),
                        carbs=float(row["carbs"]),
                        protein=float(row["protein"]),
                        fats=float(row["fats"]),
                        fiber=float(row["fiber"]),
                        category=str(row["category"]),
                        meal_tag=str(row["meal_tag"]),
                    )
                )
            except Exception as exc:
                logger.warning("Skipped row id=%s due to error: %s", row.get("id"), exc)
        return records


# ─────────────────────────────────────────────
# Module-level singleton (lazy, cached)
# ─────────────────────────────────────────────

_dataset_instance: FoodDataset | None = None


def get_dataset(csv_path: Path | str | None = None) -> FoodDataset:
    """
    Return the shared FoodDataset singleton.
    On first call the CSV is loaded; subsequent calls reuse the cached instance.

    Parameters
    ----------
    csv_path : Override the default CSV path (useful for testing).
    """
    global _dataset_instance
    if _dataset_instance is None:
        _dataset_instance = FoodDataset(csv_path)
    return _dataset_instance


def get_random_foods(n: int, seed: int | None = None) -> list[FoodRecord]:
    """
    Module-level convenience wrapper — randomly sample `n` food items.
    Used directly by the Genetic Algorithm for initial population seeding.

    Parameters
    ----------
    n    : How many FoodRecord items to return.
    seed : Optional random seed for reproducibility in tests.
    """
    return get_dataset().get_random_foods(n=n, seed=seed)


# ─────────────────────────────────────────────
# Self-test (python -m app.data.dataset)
# ─────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ds = FoodDataset()
    ds.summary()

    print("── Sample: 5 random foods ──────────────────────")
    for food in ds.get_random_foods(5, seed=42):
        print(f"  [{food.meal_tag:>9}] {food.name:<35} "
              f"{food.calories:>6.1f} kcal  "
              f"C:{food.carbs:>5.1f}g  P:{food.protein:>5.1f}g  F:{food.fats:>5.1f}g")

    print("\n── Breakfast pool (size) ──────────────────────")
    bf = ds.get_by_meal_tag("breakfast")
    print(f"  {len(bf)} items tagged as breakfast")
    for food in bf[:5]:
        print(f"  [{food.category:<14}] {food.name}")

    print("\n── Lunch pool (size) ──────────────────────────")
    ln = ds.get_by_meal_tag("lunch")
    print(f"  {len(ln)} items tagged as lunch")

    print("\n── Search: 'nasi' ─────────────────────────────")
    for food in ds.find_by_name("nasi")[:5]:
        print(f"  {food.name:<35} → {food.category} / {food.meal_tag}")
