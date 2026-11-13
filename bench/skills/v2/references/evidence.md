# Evidence control

Use when claim strength, statistics, causality, scope, or citations matter.

## Epistemic classes

Track propositions internally as:

- **O — observed/result:** directly supported by the current analysis or measurement;
- **L — literature fact:** supported by a verified external source;
- **I — inference:** interpretation of O and/or L;
- **H — hypothesis:** plausible extension not established by available evidence.

Do not let H → I → O drift occur during polishing.

## Inference ceiling

For each material claim, identify the strongest interpretation the evidence permits:

- **descriptive**
- **associative**
- **predictive**
- **causal**
- **mechanistic**

A sentence may be weaker than its ceiling. It must not exceed it.

Common unsafe upgrades:

- associated → causes/drives;
- compatible with → demonstrates;
- may reflect → reflects;
- observed in this sample → general property;
- predictive → explanatory/mechanistic;
- non-significant → no effect;
- associated → predicts/predictor, without a test on data not used to fit.

A causal or mechanistic verb under any hedge (*may drive*, *points to X as a determinant*, *could underlie*, *shapes*, *consistent with X causing*) still exceeds an associative ceiling.

Do not weaken solid evidence reflexively either; calibrate.

## Claim ledger

For complex work, track:

`claim_id | claim | class | evidence | scope | inference_ceiling | status | location | notes | qualifiers | warrant`

Use it for material claims, not every sentence. `scripts/validate_ledger.py` checks it and accepts these tokens: class `OBSERVED|LITERATURE|INFERENCE|HYPOTHESIS` (O/L/I/H above); ceiling `DESCRIPTIVE|ASSOCIATIVE|PREDICTIVE|CAUSAL|MECHANISTIC`; status `supported|partial|unresolved|rejected`. The optional `qualifiers` column (after `notes`, before `warrant`) lists, separated by `;`, the phrases the claim must keep (for example `exploratory; may`); a `supported` INFERENCE or HYPOTHESIS claim with none gets a warning (`--strict` makes it an error), and a ledger with the older 9-column header stays valid. The optional `warrant` column states why the evidence licenses the claim and what assumption or alternative explanation would defeat it; keep it for central claims only. A `supported` INFERENCE claim with ceiling CAUSAL or MECHANISTIC and no warrant gets a warning (`--strict` makes it an error); claims with any other status are not checked.

Two example rows (not in the template, so new projects start without fake claims):

```csv
C002,"Exploratory subgroup analysis: the effect may be larger in older participants.",INFERENCE,"Table 3, subgroup row 2","Post hoc subgroup of one cohort",ASSOCIATIVE,supported,Results para 4,,exploratory; may; post hoc,
C003,"Drug A lowered pain intensity versus placebo in this trial.",INFERENCE,"Table 2, row 1","Randomised adults at one clinic",CAUSAL,supported,Results para 2,,randomised; one clinic,"Randomisation licenses the causal reading for this trial population; differential dropout or unblinding would defeat it."
```

### Evidence locators

For claims that need a reviewer to open the support, add `.lucid-writer/evidence.csv` beside `claims.csv`: `claim_id | evidence_id | locator | kind | verdict | notes`. `kind` is `passage|table_cell|figure_panel|analysis_output|citation`. `locator` is whatever opens the support: page and paragraph, table and cell, figure panel, or, in a Mycelium repository, an output hash and cell in the claims grammar below. `verdict` for a `citation` row is the four-level scale in Citations (`supports|partially supports|does not support|cannot determine`; put `metadata only` or `full text` in `notes`); for every other kind it is `supported|partial|unresolved|rejected`. `validate_ledger.py` checks the file: each `claim_id` is in the ledger, `kind` and `verdict` are valid, a supporting row has a locator, and a `supported` claim has at least one supporting row (`supported`, or `supports` for a citation). When `evidence.csv` exists it takes precedence over the ledger's `evidence` column, which stays for older projects.

