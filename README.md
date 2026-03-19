# hindi-readability 📖

> **First practical Python implementation with Devanagari-specific features for Hindi text readability.**

[![PyPI version](https://img.shields.io/pypi/v/hindi-readability.svg)](https://pypi.org/project/hindi-readability/)
[![Python](https://img.shields.io/pypi/pyversions/hindi-readability.svg)](https://pypi.org/project/hindi-readability/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-38%2F38%20passing-brightgreen)](https://github.com/Erprabhat8423/hindi-readability)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97%20Demo-HuggingFace-orange)](https://huggingface.co/spaces/raja1999chaudhary/hindi-readability)

Zero external dependencies. Pure Python 3.8+. Works out of the box.

---

## Why does this exist?

English has **Flesch-Kincaid**, **Gunning Fog**, and **ARI**  readability formulas built into MS Word since 1992.

**Hindi has nothing.**

India has **24.8 crore school students**, **886 million internet users** consuming Hindi content, and **14.7 lakh schools** — all producing Hindi text with no way to automatically measure whether it is easy or hard to read.

This package fills that gap with **three original formulas** designed from scratch for Devanagari script.

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

result = rs.score("यह एक सरल वाक्य है।")
print(result["hrs"])           # 75.2  — Hindi Readability Score (0–100)
print(result["label"])         # Easy
print(result["grade_label"])   # Class 6–8
print(result["cbse_level"])    # Madhyamik
print(result["hci"])           # 0.35  — Complexity Index (0–1)
```

---

## Real Examples

```python
from hindi_readability import ReadabilityScorer
rs = ReadabilityScorer()

# Easy — children's level
easy = "यह एक बच्चा है। वह खेलता है। घर अच्छा है। माँ पानी लाई।"
r = rs.score(easy)
# hrs = 75.2  label = 'Easy'  grade_label = 'Class 6–8'

# Standard newspaper Hindi
medium = "भारत में शिक्षा का स्तर तेजी से बदल रहा है। सरकार नई नीतियां बना रही है।"
r = rs.score(medium)
# hrs = 55.8  label = 'Standard'  grade_label = 'Class 9–10'

# Expert constitutional Hindi
hard = "संविधान की प्रस्तावना में भारत को एक संप्रभु, समाजवादी, धर्मनिरपेक्ष, लोकतांत्रिक गणराज्य घोषित किया गया है।"
r = rs.score(hard)
# hrs = 0.0  label = 'Expert'  grade_label = 'College+'
```

---

## Full API Reference

### `rs.score(text)` → dict

```python
result = rs.score("यह सरल पाठ है।")
# {
#   "hrs": 75.2, "label": "Easy", "description": "Suitable for Class 3–5 students",
#   "grade": 7, "grade_label": "Class 6–8", "cbse_level": "Madhyamik",
#   "hci": 0.35, "syllables_per_word": 1.77, "conjunct_density": 15.4,
#   "raw": { "words": 13, "sentences": 4, "syllables": 23, "matras": 11,
#            "conjuncts": 2, "viramas": 2, "consonants": 18, ... }
# }
```

### `rs.compare(texts)` → list sorted easiest first

```python
ranked = rs.compare(["कठिन संवैधानिक पाठ।", "बच्चे खेलते हैं।", "भारत की नीति।"])
for r in ranked:
    print(f"HRS={r['hrs']:5.1f}  {r['label']:10}  {r['text'][:40]}")
# HRS= 91.2  Very easy   बच्चे खेलते हैं।
# HRS= 55.8  Standard    भारत की नीति।
# HRS=  0.0  Expert      कठिन संवैधानिक पाठ।
```

### `rs.batch_score(texts)` → list in original order

```python
results = rs.batch_score([text1, text2, text3])
```

### `rs.is_appropriate_for_grade(text, grade)` → bool

```python
rs.is_appropriate_for_grade("यह सरल पाठ है।", grade=5)       # True
rs.is_appropriate_for_grade("संवैधानिक प्रावधान।", grade=5)  # False
```

### `rs.simplify_suggestions(text)` → list of Hindi suggestions

```python
suggestions = rs.simplify_suggestions("संवैधानिक प्रावधानों के अनुसार...")
# ["संयुक्त अक्षरों वाले शब्द कम करें — तत्सम शब्दों की जगह तद्भव शब्द लिखें।",
#  "वाक्य छोटे करें — एक वाक्य में 10–12 से अधिक शब्द न रखें।"]
```

### Low-level functions

```python
from hindi_readability import (
    hindi_readability_score,  # float 0–100
    hindi_grade_level,        # dict {grade, grade_label, cbse_level}
    hindi_complexity_index,   # float 0–1
    analyse,                  # dict of raw Devanagari script counts
    syllables_per_word,       # float
    conjunct_density,         # conjuncts per 100 words
)
```

---

## HRS Score Interpretation

| Score   | Label      | Suitable for                          |
|---------|------------|---------------------------------------|
| 90–100  | Very easy  | Class 1–2  (Prathmik)                 |
| 70–89   | Easy       | Class 3–5  (Prathmik Uttara)          |
| 50–69   | Standard   | Class 6–8  (Madhyamik)                |
| 30–49   | Difficult  | Class 9–10 (Uccha Madhyamik)          |
| 10–29   | Very hard  | Class 11–12 (Uccha Vidyalay)          |
| 0–9     | Expert     | College+   (Snatak)                   |

---

## How the Formulas Work

### Why English formulas fail on Hindi

English readability tools count syllables and word length. Hindi requires three features English simply does not have:

**Matras (मात्राएँ)** — Vowel signs attached to consonants (ि ी ु ू ा े ै ो ौ). Long matras indicate heavier syllables. English formulas cannot detect these.

**Conjunct consonants (संयुक्त अक्षर)** — Two consonants fused by a virama (्), for example क्ष, त्र, ज्ञ, प्र. These appear mainly in Sanskrit-origin vocabulary which is significantly harder for younger readers. This is the single biggest marker of Hindi difficulty and has no equivalent in English.

**Devanagari syllable rules** — Every Hindi consonant carries an implicit /a/ vowel unless killed by a virama. Standard English syllable-counting rules are completely blind to this.

### HRS Formula

```
HRS = 206.0
      − (60.0 × avg syllables per word)
      − (1.8  × avg words per sentence)
      − (70.0 × conjunct density)
      − (8.0  × matra complexity)
```

### HGL Formula

```
HGL = 17.2 − (HRS × 0.14)   →   CBSE Class 1 to College+
```

### HCI Formula

```
HCI = 0.40×syllable_score + 0.20×sentence_score + 0.25×conjunct_score + 0.15×matra_score
```

---

## Validation Results

Validated on a **49-sentence corpus** (NCERT Class 1-12, Constitution of India, legal texts, Hindi news).

| Metric | Result | Meaning |
|--------|--------|---------|
| Pearson r | **0.81** | Strong correlation with human judgment |
| Spearman rho | **0.75** | Consistent rank ordering |
| Mean Absolute Error | **1.67 grades** | Less than 2 school grades off on average |
| Accuracy within 2 grades | **73.5%** | 36 / 49 sentences correctly classified |

Run validation yourself:
```bash
python validation/validate.py
```

---

## Open Research Directions

This package provides a **baseline**. The following are open problems suitable for M.Tech dissertation or research paper:

- **Corpus validation** : calibrate formula weights against human-graded Hindi texts (teacher-labeled data)
- **Domain calibration** : news vs. textbooks vs. legal vs. social media have different norms
- **Hinglish (code-mixed)** : no readability tool handles Hindi-English mixed text yet
- **Extension** : Bengali, Marathi, Gujarati use the same Devanagari script family
- **ML-based approach** : fine-tune IndicBERT for readability regression and compare against this baseline

---

## Running the Tests

```bash
git clone https://github.com/Erprabhat8423/hindi-readability.git
cd hindi-readability
python tests/test_all.py
# Tests: 38/38 passed ✓
```

---

## Project Structure

```
hindi-readability/
├── hindi_readability/
│   ├── __init__.py      # Public exports
│   ├── script.py        # Devanagari Unicode analyser
│   ├── formulas.py      # HRS, HGL, HCI implementations
│   └── scorer.py        # ReadabilityScorer public API
├── tests/
│   └── test_all.py      # 38 tests
├── pyproject.toml
└── README.md
```

---

## Changelog

### v0.3.0
- Corpus-calibrated grade formula on 49-sentence human-graded dataset
- Statistical proof: Pearson r=0.81, Spearman rho=0.75, MAE=1.67 grades
- Added data/validation_dataset.csv and validation/validate.py
- Fixed claim language: first practical implementation, not first ever conceptually
- Python 3.8 build fix in pyproject.toml

### v0.2.0
- Improved README with full API docs, real examples, formula explanations
- Added HRS score table with CBSE level names in English
- Added open research directions section for dissertation reference

### v0.1.0
- Initial release — HRS, HGL, HCI formulas
- ReadabilityScorer with 5 public methods
- 38 tests passing, zero external dependencies

---

## Citation

```bibtex
@software{hindi_readability,
  author    = {Prabhat Chaudhary},
  title     = {hindi-readability: The First Python Package for Hindi Text Readability},
  year      = {2026},
  version   = {0.3.0},
  publisher = {PyPI},
  url       = {https://pypi.org/project/hindi-readability/}
}
```

---

## License

MIT — free for academic and commercial use.

