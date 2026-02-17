# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pointbiserialr
import re

# --- CONFIGURATION ---
DATA_FILE = 'XXX'  # Replace with your CSV filename

# 1. Load the dataset
df = pd.read_csv(DATA_FILE)

# 1. COMPREHENSIVE LINGUISTIC FRAGMENTATION INDEX (LFI)
def detect_lfi(text):
    text_str = str(text).lower()
    # Factor A: Underscores (Technical Secret)
    underscores = text_str.count('_')
    # Factor B: Base64 (Encoding Attack)
    b64_strings = len(re.findall(r'\b[a-z0-9+/]{15,}=*\b', text_str))
    # Factor C: German Shift (Translation Attack)
    german_markers = len(re.findall(r'[öüäß]|phönix|azur|geheimnis|schlüssel', text_str))
    # Factor D: Spiret Glitches (Model Stress)
    glitches = len(re.findall(r'\b[a-z]+\d+[a-z]*\b|[@#$%^&*]', text_str))
    
    return underscores + (b64_strings * 3) + (german_markers * 2) + glitches

# 2. SEGMENTATION & CORRELATION PROCESSING
df['leaked_int'] = df['leaked'].astype(int)
df['lfi_score'] = df['response'].apply(detect_lfi)

# Create length segments to find the "Security Sweet Spot"
# We define Short as Technical, Medium as Defensive, and Long as Creative
bins = [0, 250, 1000, df['response_length'].max() + 1]
labels = ['Short (<250)', 'Medium (250-1k)', 'Long (>1k)']
df['length_segment'] = pd.cut(df['response_length'], bins=bins, labels=labels)

# 3. STATISTICAL SUMMARY
# Calculate Global Correlation
corr, _ = pointbiserialr(df['leaked_int'], df['response_length'])
print(f"Global Correlation (Length vs. Leak): {corr:.3f}")

# Calculate Leak Rates by Segment (The U-Shaped Risk Profile)
leak_matrix = df.pivot_table(index='length_segment', columns='lore_type', 
                             values='leaked_int', aggfunc='mean') * 100

# --- VISUALIZATION ---
plt.figure(figsize=(16, 7))

# Plot A: Leak Rate by Length (Visualizing the "Creative Over-sharing" in Optimal Lore)
plt.subplot(1, 2, 1)
leak_matrix.plot(kind='bar', ax=plt.gca(), cmap='berlin')
plt.title('Attack Success Rate (ASR) by Length Segment')
plt.ylabel('Leak Rate (%)')
plt.xlabel('Response Length (Characters)')
plt.xticks(rotation=0)

# Plot B: Fragmentation vs. Length
# This shows if technical "noise" is higher in short or long failures
plt.subplot(1, 2, 2)
sns.scatterplot(data=df[df['leaked']==True], x='response_length', y='lfi_score', 
                hue='lore_type', style='lore_type', s=100)
plt.title('Linguistic Fragmentation in Successful Leaks')
plt.ylabel('LFI (Noise Score)')
plt.xlabel('Character Count')

plt.tight_layout()
plt.savefig('aethelgard_security_sweet_spot.png')

# 4. EXPORT FOR PAPER
# This CSV will show the exact counts for those 3 Optimal "Long" leaks
summary_report = df.groupby(['lore_type', 'length_segment']).agg({
    'leaked': 'sum',
    'leaked_int': 'count'
}).rename(columns={'leaked': 'leak_count', 'leaked_int': 'total_trials'})
summary_report.to_csv('segmented_security_report.csv')