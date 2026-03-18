"""
scorer.py — Main Public API
============================
The ReadabilityScorer class is the primary interface for hindi-readability.
It combines all three formulas plus the raw script analysis into one call.
"""

from typing import Dict, List
from .script   import analyse, syllables_per_word, conjunct_density
from .formulas import (
    hindi_readability_score,
    hindi_grade_level,
    hindi_complexity_index,
)


_LABEL_MAP = [
    (90,  "Very easy",  "Suitable for Class 1–2 students"),
    (70,  "Easy",       "Suitable for Class 3–5 students"),
    (50,  "Standard",   "Suitable for Class 6–8 students"),
    (30,  "Difficult",  "Suitable for Class 9–10 students"),
    (10,  "Very hard",  "Suitable for Class 11–12 students"),
    (0,   "Expert",     "College-level or specialist text"),
]


def _hrs_label(hrs: float) -> tuple:
    for threshold, label, desc in _LABEL_MAP:
        if hrs >= threshold:
            return label, desc
    return "Expert", "College-level or specialist text"


class ReadabilityScorer:
    """
    All-in-one Hindi readability analyser.

    Example
    -------
    >>> from hindi_readability import ReadabilityScorer
    >>> rs = ReadabilityScorer()

    >>> rs.score("यह एक सरल वाक्य है।")
    {
        'hrs': 88.4,
        'label': 'Easy',
        'grade': 4,
        'grade_label': 'Class 3–5',
        'hci': 0.18,
        'syllables_per_word': 1.6,
        'conjunct_density': 0.0,
        ...
    }

    >>> rs.compare(["बच्चों की कहानी।", "संविधान की प्रस्तावना।"])
    [{'text': '...', 'hrs': 91.2, 'label': 'Very easy'}, ...]
    """

    def score(self, text: str) -> Dict[str, object]:
        """
        Full readability report for a single text.

        Returns
        -------
        dict with keys:
            hrs             : Hindi Readability Score (0–100, higher = easier)
            label           : human-readable ease label
            description     : who this text is suitable for
            grade           : school grade number (1–13)
            grade_label     : e.g. "Class 6–8"
            cbse_level      : e.g. "Madhyamik"
            hci             : Hindi Complexity Index (0–1, lower = easier)
            syllables_per_word : float
            conjunct_density   : conjuncts per 100 words
            raw             : raw script analysis dict
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty.")

        hrs      = hindi_readability_score(text)
        grade    = hindi_grade_level(text)
        hci      = hindi_complexity_index(text)
        raw      = analyse(text)
        label, desc = _hrs_label(hrs)

        return {
            "hrs":               hrs,
            "label":             label,
            "description":       desc,
            "grade":             grade["grade"],
            "grade_label":       grade["grade_label"],
            "cbse_level":        grade["cbse_level"],
            "hci":               hci,
            "syllables_per_word": syllables_per_word(text),
            "conjunct_density":  conjunct_density(text),
            "raw":               raw,
        }

    def compare(self, texts: List[str]) -> List[Dict[str, object]]:
        """
        Score and rank multiple texts by difficulty.

        Returns a list sorted easiest → hardest (highest HRS first).
        Each item includes 'text' (first 60 chars) + all score fields.
        """
        results = []
        for t in texts:
            try:
                s = self.score(t)
                s["text"] = t[:60] + ("…" if len(t) > 60 else "")
                results.append(s)
            except ValueError:
                continue
        return sorted(results, key=lambda x: x["hrs"], reverse=True)

    def batch_score(self, texts: List[str]) -> List[Dict[str, object]]:
        """Score a list of texts in order (no sorting)."""
        results = []
        for t in texts:
            try:
                results.append(self.score(t))
            except ValueError:
                results.append({"error": "empty text"})
        return results

    def is_appropriate_for_grade(self, text: str, grade: int) -> bool:
        """
        Check if a text is appropriate for a given school grade (1–12).

        Returns True if the text's grade level matches the target grade
        within ±1 grade of tolerance.
        """
        result = self.score(text)
        text_grade = result["grade"]
        return abs(text_grade - grade) <= 1

    def simplify_suggestions(self, text: str) -> List[str]:
        """
        Return actionable suggestions to simplify a Hindi text.
        Based on which metric is worst.
        """
        result = self.score(text)
        suggestions = []

        if result["syllables_per_word"] > 3.0:
            suggestions.append(
                "शब्दों की लंबाई कम करें — छोटे शब्द (1–2 अक्षर) अधिक आसान होते हैं।"
            )
        if result["conjunct_density"] > 15:
            suggestions.append(
                "संयुक्त अक्षरों वाले शब्द कम करें — तत्सम शब्दों की जगह तद्भव शब्द लिखें।"
            )
        if result["raw"]["sentences"] > 0:
            words_per_sent = result["raw"]["words"] / result["raw"]["sentences"]
            if words_per_sent > 15:
                suggestions.append(
                    "वाक्य छोटे करें — एक वाक्य में 10–12 से अधिक शब्द न रखें।"
                )
        if not suggestions:
            suggestions.append("यह पाठ पहले से पठनीय है। कोई बड़ा सुधार आवश्यक नहीं।")
        return suggestions
