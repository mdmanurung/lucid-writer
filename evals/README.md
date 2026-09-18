# Evaluation cases

`cases.jsonl` is a provider-agnostic behavioral evaluation set for Research Writer. It is intentionally separate from the repository-integrity tests.

Each case contains:

- `id` — stable case name;
- `prompt` — representative user request;
- `should_trigger` — whether Research Writer should be selected;
- `expect` — high-level behaviors that a grader should look for.

The cases cover routing, evidence preservation, citation discipline, causal language, right-sized workflow, report structure, review-only behavior, and reporting-guideline routing.

## Recommended evaluation procedure

For each supported host/model:

1. start a fresh session with Research Writer installed;
2. run each prompt with the minimum fixture material needed for that case;
3. score skill selection separately from output quality;
4. treat any invented citation, number, method, or result as a hard failure;
5. record model/host/version because routing behavior can change independently of the skill;
6. add a regression case before changing instructions to address a newly observed failure mode.

Suggested dimensions:

| Dimension | Pass criterion |
|---|---|
| Routing | skill triggers when relevant and stays out of unrelated creative/personal writing |
| Evidence fidelity | no unsupported strengthening, omission of material caveats, or invented evidence |
| Right-sized workflow | micro edits stay light; macro tasks perform structural/evidence checks |
| Argument | governing claim and support hierarchy are coherent when structure is requested |
| Reader clarity | prose becomes easier to follow without hiding uncertainty |
| Delivery integrity | document-wide requests propagate material changes across dependent artifacts |

The repository's `scripts/validate_repo.py` validates the **format and completeness of the eval corpus**; it does not run an LLM benchmark.


## LLM-trace safety

The `llm_trace_safe_cleanup` and `marker_not_blacklist` cases are important regressions:

- the model should improve generic prose without promising detector evasion;
- corpus-level lexical markers must not be treated as authorship proof or banned vocabulary;
- evidence, citations, numerical statements, uncertainty, and technical terms must survive the style pass.

## Coherence safety

The `coherence_no_new_claims` case tests whether the skill repairs logic and transitions without creating new scientific premises merely to connect the prose.
