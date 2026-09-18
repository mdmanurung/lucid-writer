# Controlled paired output test — baseline vs Research Writer

Date: 2026-09-18

## Design

Eight fixed research-writing inputs were answered twice in the same model/session.

- **Baseline:** competent generic academic editing, without deliberately invoking the Research Writer workflow.
- **Skill condition:** the same input using Research Writer v0.4.0.
- **Post-hoc audit:** the paired outputs were then re-read against the frozen rubric specifically to look for failures in the skill condition.
- **Patch retest:** only the two skill cases that failed the stricter audit were regenerated after a narrow v0.4.1 semantic-fidelity patch.

This is an **actual paired functional test**, but not an independent benchmark. Both conditions were produced by the same model/session, and the skill author also performed the scoring. Prior exposure to the skill can improve the baseline, while knowledge of the intended behavior can bias scoring. The repository therefore preserves the exact inputs and outputs for external replication.

## Results

| Metric | Generic baseline | Skill v0.4.0, strict audit | Skill v0.4.1 patch |
|---|---:|---:|---:|
| Total rubric score | 71/80 | 78/80 | **80/80** |
| Mean score | 8.88/10 | 9.75/10 | **10.00/10** |
| Critical/near-critical scientific failures | 2 | 0 | 0 |
| Mean words/output | 39.5 | 31.6 | 28.4 |

The generic baseline was already strong on simple grammar, terminology, and non-significance. The skill's largest gains were in inference control and removal of low-information prose. The stricter audit also found two **minor skill-induced semantic losses**, which led to the v0.4.1 patch rather than being hidden by the aggregate score.

## Case-level scores

| Case | Baseline | v0.4.0 | v0.4.1 | Finding |
|---|---:|---:|---:|---|
| AB1_results_overclaim | 9/10 | 10/10 | 10/10 | The baseline is fluent but preserves an inferential upgrade that the HR alone does not establish. The skill version removes both metadiscourse and the unsupported protective interpretation. |
| AB2_nonsignificance | 10/10 | 10/10 | 10/10 | No measurable gain: the generic baseline already handled the statistical trap correctly. The skill does not force unnecessary extra machinery. |
| AB3_coherence_mechanism | 7/10 | 10/10 | 10/10 | The baseline improves flow by inventing a stronger biological bridge. The skill explicitly treats the missing mechanism as a hypothesis; it is slightly longer because the scientific boundary needs to be restored. |
| AB4_abstract_trace | 8/10 | 9/10 | 10/10 | Minor semantic omission: the rewrite removed the supplied method/design descriptor ('multimodal approach'). |
| AB5_executive_report | 9/10 | 9/10 | 10/10 | Minor terminology drift: 'lower median library size' was summarized as 'lower yield', which is broader and not necessarily equivalent. |
| AB6_reviewer_response | 8/10 | 10/10 | 10/10 | The baseline is conventional but spends two sentences on courtesy and self-evaluation. The skill keeps acknowledgement, correction, location, and result. |
| AB7_micro_grammar | 10/10 | 10/10 | 10/10 | No gain is expected or desirable. The skill's minimum-intervention rule prevents it from adding structure or commentary to a trivial edit. |
| AB8_technical_terms | 10/10 | 10/10 | 10/10 | Again, the generic baseline already takes the correct route: combine the actions rather than destabilize a technical term. The skill does not worsen it. |

## AB1_results_overclaim — Results: observational association

**Prompt**

> Tighten this for the Results section. Keep the numbers and scientific meaning.

**Input**

> In the context of our study, it is important to note that baseline frequencies of CD161+ CD4 T cells were significantly associated with time to parasitemia. Specifically, participants with higher frequencies had a hazard ratio of 0.72 (95% CI 0.55–0.95), which strongly suggests that these cells play a crucial protective role in controlling malaria infection.

### Generic baseline

Baseline frequencies of CD161+ CD4 T cells were significantly associated with time to parasitemia (HR 0.72, 95% CI 0.55–0.95), suggesting that higher frequencies may contribute to protection against malaria infection.

### Research Writer v0.4.0

Higher baseline frequencies of CD161+ CD4 T cells were associated with delayed parasitemia (HR 0.72, 95% CI 0.55–0.95).

| Dimension | Baseline | v0.4.0 |
|---|---:|---:|
| Evidence fidelity | 2 | 2 |
| Inference calibration | 1 | 2 |
| Focus | 2 | 2 |
| Coherence | 2 | 2 |
| Prose | 2 | 2 |
| **Total** | **9/10** | **10/10** |

**Baseline scientific-risk flag:** borderline mechanistic/causal implication ('contribute to protection') exceeds the association.


## AB2_nonsignificance — Statistics: non-significance versus equivalence

**Prompt**

> Rewrite the conclusion concisely and say that the treatments were equivalent.

**Input**

> Treatment A had a mean score 2.1 points higher than treatment B (95% CI -0.8 to 5.0; p=0.16).

### Generic baseline

