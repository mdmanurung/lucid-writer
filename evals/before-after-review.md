# Before/after output review

This is a controlled **in-session qualitative benchmark**, not a blinded or independent model comparison. The same underlying model produced the examples. Its purpose is to expose whether the revised skill creates clearer decision rules and fewer failure opportunities.

## Case 1 — Results: generic prose + causal overreach

### Input

> Interestingly, participants with higher baseline CD161+ CD4 T-cell frequencies showed a significantly delayed time to parasitaemia (HR 0.72, 95% CI 0.55–0.95, p=0.018). Taken together, these findings demonstrate that CD161+ CD4 T cells play a crucial protective role against malaria infection.

### Representative unconstrained polish

> Notably, higher baseline CD161+ CD4 T-cell frequencies were significantly associated with delayed parasitaemia (HR 0.72, 95% CI 0.55–0.95, p=0.018), underscoring the crucial protective role of these cells in malaria infection.

### Research Writer v0.4

> Higher baseline CD161+ CD4 T-cell frequencies were associated with delayed parasitaemia (HR 0.72, 95% CI 0.55–0.95; p=0.018). This association is consistent with a relationship between this phenotype and parasite control but does not establish a causal protective role.

| Criterion | Unconstrained | v0.4 |
|---|---|---|
| Numeric parity | pass | pass |
| Association kept associative | partial: wording still implies protection | pass |
| Generic framing removed | fail | pass |
| Caveat explicit | fail | pass |

**Finding:** the useful difference is epistemic, not cosmetic.

## Case 2 — Discussion: generic significance language

### Input

> Our findings shed light on the complex interplay between metabolic remodeling and cytokine responses. Interestingly, IFN-γ, IL-2, TNF, and IL-10 were positively associated with CPT1A, ATGL, and GLUT1 and negatively associated with ATP5A. These robust findings underscore the importance of immunometabolism and pave the way for future studies.

### Representative unconstrained polish

> Our findings highlight the intricate interplay between cytokine responses and metabolic remodeling. Notably, IFN-γ, IL-2, TNF, and IL-10 were positively associated with CPT1A, ATGL, and GLUT1 and negatively associated with ATP5A, underscoring the central role of immunometabolism and providing a foundation for future investigation.

### Research Writer v0.4

> IFN-γ, IL-2, TNF, and IL-10 were positively associated with CPT1A, ATGL, and GLUT1 and inversely associated with ATP5A. These coordinated associations link cytokine responses to the measured metabolic proteins, but they do not establish mechanism or directionality.

| Criterion | Unconstrained | v0.4 |
|---|---|---|
| Observed associations preserved | pass | pass |
| Unsupported importance rhetoric | fail | pass |
| New mechanistic claim added | risk | no |
| Stock model-like phrases | several | none |
| Scientific qualification | absent | explicit |

## Case 3 — Non-significant result

### Input

> The adjusted mean difference was 2.1 units (95% CI -0.8 to 5.0; p=0.16). The groups were therefore equivalent.

### Representative unconstrained polish

> The adjusted mean difference was small and non-significant (2.1 units, 95% CI -0.8 to 5.0; p=0.16), indicating that the groups were equivalent.

### Research Writer v0.4

> The adjusted mean difference was 2.1 units (95% CI -0.8 to 5.0; p=0.16). These data do not establish a difference at the chosen significance threshold, but they also do not demonstrate equivalence without a prespecified equivalence margin and appropriate analysis.

| Criterion | Unconstrained | v0.4 |
|---|---|---|
| Estimate preserved | pass | pass |
| Correct interpretation of p>0.05 | fail | pass |
| Unsupported equivalence claim | retained | removed |

## Case 4 — Coherence request that invites a false bridge

### Input

> Higher X was associated with Y. Mitochondrial remodeling may alter Y. Add a smooth transition showing that X changes Y through mitochondrial remodeling.

### Representative unconstrained polish

> Higher X was associated with Y, suggesting that X may influence Y through mitochondrial remodeling.

### Research Writer v0.4

> Higher X was associated with Y. Mitochondrial remodeling is one possible explanation for this association, but the available evidence does not establish that it mediates the relationship.

| Criterion | Unconstrained | v0.4 |
|---|---|---|
| Smooth prose | pass | pass |
| New mechanistic relation implied | yes | no |
| Evidence boundary visible | no | yes |
| Transition used as hidden claim | yes | no |

## Summary

The revised skill improves the behaviors that matter most: claim strength stays tied to evidence; missing evidence remains visible; coherence edits cannot invent scientific bridges; generic prose is removed through specificity rather than "humanization"; and local edits stay local.

These examples do **not** establish superiority across models or domains. A proper external benchmark should run the repository's behavioral cases across target models with blinded human scoring.

## Mechanical cross-check

The bundled conservative linter was run on the representative outputs. It is intentionally limited to mechanical/style cues; it does **not** detect inferential errors such as non-significance being misread as equivalence.

| Output | Words | Style flags |
|---|---:|---:|
| Case 1 unconstrained | 30 | 1 |
| Case 1 v0.4 | 38 | 0 |
| Case 2 unconstrained | 44 | 1 |
| Case 2 v0.4 | 37 | 0 |
| Case 3 unconstrained | 22 | 0 |
| Case 3 v0.4 | 40 | 0 |

The longer v0.4 outputs in Cases 1 and 3 are deliberate: the added words carry necessary epistemic qualification. The optimization target is not minimum word count; it is the shortest wording that preserves a defensible scientific claim.
