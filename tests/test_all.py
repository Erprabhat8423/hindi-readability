"""
Tests for hindi-readability
Run: python tests/test_all.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from hindi_readability import (
    ReadabilityScorer,
    analyse,
    syllables_per_word,
    conjunct_density,
    hindi_readability_score,
    hindi_grade_level,
    hindi_complexity_index,
)

rs = ReadabilityScorer()

# ── Real Hindi test sentences at different difficulty levels ──────────────────

# Very EASY — short common words, no conjuncts (Class 1-2 level)
EASY = "यह एक बच्चा है। वह खेलता है। घर अच्छा है। माँ पानी लाई।"

# MEDIUM — standard newspaper Hindi (Class 6-8 level)
MEDIUM = "भारत में शिक्षा का स्तर तेजी से बदल रहा है। सरकार नई नीतियां बना रही है।"

# HARD — Sanskrit-heavy formal Hindi (Class 11-12 / college level)
HARD = "संविधान की प्रस्तावना में भारत को एक संप्रभु, समाजवादी, धर्मनिरपेक्ष, लोकतांत्रिक गणराज्य घोषित किया गया है।"

results = []

# ── Script analyser tests ─────────────────────────────────────────────────────
def t(name, cond):
    results.append((name, cond))

data_easy = analyse(EASY)
data_hard = analyse(HARD)

t("analyse returns dict",         isinstance(data_easy, dict))
t("words counted",                data_easy["words"] > 0)
t("sentences counted",            data_easy["sentences"] > 0)
t("syllables counted",            data_easy["syllables"] > 0)
t("hard text has more conjuncts", data_hard["conjuncts"] > data_easy.get("conjuncts", 0))
t("hard text has more matras",    data_hard["matras"] >= data_easy["matras"])

# syllables_per_word
syl_easy = syllables_per_word(EASY)
syl_hard = syllables_per_word(HARD)
t("syllables_per_word > 0",       syl_easy > 0)
t("hard has more syl/word",       syl_hard >= syl_easy)

# conjunct_density
cd_easy = conjunct_density(EASY)
cd_hard = conjunct_density(HARD)
t("conjunct_density >= 0",        cd_easy >= 0)
t("hard has higher density",      cd_hard > cd_easy)

# ── Formula tests ─────────────────────────────────────────────────────────────
hrs_easy   = hindi_readability_score(EASY)
hrs_medium = hindi_readability_score(MEDIUM)
hrs_hard   = hindi_readability_score(HARD)

t("HRS in 0-100 range (easy)",    0 <= hrs_easy <= 100)
t("HRS in 0-100 range (hard)",    0 <= hrs_hard <= 100)
t("easy > medium HRS",            hrs_easy > hrs_medium)
t("medium > hard HRS",            hrs_medium > hrs_hard)

grade_easy = hindi_grade_level(EASY)
grade_hard = hindi_grade_level(HARD)
t("grade dict has keys",          "grade" in grade_easy and "grade_label" in grade_easy)
t("easy grade < hard grade",      grade_easy["grade"] <= grade_hard["grade"])
t("grade 1-13 range",             1 <= grade_easy["grade"] <= 13)

hci_easy = hindi_complexity_index(EASY)
hci_hard = hindi_complexity_index(HARD)
t("HCI in 0-1 range",             0 <= hci_easy <= 1)
t("easy HCI < hard HCI",          hci_easy < hci_hard)

# ── Scorer API tests ──────────────────────────────────────────────────────────
result = rs.score(EASY)
t("score() returns dict",         isinstance(result, dict))
t("hrs key present",              "hrs" in result)
t("label key present",            "label" in result)
t("grade key present",            "grade" in result)
t("cbse_level key present",       "cbse_level" in result)
t("hci key present",              "hci" in result)
t("raw key present",              "raw" in result)
t("syllables_per_word key",       "syllables_per_word" in result)
t("conjunct_density key",         "conjunct_density" in result)

# compare() sorts easiest first
compared = rs.compare([HARD, EASY, MEDIUM])
t("compare() returns list",       isinstance(compared, list))
t("compare() sorts easy first",   compared[0]["hrs"] >= compared[-1]["hrs"])
t("compare length correct",       len(compared) == 3)

# batch_score
batch = rs.batch_score([EASY, MEDIUM, HARD])
t("batch_score returns list",     len(batch) == 3)
t("batch first is easy",          batch[0]["hrs"] > batch[2]["hrs"])

# is_appropriate_for_grade
t("easy text ok for grade 2",     rs.is_appropriate_for_grade(EASY, 2))
t("hard text not ok for grade 5", not rs.is_appropriate_for_grade(HARD, 5))

# simplify_suggestions
sugg = rs.simplify_suggestions(HARD)
t("suggestions is list",          isinstance(sugg, list))
t("suggestions not empty",        len(sugg) > 0)

# empty text raises ValueError
try:
    rs.score("")
    t("empty text raises error",  False)
except ValueError:
    t("empty text raises error",  True)

# ── Print results ─────────────────────────────────────────────────────────────
passed = sum(1 for _, r in results if r)
failed = [(n, r) for n, r in results if not r]
print(f"\nTests: {passed}/{len(results)} passed")
if failed:
    print("FAILED:", [n for n, _ in failed])
else:
    print("All tests passed! ✓")

# ── Print sample output ───────────────────────────────────────────────────────
print("\n── Sample output (easy text) ──────────────────────────────")
r = rs.score(EASY)
for k, v in r.items():
    if k != "raw":
        print(f"  {k:25}: {v}")

print("\n── HRS comparison across difficulty levels ────────────────")
for label, text in [("Easy", EASY), ("Medium", MEDIUM), ("Hard", HARD)]:
    r = rs.score(text)
    print(f"  {label:8}: HRS={r['hrs']:5.1f}  Grade={r['grade_label']:12}  Label={r['label']}")
