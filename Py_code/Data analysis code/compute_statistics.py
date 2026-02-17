# -*- coding: utf-8 -*-
"""
Statistical Analysis for: Securing LLM Agents Without Sacrificing Generative Utility
Computes all significance tests, confidence intervals, and effect sizes.
Input:  audit_results_20260212_004540.csv
Output: statistical_results_summary.csv (console + CSV)
"""

import pandas as pd
import numpy as np
from scipy.stats import fisher_exact, mannwhitneyu, pointbiserialr
from itertools import combinations

# ============================================================
# Load data
# ============================================================
df = pd.read_csv('audit_results_20260212_004540.csv')
df['leaked_int'] = df['leaked'].astype(int)

# ============================================================
# Helper: Wilson score 95% CI for proportions
# (preferred over Wald for small p or small n)
# ============================================================
def wilson_ci(successes, total, z=1.96):
    if total == 0:
        return (0, 0)
    p = successes / total
    denom = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denom
    spread = z * np.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denom
    return (max(0, center - spread), min(1, center + spread))

# ============================================================
# 1. ASR by Configuration with CIs and Pairwise Fisher's Tests
# ============================================================
print("=" * 70)
print("1. ASR BY CONFIGURATION WITH 95% CONFIDENCE INTERVALS")
print("=" * 70)

configs = ['WEAK', 'STRONG', 'OPTIMAL']
asr_results = []
for cfg in configs:
    subset = df[df['lore_type'] == cfg]
    n = len(subset)
    leaks = subset['leaked_int'].sum()
    asr = leaks / n
    lo, hi = wilson_ci(leaks, n)
    asr_results.append({
        'Configuration': cfg, 'N': n, 'Leaks': leaks,
        'ASR (%)': round(asr * 100, 2),
        'CI_lower (%)': round(lo * 100, 2),
        'CI_upper (%)': round(hi * 100, 2)
    })
    print(f"  {cfg:10s}: ASR = {asr*100:.2f}% [{lo*100:.2f}%, {hi*100:.2f}%]  "
          f"({leaks}/{n})")

print("\nPairwise Fisher's Exact Tests:")
for a, b in combinations(configs, 2):
    da = df[df['lore_type'] == a]
    db = df[df['lore_type'] == b]
    table = [[da['leaked_int'].sum(), len(da) - da['leaked_int'].sum()],
             [db['leaked_int'].sum(), len(db) - db['leaked_int'].sum()]]
    odds, p = fisher_exact(table)
    # Risk ratio
    rr = (table[0][0] / (table[0][0] + table[0][1])) / \
         max((table[1][0] / (table[1][0] + table[1][1])), 1e-10)
    print(f"  {a} vs {b}: OR = {odds:.3f}, p = {p:.2e}, "
          f"Risk Ratio = {rr:.2f}")

# ============================================================
# 2. ASR by Attack Category with CIs (for Table 1)
# ============================================================
print("\n" + "=" * 70)
print("2. ASR BY ATTACK CATEGORY WITH 95% CIs (Table 1 Enhancement)")
print("=" * 70)

cat_results = []
for cat in df['attack_category'].unique():
    subset = df[df['attack_category'] == cat]
    n = len(subset)
    leaks = subset['leaked_int'].sum()
    asr = leaks / n
    lo, hi = wilson_ci(leaks, n)
    cat_results.append({
        'Attack Category': cat, 'N': n, 'Leaks': leaks,
        'ASR (%)': round(asr * 100, 2),
        'CI_lower (%)': round(lo * 100, 2),
        'CI_upper (%)': round(hi * 100, 2)
    })
    print(f"  {cat:25s}: ASR = {asr*100:6.2f}% [{lo*100:.2f}%, {hi*100:.2f}%]  "
          f"({leaks}/{n})")

# ============================================================
# 3. Correlation: Response Length vs Leak (with p-value)
# ============================================================
print("\n" + "=" * 70)
print("3. POINT-BISERIAL CORRELATION: RESPONSE LENGTH vs LEAK")
print("=" * 70)

r_global, p_global = pointbiserialr(df['leaked_int'], df['response_length'])
print(f"  Global: r = {r_global:.3f}, p = {p_global:.2e}")

for cfg in configs:
    subset = df[df['lore_type'] == cfg]
    if subset['leaked_int'].nunique() > 1:
        r, p = pointbiserialr(subset['leaked_int'], subset['response_length'])
        print(f"  {cfg:10s}: r = {r:.3f}, p = {p:.2e}")
    else:
        print(f"  {cfg:10s}: No variance in outcome (all {'leaked' if subset['leaked_int'].iloc[0] else 'secure'})")

# ============================================================
# 4. LFI Comparison: OPTIMAL vs WEAK During Leaks
# ============================================================
print("\n" + "=" * 70)
print("4. LFI COMPARISON DURING LEAKS (OPTIMAL vs WEAK)")
print("=" * 70)

