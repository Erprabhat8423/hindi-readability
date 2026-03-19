"""
validate.py — Statistical Validation of hindi-readability v0.3.0
=================================================================
Validates the HRS formula against a 49-sentence human-graded corpus.

Run: python validation/validate.py

Results:
  Pearson r  = 0.81  (strong correlation with human judgment)
  Spearman p = 0.75  (rank correlation)
  MAE        = 1.67  (mean absolute error in grade levels)
  ±2 accuracy = 73.5% (36/49 sentences within 2 grades)
"""

import sys, os, csv, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from hindi_readability import ReadabilityScorer

rs = ReadabilityScorer()

# ── Load dataset ──────────────────────────────────────────────────
dataset = []
csv_path = os.path.join(os.path.dirname(__file__), "../data/validation_dataset.csv")
with open(csv_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        dataset.append({
            "text":             row["text"],
            "source":           row["source"],
            "human_grade":      int(row["human_grade"]),
            "human_difficulty": int(row["human_difficulty"]),
        })

print(f"Dataset loaded: {len(dataset)} sentences\n")

# ── Score every sentence ──────────────────────────────────────────
results = []
for item in dataset:
    try:
        score = rs.score(item["text"])
        results.append({
            **item,
            "hrs":               score["hrs"],
            "pred_grade":        score["grade"],
            "label":             score["label"],
            "hci":               score["hci"],
            "conjunct_density":  score["conjunct_density"],
            "syllables_per_word":score["syllables_per_word"],
        })
    except Exception as e:
        print(f"Error on: {item['text'][:30]} — {e}")

n = len(results)

# ── Pearson correlation ───────────────────────────────────────────
hrs_vals  = [r["hrs"] for r in results]
diff_vals = [11 - r["human_difficulty"] for r in results]  # invert: high=easy

mean_hrs  = sum(hrs_vals)  / n
mean_diff = sum(diff_vals) / n
cov  = sum((h-mean_hrs)*(d-mean_diff) for h,d in zip(hrs_vals,diff_vals)) / n
s_h  = math.sqrt(sum((h-mean_hrs)**2  for h in hrs_vals)  / n)
s_d  = math.sqrt(sum((d-mean_diff)**2 for d in diff_vals) / n)
pearson = cov / (s_h * s_d) if s_h * s_d > 0 else 0

# ── Spearman rank correlation ─────────────────────────────────────
def rank(vals):
    sv = sorted(enumerate(vals), key=lambda x: x[1])
    r  = [0]*len(vals)
    for ri, (oi, _) in enumerate(sv):
        r[oi] = ri+1
    return r

d2 = sum((a-b)**2 for a,b in zip(rank(hrs_vals), rank(diff_vals)))
spearman = 1 - (6*d2) / (n*(n**2-1))

# ── Accuracy metrics ──────────────────────────────────────────────
mae      = sum(abs(r["pred_grade"]-r["human_grade"]) for r in results) / n
within_1 = sum(1 for r in results if abs(r["pred_grade"]-r["human_grade"]) <= 1)
within_2 = sum(1 for r in results if abs(r["pred_grade"]-r["human_grade"]) <= 2)

# ── Per-level breakdown ───────────────────────────────────────────
levels = {
    "Easy (1–2)":     [r for r in results if r["human_difficulty"] <= 2],
    "Simple (3–4)":   [r for r in results if 3 <= r["human_difficulty"] <= 4],
    "Standard (5–6)": [r for r in results if 5 <= r["human_difficulty"] <= 6],
    "Hard (7–8)":     [r for r in results if 7 <= r["human_difficulty"] <= 8],
    "Expert (9–10)":  [r for r in results if r["human_difficulty"] >= 9],
}

# ── Print results ─────────────────────────────────────────────────
print("=" * 60)
print("  VALIDATION — hindi-readability v0.3.0")
print("=" * 60)
print(f"\n  Dataset        : {n} sentences (NCERT Cl.1-12 + Constitution + News)")
print(f"  Pearson r      : {pearson:.4f}  (HRS vs human rating)")
print(f"  Spearman rho   : {spearman:.4f}  (rank correlation)")
print(f"  Mean Abs Error : {mae:.2f} grades")
print(f"  Accuracy ±1    : {within_1/n*100:.1f}%  ({within_1}/{n})")
print(f"  Accuracy ±2    : {within_2/n*100:.1f}%  ({within_2}/{n})")

interp = "STRONG" if pearson >= 0.8 else "MODERATE-STRONG" if pearson >= 0.6 else "MODERATE"
print(f"\n  Correlation    : {interp} — formula reliably tracks human judgment")

print(f"\n  {'Level':<18} {'N':>4}  {'Avg HRS':>8}  {'MAE':>6}  {'±1 Acc':>7}")
print(f"  {'-'*50}")
for name, items in levels.items():
    if not items: continue
    avg_hrs  = sum(r["hrs"] for r in items) / len(items)
    lmae     = sum(abs(r["pred_grade"]-r["human_grade"]) for r in items) / len(items)
    lacc     = sum(1 for r in items if abs(r["pred_grade"]-r["human_grade"]) <= 1)
    print(f"  {name:<18} {len(items):>4}  {avg_hrs:>8.1f}  {lmae:>6.2f}  {lacc/len(items)*100:>6.0f}%")

# ── Save CSV ──────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "validation_results.csv")
with open(out, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=[
        "text","source","human_grade","human_difficulty",
        "hrs","pred_grade","label","hci","conjunct_density","syllables_per_word"
    ])
    w.writeheader()
    w.writerows(results)

print(f"\n  Results saved → validation/validation_results.csv")
print(f"\n  Cite in report:")
print(f'  "Pearson r={pearson:.2f}, Spearman ρ={spearman:.2f}, MAE={mae:.2f}')
print(f'   grades, ±2 accuracy={within_2/n*100:.1f}% on 49-sentence corpus."')
