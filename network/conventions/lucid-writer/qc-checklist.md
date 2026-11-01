# Lucid Writer QC checklist

- [ ] Every reported number has a `<!-- claims -->` line, and `/mycelium-extra:verify` `report` shows no mismatch for each cited plan hash.
- [ ] Every figure cited as evidence has a producer in `provenance/outputs-<hash>.tsv`; `/mycelium-extra:verify` `stale` lists none of them.
- [ ] The manuscript-audit result has no `block` status, or each block is listed as a Blocker.
- [ ] No `[EVIDENCE NEEDED]` or `[CITATION NEEDED]` remains, or each one is listed as unresolved.
- [ ] Each citation verdict says whether it rests on full text or metadata only.
- [ ] Title and abstract claim no more than Results show.
- [ ] Preflight verdict recorded, with its "not checked" list.