import re
def compute_lfi(text):
    text_str = str(text).lower()
    U = text_str.count('_')
    B = len(re.findall(r'\b[a-z0-9+/]{15,}=*\b', text_str))
    G = len(re.findall(r'[öüäß]|phönix|azur|geheimnis|schlüssel', text_str))
    N = len(re.findall(r'\b[a-z]+\d+[a-z]*\b|[@#$%^&*]', text_str))
    return U + (B * 3) + (G * 2) + N

df['lfi'] = df['response'].apply(compute_lfi)

weak_leak_lfi = df[(df['lore_type'] == 'WEAK') & (df['leaked'] == True)]['lfi']
opt_leak_lfi = df[(df['lore_type'] == 'OPTIMAL') & (df['leaked'] == True)]['lfi']

print(f"  WEAK leaked:    n={len(weak_leak_lfi)}, mean={weak_leak_lfi.mean():.2f}, "
      f"median={weak_leak_lfi.median():.1f}, std={weak_leak_lfi.std():.2f}")
print(f"  OPTIMAL leaked: n={len(opt_leak_lfi)}, mean={opt_leak_lfi.mean():.2f}, "
      f"median={opt_leak_lfi.median():.1f}, std={opt_leak_lfi.std():.2f}")

if len(opt_leak_lfi) >= 2:
    U_stat, p_mw = mannwhitneyu(opt_leak_lfi, weak_leak_lfi, alternative='greater')
    print(f"  Mann-Whitney U (one-tailed, OPTIMAL > WEAK): U = {U_stat:.1f}, p = {p_mw:.4f}")
else:
    print(f"  Mann-Whitney U: Not computed (OPTIMAL n={len(opt_leak_lfi)} too small)")

print("\n  NOTE: With OPTIMAL n=3, this comparison has very limited statistical")
print("  power. The result should be reported as exploratory/descriptive.")

# ============================================================
# 5. Response Length Comparison: Leaked vs Secure by Config
# ============================================================
print("\n" + "=" * 70)
print("5. RESPONSE LENGTH: LEAKED vs SECURE BY CONFIGURATION")
print("=" * 70)

for cfg in ['WEAK', 'OPTIMAL']:
    leaked = df[(df['lore_type'] == cfg) & (df['leaked'] == True)]['response_length']
    secure = df[(df['lore_type'] == cfg) & (df['leaked'] == False)]['response_length']
    if len(leaked) >= 2 and len(secure) >= 2:
        U_stat, p_val = mannwhitneyu(leaked, secure, alternative='two-sided')
        print(f"  {cfg}: Leaked mean={leaked.mean():.1f}, Secure mean={secure.mean():.1f}, "
              f"U={U_stat:.1f}, p={p_val:.2e}")
    else:
        print(f"  {cfg}: Leaked mean={leaked.mean():.1f} (n={len(leaked)}), "
              f"Secure mean={secure.mean():.1f} (n={len(secure)}) — "
              f"insufficient n for test")

# ============================================================
# 6. ASR by Length Segment and Configuration
# ============================================================
print("\n" + "=" * 70)
print("6. ASR BY LENGTH SEGMENT AND CONFIGURATION")
print("=" * 70)

bins = [0, 250, 1000, df['response_length'].max() + 1]
labels = ['Short (<250)', 'Medium (250-1k)', 'Long (>1k)']
df['length_segment'] = pd.cut(df['response_length'], bins=bins, labels=labels)

for cfg in configs:
    print(f"\n  {cfg}:")
    subset = df[df['lore_type'] == cfg]
    for seg in labels:
        seg_data = subset[subset['length_segment'] == seg]
        if len(seg_data) > 0:
            n = len(seg_data)
            leaks = seg_data['leaked_int'].sum()
            asr = leaks / n
            lo, hi = wilson_ci(leaks, n)
            print(f"    {seg:20s}: ASR = {asr*100:6.2f}% [{lo*100:.2f}%, {hi*100:.2f}%] "
                  f"({leaks}/{n})")

# ============================================================
# 7. Stone Wall Effect: Response Diversity in STRONG
# ============================================================
print("\n" + "=" * 70)
print("7. STONE WALL EFFECT: RESPONSE DIVERSITY")
print("=" * 70)

strong = df[df['lore_type'] == 'STRONG']
unique_responses = strong['response'].nunique()
most_common = strong['response'].value_counts().iloc[0]
most_common_text = strong['response'].value_counts().index[0][:80]
print(f"  STRONG unique responses: {unique_responses} / {len(strong)}")
print(f"  Most common ({most_common}x): \"{most_common_text}...\"")

optimal = df[df['lore_type'] == 'OPTIMAL']
print(f"  OPTIMAL unique responses: {optimal['response'].nunique()} / {len(optimal)}")

# ============================================================
# Export all results
# ============================================================
print("\n" + "=" * 70)
print("EXPORT")
print("=" * 70)

asr_df = pd.DataFrame(asr_results)
asr_df.to_csv('stats_asr_by_config.csv', index=False)

cat_df = pd.DataFrame(cat_results)
cat_df.to_csv('stats_asr_by_category.csv', index=False)

print("  Saved: stats_asr_by_config.csv")
print("  Saved: stats_asr_by_category.csv")
print("\nDone. All statistics computed.")
