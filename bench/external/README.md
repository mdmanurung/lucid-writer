# External labelled pairs

Plan for testing the skill on sentence pairs that other people labelled. Nothing here is
run against a model yet, and no data is committed.

## Why

The prose bench's gold labels are ours, from one labeller. A published corpus with
independent labels lets us check two things: whether a model sees that a derived sentence is
stronger than its source, and whether our ceiling labels agree with outside ones.

## Corpora and licences

Checked 2026-11-13.

| Corpus | Licence found | Redistribute? |
|---|---|---|
| Wright and Augenstein (EMNLP 2021), `copenlu/scientific-exaggeration-detection` on Hugging Face | The dataset card metadata says `license:gpl-3.0` (Hugging Face API). The GitHub root listing showed no LICENSE file; I did not open one directly. The rows come from the InSciOut data, which figshare lists as CC BY 4.0 (figshare API, article 903704, version 5). The OSF registration of Bratton et al. (v8qhn) links a licence resource named "CC-By Attribution 4.0 International", and the paper states CC BY 4.0 for the replication data. `insciout.zip` (downloaded, md5 matched the record) has no licence or README file inside. It holds the coded press releases and news articles themselves (for example a Mail Online article), so third-party text sits beside the CC BY record; I found no statement about its rights. | Unresolved: a GPL-3.0 tag on the card against CC BY upstream, and third-party article text in the archive. Treated as not clearly allowed. |
| Yu, Li and Wang (EMNLP 2019), `junwang4/causal-language-use-in-science` on GitHub | The repo has a GPL-3.0 LICENSE file. No data licence or usage statement is given, and the README does not say whether GPL covers `data/pubmed_causal_language_use.csv`. | Not clearly allowed. |

Rule applied: where redistribution is not clearly allowed, commit a script that downloads
and samples at run time, never the data. `sample_pairs.py` does that and writes to
`bench/external/sample/`, which is gitignored. It retries server errors and exits with one
line if a download fails.

## What each corpus holds

- Exaggeration: 663 abstract/press-release pairs (the paper's Table 6 counts: 113
  downplays, 406 same, 144 exaggerates). The Hugging Face viewer shows a `train` split of
  100 and a `test` split of 563; `--split all` returns all 663. The dataset's GitHub README
  says `insciout_test.jsonl` is the paper's test data. I downloaded both GitHub files
  (`insciout_test.jsonl`, 563 rows; `insciout_train.jsonl`, 100 rows) and compared them with
  the Hugging Face splits: the pair sets are identical and the splits do not overlap. So the
  Hugging Face `test` split is the paper's test set. The paper's text says 553 test pairs
  remained after sampling 100; the data has 563, which is what 663 minus 100 gives, so I
  read "553" as a typo. One row is a pair:
  `abstract_conclusion` with `abstract_strength`, and `press_release_conclusion` with
  `press_release_strength`. The paper defines `exaggeration_label` as `downplays` when the
  press-release strength is below the abstract's, `same` when equal and `exaggerates` when
  above. In a 20-row sample the field matched that rule every time, and `sample_pairs.py`
  records both.
- Causal language: one CSV, columns `sentence,label`. The paper reports 3,126 annotated
  sentences, of which 3,061 hold a single relation type; the README's counts (998
  correlational, 213 conditional causal, 494 direct causal, 1,356 no relationship) sum to
  3,061. It has no source/derived pairs and no identifier column, so it labels single
  sentences only. The paper names the four classes but gives no numeric codes; the order
  below comes from the repo README alone.

## Label definitions

From Table 1 of Yu et al. (2019), quoted:

| Class | Definition |
|---|---|
| No relationship | "No correlation or causation relationship is mentioned in the statement." Per the paper, sentences about a tool's function or about study limitations get this label even when they contain causal cues. |
| Correlational | "The statement describes the association between variables, but causation cannot be explicitly stated." |
| Conditional causal | "The statement shows that one variable directly changes the other. However, the relation carries an element of doubt in it, which is normally via hedges or modalities." |
| Direct causal | "The statement says that the independent variable directly alters the dependent variable." |

Wright and Augenstein use the four strength levels of Li et al. (2017), "An NLP Analysis of
Exaggerated Claims in Science News" (NLPmJ 2017, pages 106-111, ACL Anthology W17-4219):
0 statement of no relationship, 1 statement of correlation, 2 conditional statement of
causation, 3 statement of causation. Li et al. number their classes 1, 2, 4 and 6, so the
0-3 numbering is Wright's renumbering. Table 1 of Li et al., quoted:

