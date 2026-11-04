# Patterns: generic model prose in research writing

Use when a request asks to remove AI/LLM-sounding prose, or when an edit finds several of these patterns in one passage. `prose.md` §4 points here.

Each pattern is a default choice: the phrase that fits the most readers and subjects. A writer choosing for one reader and one result makes uneven, specific choices. The patterns are writing cues, **not evidence of AI authorship**. Do not optimise for detector scores, insert errors, or vary rhythm for its own sake.

## How to use the list

Patterns in group A justify an edit on one sighting. A pattern marked *weak alone* needs other patterns in the same passage before you act.

Every sentence kept must add a fact, a step, a qualification or a reason the reader did not already have.

Edit only expression. A pattern fix never changes a number, a citation, a claim's strength, its scope, or a caveat. Run the parity check in `prose.md` after every pass.

Return only the final text, as non-negotiable 8 in `SKILL.md` requires. Do not return a draft, a list of remaining patterns, or a change log unless asked.

## Science overrides

These general-prose fixes are wrong in research writing. The evidence rules in `SKILL.md` and `evidence.md` win.

| General fix | In research prose |
|---|---|
| Cut stacked qualifiers | Keep every hedge that carries real uncertainty: design limits, sample size, a CI crossing a threshold, an untested alternative. Cut only hedges that repeat each other ("could potentially possibly"). |
| Replace "associated with" by the actual relationship | In a correlational result, "associated with" **is** the actual relationship. Upgrade it only when the design supports a stronger verb. |
| Prefer active voice | Methods use passive by convention. Use active when the actor matters. |
| Cut "studies show" | Name the study with its citation, or insert `[CITATION NEEDED]`. Do not delete the claim silently and do not invent a source. |
| Ban the listed AI words | `robust`, `key`, `landscape`, `enhance`, `interplay`, `highlight`, `gate`, `significant` have technical meanings. Flag only the figurative or undefined use. |
| Never use dashes | Keep dashes in ranges (0.55–0.95), compound names and author pairs. Scrutinise only a text full of em dashes used as all-purpose connectors. |

## A. Staging instead of stating (act on one sighting)

**A1. Contrast against a claim no one made.** "Not only X but also Y"; "not X but Y"; "This does not mean X. It means Y."; "X rather than merely Y". The negative half inflates the positive half. State Y. Keep the contrast when X is a belief the reader or the literature actually holds, and cite it.

> Before: These results are not merely descriptive; they reveal a fundamental mechanism of immune regulation.
> After: These results describe [what was measured]. (Any mechanistic claim needs its own evidence.)

**A2. Closers that restate.** A last sentence or one-line paragraph that names what the paragraph just showed ("This highlights the importance of...", "These findings are significant."), the same closer after each section, or a row of fragments. Cut it. Keep a final sentence that adds a consequence, a limit or the next question.

**A3. Aphorisms and fake depth.** "At its core", "the real question is", "what truly matters", "X is the language of Y", "lies at the heart of". Replace with the specific claim.

**A4. Staged run-ups.** "Here we explore...", "Let us now turn to...", "It is worth considering...", "In this section we will discuss...". Start with the content. A roadmap sentence is fine in a long Introduction when the venue expects one.

**A5. Arguing with no one.** "This is not to say...", "To be clear...", "One might be tempted to...", "It would be easy to conclude..." with no source for the view rejected. Remove the defence, or attribute and answer the view.

## B. Rhythm by rule

**B1. Forced triads.** Three adjectives, three nouns or three parallel sentences where the evidence has one or two parts ("novel, robust and scalable"). Keep three items only when there are three.

**B2. Repeated openers.** Several sentences or paragraphs in a row opening the same way ("We found... We observed... We showed..."; "Notably, ... Notably, ..."). Merge or reorder. Do not ban the word.

**B3. Em dashes as the default connector.** *Weak alone.* Replace a dash with the connector that names the relation: comma, colon, parentheses, "because", "so".

**B4. Stacked qualifiers.** *Weak alone.* See the science override: cut repeats, keep each uncertainty that the evidence carries.

## C. Inflation and borrowed authority

**C1. Inflated significance.** "Plays a pivotal role", "marks a paradigm shift", "sheds light on", "underscores the importance", "paves the way", "holds great promise", "opens new avenues". State the result and its supported implication, or cut.

**C2. Overused words.** delve, intricate, multifaceted, tapestry, testament, meticulous, pivotal, crucial, showcase, unveil, realm, and figurative robust, landscape, key. Use the plain word or the measured quantity. *Weak alone* unless several cluster.

**C3. Shallow -ing riders.** A clause bolted onto a result: "..., highlighting the role of X", "..., suggesting a central function", "..., underscoring its importance". The rider usually upgrades the claim. Cut it, or make it a separate sentence with its own support.

> Before: IL-10 was elevated in responders, highlighting its central role in protection.
> After: IL-10 was elevated in responders.

**C4. Borrowed authority.** "Studies have shown", "it is well established", "experts agree", "growing evidence suggests", "it is widely accepted" without a citation. Cite the studies or insert `[CITATION NEEDED]`.

**C5. Avoiding is and has.** "Serves as", "stands as", "acts as a" (figurative), "boasts", "features", "represents a". Use *is* or *has*. Keep "acts as" for a measured function (an enzyme acts as a catalyst).

**C6. Sales language.** Groundbreaking, cutting-edge, unprecedented, powerful, state-of-the-art, first-ever without a supporting comparison. Remove, or keep with the comparison that supports it.

## D. Formatting by rule

**D1. Bold labels on every item.** Lists where each item starts with a bold label and colon that repeat the content. Turn into prose, or keep the list without bold.

**D2. Decorative headings.** Title Case, emojis, arrows, a rule between every section, a heading restated in the first sentence below it. Use the venue's heading style; cut the restating sentence.

## E. Leftovers from chat and drafting

Remove these outright.

**E1. Chat residue.** "Certainly!", "Here is a revised version", "I hope this helps", "Let me know if...", "As an AI...". It is the surest pattern and easy to miss when it wraps real content.

**E2. Knowledge-limit hedges and guesses.** "As of my last update", "based on available information", "while details are limited", "it is believed that", "likely" filling a gap with no source. State what the source does not show, or mark `[EVIDENCE NEEDED]`.

**E3. Writing about the document.** "This section is organised as follows", "the table below compares", "this paragraph was revised to". Keep one roadmap where the venue expects it. Cut descriptions the reader can see.

## When not to act

Leave a pattern alone inside a quotation, a title, a defined term, or a passage that discusses the phrase. Leave it where the author's voice profile (`.lucid-writer/voice.md`) shows it as a deliberate habit, unless it changes claim strength. Several patterns together are the signal; one is usually an ordinary choice.

## Source

Adapted from `blader/humanizer` (Siqi Chen, MIT), which builds on Wikipedia's "Signs of AI writing" (WikiProject AI Cleanup). Re-expressed for research prose with the science overrides above. See `docs/methodology.md`.
