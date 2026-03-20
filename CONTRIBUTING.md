# Contributing to hindi-readability

Thank you for your interest in contributing! This is an open-source research project focused on Hindi text readability — a genuinely under-served area in NLP. Every contribution, however small, helps make Hindi content more accessible to 886 million users.

---

## Ways to Contribute

### 1. Expand the Hindi word lexicons
The sentiment and difficulty lexicons in `hindi_readability/formulas.py` currently cover ~200 Hindi words. Adding more words — especially tatsam (Sanskrit-origin) vocabulary — directly improves formula accuracy.

**How:** Open `hindi_readability/formulas.py` and add entries to the relevant word lists. Then run the test suite to confirm nothing breaks.

### 2. Add sentences to the validation corpus
The file `data/validation_dataset.csv` currently has 49 sentences. More real, human-graded sentences improve our statistical validation.

**Format:**
```
text,source,human_grade,human_difficulty,cbse_class
आपका हिंदी वाक्य यहाँ।,Source name,6,4,6
```

Rules for adding sentences:
- Must be real Hindi text (not synthetically generated)
- Source must be named (NCERT class, newspaper name, book title)
- `human_grade` = CBSE class level (1–13, where 13 = College+)
- `human_difficulty` = difficulty 1–10 based on your reading judgment
- No duplicate sentences

### 3. Extend to new Indic languages
The `script.py` module uses Unicode ranges — extending to Bengali (U+0980–U+09FF), Gujarati (U+0A80–U+0AFF), or Marathi (same Devanagari block) requires adding new Unicode ranges and calibrating formula constants.

### 4. Report bugs or wrong scores
If you find a Hindi text that gets a clearly wrong readability score, open a GitHub Issue with:
- The input text
- The score you got
- What score you expected and why

### 5. Improve documentation
Fix typos, add examples, translate the README to Hindi, or improve the API reference.

---

## Development Setup

```bash
# 1. Fork and clone the repo
git clone https://github.com/YOUR-USERNAME/hindi-readability.git
cd hindi-readability

# 2. Install in editable mode (no extra dependencies needed)
pip install -e .

# 3. Run the test suite
python tests/test_all.py
# Expected: Tests: 38/38 passed ✓

# 4. Run the validation script
python validation/validate.py
# Expected: Pearson r=0.81, MAE=1.67
```

---

## Project Structure

```
hindi-readability/
├── hindi_readability/
│   ├── __init__.py      # Public API exports
│   ├── script.py        # Devanagari Unicode analyser (matras, conjuncts, syllables)
│   ├── formulas.py      # HRS, HGL, HCI formula implementations
│   └── scorer.py        # ReadabilityScorer public API class
├── tests/
│   └── test_all.py      # 38 tests — must all pass before submitting PR
├── data/
│   └── validation_dataset.csv   # Human-graded Hindi sentences corpus
├── validation/
│   └── validate.py      # Statistical validation — Pearson r, MAE, accuracy
├── pyproject.toml
└── README.md
```

---

## Submitting a Pull Request

1. **Fork** the repository and create a branch: `git checkout -b my-contribution`
2. **Make your changes** — keep each PR focused on one thing
3. **Run all tests:** `python tests/test_all.py` — all 38 must pass
4. **If you changed the formula or corpus**, run `python validation/validate.py` and include the output in your PR description
5. **Submit the PR** with a clear description of what you changed and why

---

## Code Style

- Python 3.8+ compatible (no walrus operator, no `X | Y` union types)
- No external dependencies — everything must work with the Python standard library only
- Hindi text in source files must be UTF-8 encoded
- All public functions must have a docstring with an example

---

## Reporting Issues

Open a GitHub Issue and include:

| Field | Example |
|-------|---------|
| Input text | `"यह एक परीक्षण है।"` |
| Expected score | HRS ~80 (Easy) |
| Actual score | HRS 12 (Expert) |
| Python version | 3.11 |
| Package version | `pip show hindi-readability` |

---

## Research Context

This package is part of M.Tech Computer Science research at Sagar Institute Of Technology and Management. If you use this package or dataset in academic work, please cite:

```bibtex
@software{hindi_readability,
  author    = {Prabhat Chaudhary},
  title     = {hindi-readability: First Practical Python Implementation
               of Devanagari-Aware Hindi Text Readability Scoring},
  year      = {2026},
  version   = {0.3.0},
  publisher = {PyPI},
  url       = {https://pypi.org/project/hindi-readability/}
}
```

---

## Open Research Problems

If you are an NLP researcher looking for dissertation topics, these are the open problems this package does not yet solve:

- **Hinglish (code-mixed) readability** — no tool handles Hindi-English mixed text
- **Corpus validation** — formula weights need calibration on 200+ teacher-graded sentences
- **ML-based comparison** — fine-tuning IndicBERT for readability regression
- **Extension to Bengali and Marathi** — same Devanagari family, needs calibration
- **Sarcasm and negation** — lexicon-based scoring fails on sarcastic text

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

*Questions? Open a GitHub Issue or reach out via the repository.*