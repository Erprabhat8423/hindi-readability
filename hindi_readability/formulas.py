"""
formulas.py — Hindi Readability Formulas
=========================================
This module implements THREE original readability formulas for Hindi text,
all designed from scratch for Devanagari script characteristics.

WHY NOT JUST TRANSLATE FLESCH-KINCAID?
---------------------------------------
Flesch-Kincaid counts English syllables and words per sentence.
Hindi is fundamentally different:
  1. Syllable weight — Hindi has HEAVY (guru) and LIGHT (laghu) syllables
     based on matras. A long-matra word is harder than a short one of the
     same syllable count.
  2. Conjuncts (sankyukt akshar) — These are the single biggest marker of
     reading difficulty in Hindi. They appear in Sanskrit-origin (tatsama)
     words which educated adults use but children struggle with.
  3. Sentence structure — Hindi is SOV (Subject-Object-Verb). Long sentences
     with postpositions and embedded clauses are harder than simple SOV.

THE THREE FORMULAS
-------------------
1. Hindi Readability Score (HRS)   — ease score 0–100 (higher = easier)
2. Hindi Grade Level (HGL)         — school grade 1–12+
3. Hindi Complexity Index (HCI)    — raw difficulty 0–1 (lower = easier)

Each formula is independently usable. HRS is the headline metric.

FORMULA DERIVATION
-------------------
HRS is adapted from Flesch Reading Ease with Hindi-specific weights:

  HRS = 121.2
        - (58.0  × avg_syllables_per_word)
        - (1.02  × avg_words_per_sentence)
        - (22.0  × conjunct_density_normalized)
        - (6.0   × matra_complexity)

Weights chosen by linguistic reasoning:
  • avg_syllables_per_word  : primary difficulty driver (same as English)
  • avg_words_per_sentence  : secondary (same as English, lower weight)
  • conjunct_density        : NEW — unique to Hindi/Devanagari
  • matra_complexity        : NEW — ratio of heavy matras (long vowels)
                               to total matras; long matras = harder words

HGL maps HRS to Indian school grades (Class 1–12) using the same
inverse relationship as Kincaid but re-calibrated for Hindi:

  HGL = 17.2 - (HRS × 0.14)

HCI is a 0–1 normalized composite:
  HCI = weighted average of 4 sub-scores (syllable, sentence, conjunct, matra)

GRADE LABELS
------------
These are mapped to CBSE/NCERT grade groupings:
  Class 1–2   : Prathmik (Primary) — very simple
  Class 3–5   : Prathmik Uttara — simple
  Class 6–8   : Madhyamik — standard
  Class 9–10  : Uccha Madhyamik — difficult
  Class 11–12 : Uccha Vidyalay — very difficult
  College+    : Snatak — expert
"""

from typing import Dict
from .script import analyse, MATRAS

# Long-vowel matras — these indicate "heavy" (guru) syllables, harder to read
LONG_MATRAS = {
    "\u093E",  # ा  (aa)
    "\u0940",  # ी  (ii)
    "\u0942",  # ू  (uu)
    "\u0948",  # ै  (ai)
    "\u094C",  # ौ  (au)
    "\u0947",  # े  (e)
    "\u094B",  # ो  (o)
}


def _matra_complexity(text: str) -> float:
    """
    Ratio of long (heavy) matras to total matras.
    Range: 0.0 (all short vowels) → 1.0 (all long vowels).
    Long matras in a text signal Sanskrit-heavy vocabulary → harder.
    """
    long_count  = sum(1 for ch in text if ch in LONG_MATRAS)
    total_count = sum(1 for ch in text if ch in MATRAS)
    if total_count == 0:
        return 0.0
    return long_count / total_count


def hindi_readability_score(text: str) -> float:
    """
    Hindi Readability Score (HRS) — the headline metric.

    Range  : 0 – 100
    Higher = easier to read (same direction as Flesch Reading Ease)

    Interpretation:
        90–100  : Very easy  (Class 1–2)
        70–89   : Easy       (Class 3–5)
        50–69   : Standard   (Class 6–8)
        30–49   : Difficult  (Class 9–10)
        10–29   : Very hard  (Class 11–12)
        0–9     : Expert     (College+)
    """
    data = analyse(text)
    words     = max(data["words"], 1)
    sentences = max(data["sentences"], 1)
    syllables = max(data["syllables"], 1)

    avg_syl_per_word    = syllables / words
    avg_words_per_sent  = words / sentences
    conjunct_dens_norm  = (data["conjuncts"] / words)          # 0–N per word
    matra_compl         = _matra_complexity(text)

    score = (
        206.0
        - (60.0 * avg_syl_per_word)
        - (1.8  * avg_words_per_sent)
        - (70.0 * conjunct_dens_norm)
        - (8.0  * matra_compl)
    )
    return round(max(0.0, min(100.0, score)), 2)


def hindi_grade_level(text: str) -> Dict[str, object]:
    """
    Hindi Grade Level (HGL) — maps HRS to Indian school grade.

    Returns dict with:
        grade       : int   (1–13, where 13 = college+)
        grade_label : str   (e.g. "Class 6–8")
        cbse_level  : str   (e.g. "Madhyamik")
    """
    hrs = hindi_readability_score(text)
    raw_grade = 17.2 - (hrs * 0.14)
    grade = max(1, min(13, round(raw_grade)))

    if grade <= 2:
        label, cbse = "Class 1–2",   "Prathmik (Primary)"
    elif grade <= 5:
        label, cbse = "Class 3–5",   "Prathmik Uttara (Upper Primary)"
    elif grade <= 8:
        label, cbse = "Class 6–8",   "Madhyamik (Middle School)"
    elif grade <= 10:
        label, cbse = "Class 9–10",  "Uccha Madhyamik (Secondary)"
    elif grade <= 12:
        label, cbse = "Class 11–12", "Uccha Vidyalay (Senior Secondary)"
    else:
        label, cbse = "College+",    "Snatak (Graduate)"

    return {"grade": grade, "grade_label": label, "cbse_level": cbse}


def hindi_complexity_index(text: str) -> float:
    """
    Hindi Complexity Index (HCI) — normalized 0→1 composite score.

    Lower  = easier
    Higher = harder

    Sub-components (all normalized 0–1):
        syl_score      : syllables/word normalized (cap at 5 syl/word)
        sent_score     : words/sentence normalized (cap at 30 words/sent)
        conjunct_score : conjuncts/word normalized (cap at 1 per word)
        matra_score    : long-matra ratio (already 0–1)
    """
    data   = analyse(text)
    words  = max(data["words"], 1)
    sents  = max(data["sentences"], 1)

    syl_score      = min(data["syllables"] / words, 5) / 5
    sent_score     = min(words / sents, 30) / 30
    conjunct_score = min(data["conjuncts"] / words, 1.0)
    matra_score    = _matra_complexity(text)

    hci = (
        0.40 * syl_score +
        0.20 * sent_score +
        0.25 * conjunct_score +
        0.15 * matra_score
    )
    return round(hci, 4)
