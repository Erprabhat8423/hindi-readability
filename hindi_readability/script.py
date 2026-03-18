"""
script.py — Devanagari Script Analyser
=======================================
Counts the building blocks of Hindi text that determine reading difficulty:

  - Matras       : vowel diacritics attached to consonants  (ि ी ु ू े ै ो ौ etc.)
  - Virama       : halant ् — joins two consonants into a conjunct
  - Conjuncts    : two or more consonants merged (e.g. क्ष  त्र  ज्ञ)
  - Syllables    : every independent vowel OR consonant+vowel unit
  - Anusvara/
    Visarga      : nasal/aspiration marks — add phonetic weight

Research basis
--------------
In Devanagari every consonant carries an implicit /a/ vowel (schwa).
A matra overrides that default vowel.  A virama (U+094D) suppresses
the vowel completely and glues the consonant to the next one — forming
a conjunct.  Conjuncts are the primary marker of textual complexity
in Hindi: they appear mainly in Sanskrit-origin (tatsama) words which
are harder to read than native Prakrit-derived (tadbhava) words.

Unicode ranges used
-------------------
Devanagari block: U+0900 – U+097F
  Vowels (independent): U+0904 – U+0914
  Consonants:           U+0915 – U+0939, U+0958 – U+095F (nukta variants)
  Matras (dependent):   U+093E – U+094C, U+094E – U+094F  (also U+0955-U+0957)
  Virama (halant):      U+094D
  Anusvara:             U+0902
  Visarga:              U+0903
  Chandrabindu:         U+0901
"""

import re
import unicodedata
from typing import Dict


# ── Unicode code-point sets ────────────────────────────────────────────────
VIRAMA       = "\u094D"   # ् halant — the conjunct-former
ANUSVARA     = "\u0902"   # ं
CHANDRABINDU = "\u0901"   # ँ
VISARGA      = "\u0903"   # ः
AVAGRAHA     = "\u093D"   # ऽ

# Independent vowels (अ आ इ ई … औ)
INDEPENDENT_VOWELS = set(chr(c) for c in range(0x0904, 0x0915))

# Consonants (क … ह + nukta variants)
CONSONANTS = set(chr(c) for c in range(0x0915, 0x093A)) | \
             set(chr(c) for c in range(0x0958, 0x0960))

# Dependent vowel signs / matras (ा ि ी ु ू ृ े ै ो ौ ॆ ॊ …)
MATRAS = set(chr(c) for c in range(0x093E, 0x094D)) | \
         {chr(0x094E), chr(0x094F)} | \
         set(chr(c) for c in range(0x0955, 0x0958))


def analyse(text: str) -> Dict[str, int]:
    """
    Analyse a Hindi text string and return raw script-level counts.

    Returns
    -------
    dict with keys:
        total_chars      : total non-whitespace characters
        consonants       : number of consonant code-points
        independent_vowels: standalone vowel letters
        matras           : dependent vowel signs (ि ी ु ू ा …)
        viramas          : halant signs ् (each one forms part of a conjunct)
        conjuncts        : number of conjunct clusters (= number of viramas
                           not at end of word, roughly)
        anusvara         : ं count
        visarga          : ः count
        syllables        : estimated syllable count (see _count_syllables)
        words            : whitespace-delimited tokens
        sentences        : splits on । ॥ . ? !
    """
    text = unicodedata.normalize("NFC", text)

    counts: Dict[str, int] = {
        "total_chars":        0,
        "consonants":         0,
        "independent_vowels": 0,
        "matras":             0,
        "viramas":            0,
        "conjuncts":          0,
        "anusvara":           0,
        "visarga":            0,
        "syllables":          0,
        "words":              0,
        "sentences":          0,
    }

    for ch in text:
        if ch.isspace():
            continue
        counts["total_chars"] += 1
        if ch in CONSONANTS:
            counts["consonants"] += 1
        elif ch in INDEPENDENT_VOWELS:
            counts["independent_vowels"] += 1
        elif ch in MATRAS:
            counts["matras"] += 1
        elif ch == VIRAMA:
            counts["viramas"] += 1
        elif ch == ANUSVARA or ch == CHANDRABINDU:
            counts["anusvara"] += 1
        elif ch == VISARGA:
            counts["visarga"] += 1

    # Conjuncts = sequences of  consonant + virama + consonant  (chain possible)
    # We count each virama that is followed by a consonant as one conjunct bond.
    i = 0
    chars = list(text)
    while i < len(chars) - 1:
        if chars[i] == VIRAMA:
            if i + 1 < len(chars) and chars[i + 1] in CONSONANTS:
                counts["conjuncts"] += 1
        i += 1

    counts["syllables"]  = _count_syllables(text)
    counts["words"]      = len([w for w in text.split() if w.strip()])
    counts["sentences"]  = max(1, len([s for s in re.split(r"[।॥.!?]+", text) if s.strip()]))

    return counts


def _count_syllables(text: str) -> int:
    """
    Estimate syllable count in Devanagari text.

    Rule (based on Devanagari phonology):
      Each syllable has exactly ONE vowel nucleus, which is either:
        (a) an independent vowel letter, OR
        (b) a consonant carrying its implicit /a/ (not followed by virama), OR
        (c) a consonant + matra combination.
      Virama suppresses the schwa → that consonant does NOT form its own syllable.
      Anusvara / visarga extend the preceding syllable but don't add a new one.
    """
    syllables = 0
    chars = list(unicodedata.normalize("NFC", text))
    i = 0
    while i < len(chars):
        ch = chars[i]
        if ch in INDEPENDENT_VOWELS:
            syllables += 1
        elif ch in CONSONANTS:
            # peek ahead: is this consonant killed by a virama?
            next_ch = chars[i + 1] if i + 1 < len(chars) else ""
            if next_ch == VIRAMA:
                pass  # virama kills the schwa → no syllable nucleus here
            else:
                syllables += 1  # implicit /a/ or explicit matra → one syllable
        i += 1
    return max(syllables, 1)


def syllables_per_word(text: str) -> float:
    """Average syllables per word — a key difficulty signal."""
    data = analyse(text)
    return round(data["syllables"] / max(data["words"], 1), 4)


def conjunct_density(text: str) -> float:
    """Conjuncts per 100 words — higher = more Sanskrit-heavy = harder."""
    data = analyse(text)
    return round(data["conjuncts"] / max(data["words"], 1) * 100, 4)