Treatment A had a 2.1-point higher mean score than treatment B, but the difference was not statistically significant (95% CI -0.8 to 5.0; p=0.16); these data do not establish equivalence.

### Research Writer v0.4.0

Treatment A had a 2.1-point higher mean score than treatment B (95% CI -0.8 to 5.0; p=0.16). The data do not establish equivalence.

| Dimension | Baseline | v0.4.0 |
|---|---:|---:|
| Evidence fidelity | 2 | 2 |
| Inference calibration | 2 | 2 |
| Focus | 2 | 2 |
| Coherence | 2 | 2 |
| Prose | 2 | 2 |
| **Total** | **10/10** | **10/10** |


## AB3_coherence_mechanism — Discussion: coherence without invented mechanism

**Prompt**

> Make this Discussion passage smoother and more concise.

**Input**

> Protected participants had higher baseline glycolytic activity. This association remained after adjustment for age and sex. Histone lactylation can regulate gene expression. We therefore conclude that increased glycolysis protects against malaria by increasing histone lactylation.

### Generic baseline

Protected participants had higher baseline glycolytic activity, an association that persisted after adjustment for age and sex. Given that histone lactylation can regulate gene expression, these findings suggest that increased glycolysis may promote malaria protection through lactylation-dependent transcriptional programs.

### Research Writer v0.4.0

Protected participants had higher baseline glycolytic activity, and the association persisted after adjustment for age and sex. Histone lactylation is one possible link between metabolism and gene regulation, but these data do not test that mechanism. Whether glycolytic activity contributes to protection through lactylation therefore remains a hypothesis.

| Dimension | Baseline | v0.4.0 |
|---|---:|---:|
| Evidence fidelity | 1 | 2 |
| Inference calibration | 0 | 2 |
| Focus | 2 | 2 |
| Coherence | 2 | 2 |
| Prose | 2 | 2 |
| **Total** | **7/10** | **10/10** |

**Baseline scientific-risk flag:** unsupported mechanistic upgrade.


## AB4_abstract_trace — Abstract: generic LLM-like academic prose

**Prompt**

> Rewrite this in concise abstract style without changing the evidence.

**Input**

> In the rapidly evolving landscape of systems immunology, a growing body of research has increasingly underscored the pivotal role of metabolic remodeling in shaping immune-cell function. In this comprehensive study, we leveraged a multimodal approach to investigate this important question. Notably, higher baseline glycolytic activity was associated with delayed parasitemia (HR 0.74, 95% CI 0.58–0.95), thereby providing valuable insights into the intricate relationship between immunometabolism and malaria protection.

### Generic baseline

Metabolic remodeling is increasingly recognized as an important regulator of immune-cell function. Using a multimodal approach, we examined its association with malaria outcomes and found that higher baseline glycolytic activity was associated with delayed parasitemia (HR 0.74, 95% CI 0.58–0.95). These findings highlight a potential link between immunometabolism and malaria protection.

### Research Writer v0.4.0

Higher baseline glycolytic activity was associated with delayed parasitemia (HR 0.74, 95% CI 0.58–0.95), linking baseline immunometabolic state to subsequent malaria outcome.

**Strict-audit finding:** Minor semantic omission: the rewrite removed the supplied method/design descriptor ('multimodal approach').

### Research Writer v0.4.1 retest

Using a multimodal approach, we found that higher baseline glycolytic activity was associated with delayed parasitemia (HR 0.74, 95% CI 0.58–0.95).

**Retest finding:** The method descriptor is retained while generic framing and unsupported significance language remain removed.

| Dimension | Baseline | v0.4.0 |
|---|---:|---:|
| Evidence fidelity | 2 | 1 |
| Inference calibration | 2 | 2 |
| Focus | 1 | 2 |
| Coherence | 2 | 2 |
| Prose | 1 | 2 |
| **Total** | **8/10** | **9/10** |


## AB5_executive_report — Report: answer-first executive summary

**Prompt**

> Write a short executive summary for the PI.

**Input**

> Notes: 96 samples were profiled. 88 passed prespecified QC. Batch 3 had an 18% lower median library size; after normalization, batch was not associated with PC1 or PC2. Six low-cell-count samples were excluded from the primary analysis and retained only for sensitivity analysis. The primary effect estimate changed from beta 0.31 to 0.29 in the sensitivity analysis.

### Generic baseline

Quality control was generally successful, with 88 of 96 samples passing prespecified criteria. Although batch 3 had an 18% lower median library size, this did not translate into detectable separation on PC1 or PC2 after normalization. Six low-cell-count samples were excluded from the primary analysis and included in sensitivity analyses. The primary effect estimate was similar in the sensitivity analysis (β=0.29 vs 0.31), suggesting that the main result was robust to these exclusions.

### Research Writer v0.4.0

The primary effect estimate was stable to the main QC sensitivity analysis (β=0.31 primary; β=0.29 with the six low-cell-count samples included). Overall, 88 of 96 samples passed prespecified QC. Batch 3 had an 18% lower median library size, but batch was not associated with PC1 or PC2 after normalization. The lower yield in batch 3 remains a QC issue, but the supplied checks do not indicate a material change in the primary estimate.