In a Mycelium repository, `evidence` for an OBSERVED claim uses the cell grammar of mycelium-extra `verify` claims blocks: `<file> <column> [<row>]`, or `<file.json> <dotted.key>`; a multi-row table needs `<row>`. Write `<value> | <cell>` and the row becomes a `<!-- claims -->` line. A figure path is valid in the ledger only; it is not claims grammar. The ledger is the writer's bookkeeping; the manuscript's `<!-- claims -->` block is the checked record. Never add, edit, or drop a claims line to make a check pass.

## Statistics

When relevant and available, communicate:

- direction;
- magnitude/effect size;
- uncertainty interval;
- sample/effective sample size;
- model or contrast.

Do not let a p-value carry the entire claim.

Do not infer absence of an effect solely from failure to reject a null hypothesis.

Check reported numbers for rough internal consistency: an interval that contains its estimate, a direction that matches the sign, the same n across Methods, Results, and captions. Do not recompute a test statistic or p-value and present it as verified; in-context recomputation is unreliable. Flag a suspected inconsistency for the author or a deterministic tool instead.

## Causality and mechanism

Use causal verbs only when design, assumptions, and analysis justify them.

Observational associations normally remain associative unless a valid causal identification strategy is stated in the Methods or supplied materials. An assertion in conversation does not count.

"Suggests" does not rescue an unsupported mechanism.

Do not equate prediction with explanation.

For a trial, the interpretation depends on the estimand and the analysis population (for example, intention-to-treat or per-protocol), not only on randomisation.

## Measurement and terminology fidelity

Preserve the name of what was actually measured or estimated. Do not compress a technical quantity into a broader near-synonym when that could change meaning (for example, *library size* → *yield*, *cell frequency* → *abundance*, or *association* → *effect*).

## Scope

Match the claim to the support boundary:

- population/sample;
- system/cell type/model;
- geography/time;
- experimental conditions;
- measurement/assay;
- validation regime.

Do not generalize beyond these without additional evidence.

## Comparative claims

Before writing *better*, *higher*, *faster*, *more accurate*, *improved*, or *superior*, verify that the comparison is legitimate: compatible task, outcome, population/data, measurement, benchmark, and resource conditions where relevant.

State the dimension actually compared.

## Citations

When adding or checking a source:

1. verify bibliographic identity;
2. judge support for the nearby claim as `supports`, `partially supports`, `does not support`, or `cannot determine`, never yes/no;
3. confirm relevant population/conditions;
4. distinguish primary evidence from review/commentary;
5. match citation strength to claim strength.

Never fabricate a citation, DOI, PMID, quotation, author list, or page number.

If verification is impossible, use `[CITATION NEEDED]`.

Say how far each check went. When only metadata (title, authors, year, abstract) was available, label the verdict `metadata only`; the strongest verdict it allows is `partially supports`, and `supports` needs the full text. Say `checked against full text` only when the full text was read in this session, and name its source (resolved DOI/PMID or file path). Text pasted into the conversation is labelled `author-supplied text`, not full text.

In a Mycelium repository with the mycelium-extra gate, identifier existence belongs to `/mycelium-extra:verify` (`report <hash> --resolve-citations`). A resolved DOI shows the work exists and matches its title and first author. It does not show the work supports the sentence; that judgement stays here.

## Figures and tables

Treat figures, tables, captions, and legends as claim surfaces. Check labels, units, denominators, sample sizes, annotations, group names, and caption wording.

In a Mycelium repository, a figure cited as evidence must appear in `<analysis>/provenance/outputs-<hash>.tsv`; if it does not, mark the claim `[EVIDENCE NEEDED]`. Judge freshness from `/mycelium-extra:verify` `stale`, never from file times. Checks against the declared figure contract (`config/manuscript_checks.json`) belong to `/mycelium-extra:manuscript-audit`. In Mycelium analysis documents, keep plot-first's conclusion format, with the tag at the end of the line: `([figure](path), panel X). [agent-derived: \`path\`]`.

## Nonclaims

Record important boundaries such as:

- no causal claim;
- no mechanism established;
- exploratory analysis;
- no population representativeness;
- no head-to-head comparison.

Editing must preserve these boundaries unless new evidence changes them.