| Level (Li category) | Definition |
|---|---|
| 0 (1) statement of no relationship | "Explicitly stating there is no relationship" |
| 1 (2) statement of correlation | "The IV and DV are associated, but causation cannot be explicitly stated" (category 3, an ambiguous relationship, is merged in) |
| 2 (4) conditional statement of causation | "Causal statements show that the IV directly changes the DV. Conditional causal statements carry an element of doubt in them." (category 5, statements with "can", is merged in) |
| 3 (6) statement of causation | "This statement says that the IV directly alters the DV." |

IV and DV are independent and dependent variable. Li et al. dropped their category 0 ("no
relationship is mentioned", 2 examples), and Wright's table maps Sumner's matching code to no
level. So a Wright 0 is an explicit null statement. I did not read Sumner et al.'s own
definitions.

## Label mapping to the ceiling vocabulary

A corpus label rates the strength of a sentence's wording. A ceiling says what the evidence
allows. The table gives the lowest ceiling the wording would need. A causal verb under a
hedge still needs a CAUSAL ceiling (`references/evidence.md`, "Common unsafe upgrades"), so
both conditional classes map to CAUSAL. Label 0 maps to DESCRIPTIVE, the floor of the
vocabulary (see below). Nothing maps to PREDICTIVE or MECHANISTIC. **Unsure** marks a
judgement call for you.

| Exaggeration label | Wording | Ceiling needed | Sure? |
|---|---|---|---|
| 0 | statement of no relationship | DESCRIPTIVE | sure, from the rows (below) |
| 1 | statement of correlation | ASSOCIATIVE | sure |
| 2 | conditional statement of causation | CAUSAL | sure: Li et al. define it as a causal statement that carries doubt, and a hedged causal verb still needs CAUSAL |
| 3 | statement of causation | CAUSAL | sure |

| Causal-language label (README order) | Class | Ceiling needed | Sure? |
|---|---|---|---|
| 0 | no relationship | DESCRIPTIVE | sure: by definition no relation is mentioned |
| 1 | direct causal | CAUSAL | sure |
| 2 | conditional causal | CAUSAL | sure |
| 3 | correlational | ASSOCIATIVE | sure (the paper's cue list includes "predictor", which would need PREDICTIVE; the lowest ceiling is still ASSOCIATIVE) |

What label 0 holds. I read 8 of the 87 abstract conclusions and 6 of the 98 press-release
conclusions with strength 0 (seed 1, all 663 pairs). They are null findings ("did not differ
significantly", "a lack of evidence for an impact", "does not protect against eczema"),
plain descriptions ("Ever use of e-cigarettes increased during 2012-2014", "This device
was found to have an unacceptably high revision rate"), a projection ("160,000 more people
... will need palliative care by 2040") and a recommendation. None claims a correlation or
a cause, and none needs more than a DESCRIPTIVE ceiling. (Li et al.'s definition of level 0,
above, is an explicit null statement. The rows hold plain descriptions as well, and both fit a
DESCRIPTIVE ceiling.) This reverses an earlier plan to map label 0 to a level outside the
vocabulary. The Yu et al. "no relationship" class holds
the same mix (it includes background sentences, which need no ceiling at all, so DESCRIPTIVE
is again the floor).

The two corpora number the classes differently (3 is causation in one, correlational in
the other). `sample_pairs.py` keeps a separate map for each.

## Sampling plan

About 20 items per corpus, drawn with a fixed seed and spread over the labels. The
exaggeration sample is stratified on `exaggeration_label` (same, exaggerates, downplays),
not on the 0-3 strength labels. If a label has too few rows the others fill the quota, and
the script warns when it writes fewer than `--n`.

```bash
python3.12 bench/external/sample_pairs.py --self-test        # free, no network
python3.12 bench/external/sample_pairs.py exaggeration --n 20  # 20 pairs from the test split
python3.12 bench/external/sample_pairs.py causal --n 20        # 20 sentences
```

The scripts need Python 3.11 or newer. On RHEL 8 `python3` is 3.6; use `python3.12`.

Use of the sample: give a model the source sentence and the derived sentence, ask whether
the derived one claims more than the source, and compare with the corpus label. Compare the
no-skill arm and the skill arm. This is a closed-vocabulary probe, like the main bench, so
it can only show recognition, not rewriting. All eight mappings are marked sure, but the
label-0 reading rests on 14 sampled rows.

## Not done

- Reading Sumner et al.'s (2014) own definitions, the source of Li et al.'s categories.
- Rights in the third-party press-release and news text inside `insciout.zip`.
- Any model run. Cost is zero until you ask for one.