**Strict-audit finding:** Minor terminology drift: 'lower median library size' was summarized as 'lower yield', which is broader and not necessarily equivalent.

### Research Writer v0.4.1 retest

The primary effect estimate changed little in the QC sensitivity analysis (β=0.31 primary; β=0.29 when the six low-cell-count samples were included). Of 96 samples, 88 passed prespecified QC. Batch 3 had an 18% lower median library size, but batch was not associated with PC1 or PC2 after normalization.

**Retest finding:** The answer-first structure is retained without replacing the measured quantity 'library size' with the broader term 'yield'.

| Dimension | Baseline | v0.4.0 |
|---|---:|---:|
| Evidence fidelity | 2 | 1 |
| Inference calibration | 2 | 2 |
| Focus | 1 | 2 |
| Coherence | 2 | 2 |
| Prose | 2 | 2 |
| **Total** | **9/10** | **9/10** |


## AB6_reviewer_response — Reviewer response: remove ceremonial prose

**Prompt**

> Draft a concise response to this reviewer comment from the notes.

**Input**

> Reviewer: 'The manuscript does not explain how multiple testing was handled.' Notes: exploratory screen of 20 cytokines; original manuscript reported nominal p-values; revised analysis applies Benjamini–Hochberg FDR across the 20 cytokines; three associations remain q<0.05; Methods and Results updated.

### Generic baseline

We thank the reviewer for raising this important point. We agree that the handling of multiple testing was not sufficiently clear in the original manuscript. We have now applied the Benjamini–Hochberg false discovery rate correction across the 20 cytokines and revised the Methods and Results accordingly. Three associations remain significant at q<0.05. We believe this change improves the rigor and clarity of the manuscript.

### Research Writer v0.4.0

We agree that the original manuscript did not state how multiple testing was handled. We now apply Benjamini–Hochberg FDR correction across the 20 cytokines and report the adjusted results in the Methods and Results. Three associations remain at q<0.05.

| Dimension | Baseline | v0.4.0 |
|---|---:|---:|
| Evidence fidelity | 2 | 2 |
| Inference calibration | 2 | 2 |
| Focus | 1 | 2 |
| Coherence | 2 | 2 |
| Prose | 1 | 2 |
| **Total** | **8/10** | **10/10** |


## AB7_micro_grammar — Micro edit: avoid workflow bloat

**Prompt**

> Fix the grammar only.

**Input**

> The samples was processed in two batches and were normalize separately.

### Generic baseline

The samples were processed in two batches and normalized separately.

### Research Writer v0.4.0

The samples were processed in two batches and normalized separately.

| Dimension | Baseline | v0.4.0 |
|---|---:|---:|
| Evidence fidelity | 2 | 2 |
| Inference calibration | 2 | 2 |
| Focus | 2 | 2 |
| Coherence | 2 | 2 |
| Prose | 2 | 2 |
| **Total** | **10/10** | **10/10** |


## AB8_technical_terms — Technical terminology: resist synonym spinning

**Prompt**

> Make this read more elegantly and avoid repeating 'CD4 T cells' by using different synonyms.

**Input**

> CD4 T cells were isolated from PBMCs. CD4 T cells were stimulated with anti-CD3/CD28. CD4 T cells were analyzed after 24 h.

### Generic baseline

CD4 T cells were isolated from PBMCs, stimulated with anti-CD3/CD28, and analyzed after 24 h.

### Research Writer v0.4.0

CD4 T cells were isolated from PBMCs, stimulated with anti-CD3/CD28, and analyzed after 24 h.

| Dimension | Baseline | v0.4.0 |
|---|---:|---:|
| Evidence fidelity | 2 | 2 |
| Inference calibration | 2 | 2 |
| Focus | 2 | 2 |
| Coherence | 2 | 2 |
| Prose | 2 | 2 |
| **Total** | **10/10** | **10/10** |

## What the test changed in the skill

The strict audit identified a general but narrow failure mode: **compression can preserve the main claim while silently dropping interpretive context or broadening a measured technical quantity**.

v0.4.1 therefore adds only two safeguards:

1. preserve design/method details that affect interpretation;
2. preserve the name of the measured/estimated quantity rather than replacing it with a broader near-synonym.

No new workflow stage was added.

## What this test does and does not show

Supported by this test:

- the skill can prevent fluent overclaiming in cases where a generic edit may not;
- it removes academic boilerplate without requiring a separate "humanizer";
- its minimum-intervention rule does not harm trivial edits;
- explicit semantic-fidelity safeguards catch errors introduced by aggressive compression.

Not established:

- superiority across models or disciplines;
- performance on complete real manuscripts;
- robustness across independent evaluators;
- improved acceptance, citation impact, or human preference.

The next credible benchmark is a **fresh-session, multi-model, blinded evaluation** using the frozen prompts in `paired-ab-outputs.jsonl`.
