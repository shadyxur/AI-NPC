# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the dataset
# Update the filename as needed
df = pd.read_csv('audit_results_20260212_004540.csv')

# --- DATA PRE-PROCESSING ---
# Ensure 'leaked' column is actual Boolean (True/False)
# This handles cases where CSV loads them as strings "TRUE" or "FALSE"
if df['leaked'].dtype == 'object':
    df['leaked'] = df['leaked'].astype(str).str.strip().str.upper() == 'TRUE'

# 2. Global Metric: Attack Success Rate (ASR)
total_asr = df['leaked'].mean() * 100
print(f"Global Attack Success Rate: {total_asr:.2f}%")

# 3. Performance by Lore Type (The Core Variable)
lore_comparison = df.groupby('lore_type').agg(
    total_trials=('leaked', 'count'),
    total_leaks=('leaked', 'sum'),
    asr=('leaked', 'mean')
).reset_index()
lore_comparison['asr'] *= 100

# 4. Vulnerability by Attack Category
cat_analysis = df.groupby('attack_category').agg(
    total_trials=('leaked', 'count'),
    leaks=('leaked', 'sum'),
    asr=('leaked', 'mean')
).sort_values(by='asr', ascending=False).reset_index()
cat_analysis['asr'] *= 100

# 5. Auditor Calibration (Confidence vs. Reality)
# High confidence should ideally have near-zero leaks (True Negatives)
conf_matrix = pd.crosstab(df['confidence'], df['leaked'], margins=True)

# --- VISUALIZATION ---
plt.style.use('seaborn-v0_8-whitegrid')
fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# Chart 1: ASR per Lore
sns.barplot(data=lore_comparison, x='lore_type', y='asr', ax=axes[0,0], palette='coolwarm')
axes[0,0].set_title('ASR by Lore Configuration', fontweight='bold')
axes[0,0].set_ylabel('Success Rate (%)')

# Chart 2: Top Vulnerable Categories
sns.barplot(data=cat_analysis.head(10), x='asr', y='attack_category', ax=axes[0,1], palette='flare')
axes[0,1].set_title('Top 10 Attack Categories by Success Rate', fontweight='bold')

# Chart 3: Severity Analysis
sns.countplot(data=df[df['leaked'] == True], x='lore_type', hue='leak_type', ax=axes[1,0])
axes[1,0].set_title('Leak Severity Distribution', fontweight='bold')

# Chart 4: Confidence Reliability
sns.barplot(data=df, x='confidence', y='leaked', ax=axes[1,1], palette='viridis', errorbar=None)
axes[1,1].set_title('Mean Leak Rate by Auditor Confidence', fontweight='bold')
axes[1,1].set_ylabel('Leak Probability')

plt.tight_layout()
plt.savefig('aethelgard_final_plots.png')
print("Charts saved to 'aethelgard_final_plots.png'.")

# 6. Export Results for Paper
lore_comparison.to_csv('summary_lore.csv', index=False)
cat_analysis.to_csv('summary_categories.csv', index=False)