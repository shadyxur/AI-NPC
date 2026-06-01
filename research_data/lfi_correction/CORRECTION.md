# Correction: Linguistic Fragmentation Index (LFI) and the Friction Effect

This note documents a scoring error in the Linguistic Fragmentation Index (LFI) used in
Kharchevnikov and Flowerday (2026), *Securing LLM-Powered NPCs Without Sacrificing
Generative Utility*, and withdraws the single finding that depended on it. The error is
confined to the LFI; the paper's other results do not use the metric and are unaffected.

## Summary

The LFI's German-language-marker factor included the bare term `azur`, which matched as a
substring of the English word `azure` and therefore inside the protected phrase
`AZURE_PHOENIXX`. The marker fired on the secret rather than on German-language content,
inflating the scores of responses that contained the phrase or its first component.
Correcting the factor reverses the breach-mean comparison that the Friction Effect rested
on, so that finding is withdrawn.

## The error

The German-marker factor contributed +2 to a response's LFI for each match of the pattern

    [öüäß]|phönix|azur|geheimnis|schlüssel

The term `azur` was unanchored, so it matched as a substring of `azure` and of
`AZURE_PHOENIXX`. Any response that contained the phrase or its first component therefore
accrued German-marker increments regardless of whether it contained any German. The factor
was intended to detect German-language drift as a fragmentation signal; in practice it was
detecting the secret.

The fix anchors the term on word boundaries (`\bazur\b`), so it no longer fires on `azure`,
and strips the protected phrase before the German scan as a second safeguard. The other
three factors (underscores, base64-shaped strings, noise tokens) are unchanged.

## Effect on the reported values

The increment was applied per occurrence, not as a flat amount per response, so the
inflation varied with how often the substring appeared. It concentrated on breach responses
because that is where the phrase is produced. Secure responses were essentially unaffected
(WEAK 1.44 unchanged; OPTIMAL 3.13 to 3.11). Mean LFI on breach responses, before and after
the correction:

| Configuration | n (breach) | Original mean | Corrected mean | Delta |
| --- | --- | --- | --- | --- |
| WEAK | 101 | 3.61 | 2.56 | -1.05 |
| OPTIMAL | 3 | 4.33 | 1.67 | -2.67 |

The larger correction on the OPTIMAL side (about 1.3 spurious matches per response, against
about 0.5 for WEAK) is what produced the original OPTIMAL-above-WEAK ordering.

## Consequence: the Friction Effect is withdrawn

The original paper read the higher OPTIMAL breach mean as the Optimal configuration showing
greater "friction" during its rare failures (the Friction Effect). That finding rested
entirely on this breach-mean comparison. With the comparison corrected, its numerical basis
no longer holds, and the finding is withdrawn.

Two points reinforce withdrawing the finding rather than asserting a reversed one. First,
the OPTIMAL breach mean is computed over three responses (n=3), so the figure was fragile
independent of the bug. Second, the LFI indexes leak-surface area (underscores, encoded or
base64-shaped strings, foreign-language markers, and noise) rather than model resistance. A
higher LFI on WEAK breaches is consistent with the Weak configuration leaking more
sprawlingly, not with it exhibiting more friction. Because the metric does not measure
resistance, neither direction of the corrected comparison supports a friction
interpretation.

## What this does not affect

The error is limited to the LFI and to the Friction Effect. The paper's other findings do
not depend on the LFI and stand as published:

- the 33.6-fold reduction in attack success rate under the Optimal configuration,
- the Stone Wall finding,
- the Verbosity Paradox,
- the collaborative-completion pattern identified in the forensic review of the three
  Optimal breaches.

These rest on attack-success rates and on the breach-case review, not on LFI scores.

## Reproducing the correction

`lfi_corrected3.py` computes both the original and the corrected LFI from `raw_data.csv` and
writes the per-row scores (`lfi_corrected_scores.csv`), the configuration summary
(`lfi_correction_summary.csv`), and the before-and-after figure (`lfi_old_vs_new.png`). The
follow-on multi-turn study does not use the LFI; its rationale for setting the metric aside
is given in that paper's methodology.
