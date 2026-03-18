# hindi-readability 📖🇮🇳

**The first Python package for measuring the readability of Hindi text.**

Zero external dependencies. Pure Python 3.9+.

---

## The Problem

English has Flesch-Kincaid, Gunning Fog, and ARI — readability formulas used in MS Word since 1992. **Hindi has nothing.**

India has 24.8 crore school students, 886 million internet users consuming Hindi content, and 14.7 lakh schools — all producing and consuming Hindi text with no way to automatically measure whether it is easy or hard to read.

This package fills that gap with three **original formulas** designed specifically for Devanagari script.

---

## Installation

```bash
pip install hindi-readability
```

---

## Quick Start

```python
from hindi_readability import ReadabilityScorer

rs = ReadabilityScorer()

# Simple sentence
result = rs.score("यह एक सरल वाक्य है।")
print(result["hrs"])          # Hindi Readability Score (0-100)
print(result["label"])        # "Easy"
print(result["grade_label"])  # "Class 3–5"
print(result["cbse_level"])   # "Prathmik Uttara"

# Constitutional text — hard
result = rs.score("संविधान की प्रस्तावना में भारत को एक संप्रभु, समाजवादी, धर्मनिरपेक्ष, लोकतांत्रिक गणराज्य घोषित किया गया है।")
print(result["hrs"])        # 0.0
print(result["label"])      # "Expert"
print(result["grade_label"])# "College+"

# Compare multiple texts — sorted easiest first
texts = [
    "बच्चे खेलते हैं।",
    "भारत की शिक्षा नीति बदल रही है।",
    "संवैधानिक प्रावधानों के अनुसार नागरिकों के मूल अधिकार सुरक्षित हैं।",
]
ranked = rs.compare(texts)
for r in ranked:
    print(f"{r['hrs']:5.1f}  {r['label']:12}  {r['text'][:40]}")

# Get simplification suggestions
suggestions = rs.simplify_suggestions("संवैधानिक प्रावधानों के अनुसार...")
for s in suggestions:
    print(s)

# Check if appropriate for a school grade
rs.is_appropriate_for_grade("यह सरल पाठ है।", grade=5)  # True/False
```

---

## The Three Formulas

### 1. Hindi Readability Score (HRS)
An ease score from **0 to 100** — higher means easier. Inspired by Flesch Reading Ease but redesigned for Devanagari.

| Score | Label | Suitable for |
|-------|-------|-------------|
| 90–100 | Very easy | Class 1–2 |
| 70–89 | Easy | Class 3–5 |
| 50–69 | Standard | Class 6–8 |
| 30–49 | Difficult | Class 9–10 |
| 10–29 | Very hard | Class 11–12 |
| 0–9 | Expert | College+ |

**Formula:**
```
HRS = 206.0
      - (60.0 × avg_syllables_per_word)
      - (1.8  × avg_words_per_sentence)
      - (70.0 × conjunct_density)
      - (8.0  × matra_complexity)
```

### 2. Hindi Grade Level (HGL)
Maps HRS to Indian school grades (CBSE Class 1 to College+).

### 3. Hindi Complexity Index (HCI)
A normalized 0–1 score. Lower = easier. Useful for ML pipelines.

---

## Why These Formulas Are Different

| Feature | English (Flesch-Kincaid) | Hindi (this package) |
|---------|--------------------------|---------------------|
| Syllable counting | English phoneme rules | Devanagari matra-based |
| Conjunct detection | Not applicable | ✓ Virama-based detection |
| Script-aware | No | ✓ Full Unicode U+0900–U+097F |
| Long vowel complexity | No | ✓ Guru/laghu distinction |
| CBSE grade mapping | No | ✓ Class 1–12 + College |

**Conjunct consonants** (संयुक्त अक्षर) — formed when a virama (्) joins two consonants — are the primary marker of Sanskrit-origin vocabulary. They appear in tatsam words (तत्सम) which are significantly harder for younger readers. This package detects them automatically using Unicode analysis.

---

## What Is Solved vs. What This Package Solves

### Already solved (for English)
- Flesch Reading Ease (1948)
- Flesch-Kincaid Grade Level (1975)
- Gunning Fog Index (1952)

### What this package solves (first ever for Hindi)
- Matra-aware syllable counting
- Conjunct consonant density as a difficulty signal
- CBSE-aligned grade level output
- Actionable simplification suggestions in Hindi

### Still open (future research / dissertation topics)
- Validation against human-graded Hindi texts (labeled corpus needed)
- Domain-specific calibration (news vs. textbooks vs. legal)
- Extension to Bengali, Marathi, Gujarati (same Devanagari script family)
- Hinglish (code-mixed Hindi-English) readability

---

## API Reference

```python
ReadabilityScorer.score(text)              # Full report dict
ReadabilityScorer.compare(texts)           # Rank list easiest→hardest
ReadabilityScorer.batch_score(texts)       # Score list in order
ReadabilityScorer.is_appropriate_for_grade(text, grade)  # bool
ReadabilityScorer.simplify_suggestions(text)  # list of Hindi suggestions

# Low-level functions
hindi_readability_score(text)    # float 0-100
hindi_grade_level(text)          # dict {grade, grade_label, cbse_level}
hindi_complexity_index(text)     # float 0-1
analyse(text)                    # dict of raw script counts
syllables_per_word(text)         # float
conjunct_density(text)           # conjuncts per 100 words
```

---

## Citation

If you use this package in academic work:

```
@software{hindi_readability,
  author    = {Prabhat Chaudhary},
  title     = {hindi-readability: The First Python Package for Hindi Text Readability},
  year      = {2025},
  publisher = {PyPI},
  url       = {https://pypi.org/project/hindi-readability/}
}
```

---

## License

MIT — free for academic and commercial use.
