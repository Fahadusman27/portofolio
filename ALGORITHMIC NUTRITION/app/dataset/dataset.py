"""
dataset.py
----------
Data handler for the TKPI (Tabel Komposisi Pangan Indonesia) CSV dataset.
Loads and sanitises food composition data; provides random-sampling helpers
for Genetic Algorithm gene initialisation.
"""

import os
import random
from pathlib import Path
from typing import Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Path resolution — works regardless of the working directory
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent
DEFAULT_CSV_PATH = _HERE / "tkpi_data.csv"

# ---------------------------------------------------------------------------
# Expected columns (must match the CSV header exactly)
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = [
    "No",
    "Nama_Bahan",
    "Porsi_g",
    "Kalori_kal",
    "Karbohidrat_g",
    "Protein_g",
    "Lemak_g",
    "Serat_g",
]

NUMERIC_COLUMNS = [
    "Porsi_g",
    "Kalori_kal",
    "Karbohidrat_g",
    "Protein_g",
    "Lemak_g",
    "Serat_g",
]


# ---------------------------------------------------------------------------
# FoodDataset class
# ---------------------------------------------------------------------------

class FoodDataset:
    """
    Loads and exposes the TKPI food composition dataset.

    Usage
    -----
    >>> ds = FoodDataset()
    >>> sample = ds.random_food_item()   # one random row as a dict
    >>> batch  = ds.random_sample(n=4)   # four random rows as list of dicts
    """

    def __init__(self, csv_path: Optional[str | Path] = None) -> None:
        """
        Parameters
        ----------
        csv_path : str or Path, optional
            Absolute or relative path to ``tkpi_data.csv``.
            Defaults to the ``tkpi_data.csv`` file in the same directory as
            this module.
        """
        path = Path(csv_path) if csv_path else DEFAULT_CSV_PATH

        if not path.exists():
            raise FileNotFoundError(
                f"TKPI dataset not found at: {path}\n"
                "Place 'tkpi_data.csv' inside 'app/dataset/' or pass the "
                "correct path to FoodDataset()."
            )

        self._df: pd.DataFrame = self._load(path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self, path: Path) -> pd.DataFrame:
        """Read CSV, validate columns, and clean numeric values."""
        df = pd.read_csv(path)

        # ── Validate columns ────────────────────────────────────────────
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(
                f"CSV is missing expected columns: {missing}\n"
                f"Found columns: {list(df.columns)}"
            )

        # ── Fill NaN in numeric columns with 0.0 ────────────────────────
        for col in NUMERIC_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        # ── Drop rows with no food name ──────────────────────────────────
        df = df.dropna(subset=["Nama_Bahan"]).reset_index(drop=True)

        # ── Remove rows where all macros are zero (unusable data) ────────
        macro_cols = ["Kalori_kal", "Karbohidrat_g", "Protein_g", "Lemak_g"]
        df = df[df[macro_cols].sum(axis=1) > 0].reset_index(drop=True)

        if df.empty:
            raise ValueError("Dataset is empty after cleaning. Check your CSV file.")

        return df

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def dataframe(self) -> pd.DataFrame:
        """The cleaned Pandas DataFrame (read-only view)."""
        return self._df.copy()

    @property
    def size(self) -> int:
        """Number of usable food items in the dataset."""
        return len(self._df)

    def get_item_by_index(self, idx: int) -> dict:
        """
        Return a single food item as a plain dict by its integer index.

        Parameters
        ----------
        idx : int
            Row index (0-based, wraps with modulo if out of range).

        Returns
        -------
        dict
            Keys match REQUIRED_COLUMNS.
        """
        safe_idx = idx % self.size
        return self._df.iloc[safe_idx].to_dict()

    def random_food_item(self) -> dict:
        """
        Return one randomly selected food item as a plain dict.

        Intended use: supply a single **gene** to the Genetic Algorithm.
        """
        idx = random.randint(0, self.size - 1)
        return self._df.iloc[idx].to_dict()

    def random_sample(self, n: int = 4) -> list[dict]:
        """
        Return ``n`` randomly selected food items (with replacement).

        Intended use: initialise one **chromosome** (daily meal plan) for
        the Genetic Algorithm.

        Parameters
        ----------
        n : int
            Number of items to sample. Defaults to 4 (one per meal slot).

        Returns
        -------
        list[dict]
            List of food-item dicts.
        """
        if n < 1:
            raise ValueError("n must be at least 1.")
        return [self.random_food_item() for _ in range(n)]

    def all_indices(self) -> list[int]:
        """Return a list of all valid row indices."""
        return list(range(self.size))

    def summary(self) -> str:
        """Human-readable dataset summary."""
        return (
            f"FoodDataset | {self.size} items loaded\n"
            f"  Avg Kalori  : {self._df['Kalori_kal'].mean():.1f} kcal\n"
            f"  Avg Protein : {self._df['Protein_g'].mean():.1f} g\n"
            f"  Avg Carbs   : {self._df['Karbohidrat_g'].mean():.1f} g\n"
            f"  Avg Fat     : {self._df['Lemak_g'].mean():.1f} g\n"
        )


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ds = FoodDataset()
    print(ds.summary())
    print("\nRandom gene  :", ds.random_food_item()["Nama_Bahan"])
    print("Random chromosome:", [x["Nama_Bahan"] for x in ds.random_sample(4)])
