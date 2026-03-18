"""
hindi-readability
=================
The first Python package for measuring readability of Hindi text.

Provides three original formulas designed for Devanagari script:
  - Hindi Readability Score (HRS)  — 0-100, higher = easier
  - Hindi Grade Level (HGL)        — CBSE Class 1 to College+
  - Hindi Complexity Index (HCI)   — 0-1, lower = easier

Install: pip install hindi-readability
"""

from .scorer  import ReadabilityScorer
from .script  import analyse, syllables_per_word, conjunct_density
from .formulas import (
    hindi_readability_score,
    hindi_grade_level,
    hindi_complexity_index,
)

__version__ = "0.2.0"
__author__  = "Prabhat Chaudhary"
__all__ = [
    "ReadabilityScorer",
    "analyse",
    "syllables_per_word",
    "conjunct_density",
    "hindi_readability_score",
    "hindi_grade_level",
    "hindi_complexity_index",
]
