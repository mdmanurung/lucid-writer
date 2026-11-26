# Lucid Writer QC checklist

- [ ] Every reported number has a `<!-- claims -->` line, and `/mycelium-extra:verify` `report` shows no mismatch for each cited plan hash.
- [ ] Every figure cited as evidence has a producer in `provenance/outputs-<hash>.tsv`; `/mycelium-extra:verify` `stale` lists none of them.
- [ ] The manuscript-audit result has no `block` status, or each block is listed as a Blocker.
- [ ] `/mycelium-extra:verify` `report` shows no decision-log `block`: every row of `logs/decisions.tsv` has a plan row. No method is reported that the log does not show.
- [ ] Every finding in the text reproduces under `/mycelium-extra:verify` `reproduce`. An unreproduced finding is dropped; an inconclusive one is worded as a description and carries `[AUTHOR CHECK]` or `[EVIDENCE NEEDED]` (markers as defined in the lucid-writer skill). No marker remains at release.
- [ ] Each headline number has its `<!-- explain -->` lines, and a factor with no inspected figure carries `[EVIDENCE NEEDED]`.
- [ ] No `[EVIDENCE NEEDED]` or `[CITATION NEEDED]` remains, or each one is listed as unresolved.
- [ ] Each citation verdict says whether it rests on full text or metadata only.
- [ ] Title and abstract claim no more than Results show.
- [ ] Preflight verdict recorded, with its "not checked" list.
