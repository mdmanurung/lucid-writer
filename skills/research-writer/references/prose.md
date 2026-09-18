# Prose: coherence, concision, and generic-model cleanup

Use for editing, flow/coherence, or requests to remove generic AI/LLM-sounding prose.

## Core rule

Improve **expression and connections without changing the science**.

Preserve claims, numbers, citations, scope, uncertainty, stable technical terms, and design/method context needed to interpret the evidence unless verified evidence requires a change.

## 1. Coherence

Check from large scale to small scale:

### Whole text
- contradiction or scope drift;
- abstract/title stronger than body;
- duplicated arguments with inconsistent interpretations;
- terminology changing meaning.

### Paragraph
Each paragraph should normally make one main move. Look for topic jumps, missing links, unclear referents, orphan claims, and unsignaled shifts from result to interpretation.

Repair in this order:

1. reorder existing sentences;
2. replace vague referents with concrete nouns;
3. delete repetition;
4. split overloaded sentences;
5. add a short connective phrase only when the relation is already supported.

### Seams
At section and paragraph boundaries, make the relationship visible only when needed: continuation, contrast, consequence, qualification, example, scale shift, or next question.

Do not use *therefore*, *because*, *despite*, or similar language to invent a relation.

## 2. Direct research prose

Prefer:

- substantive point before framing;
- concrete subjects and informative verbs;
- subject and main verb reasonably close;
- domain-standard terminology;
- active voice when the actor matters, passive when process/result is the natural focus;
- qualifications placed next to the claim they limit;
- important new information in positions of emphasis.

Useful default: given/active information → new information.

Long sentences are acceptable when their hierarchy is clear. Short sentences are not automatically better.

## 3. Cut low-information prose

Scrutinize, rather than mechanically ban:

- *It is important to note...*
- *Interestingly / Notably...*
- *Taken together...*
- *In this context...*
- *sheds light on*
- *underscores the importance*
- *highlights the need*
- *provides valuable insights*
- *paves the way*
- undefined *robust*, *novel*, *comprehensive*, *multifaceted*, *intricate*, *pivotal*

Replace rhetoric with the actual result, relation, or implication when supported.

Also remove duplicate summaries and endings that merely restate the paragraph.

## 4. Generic model-like patterns

Audit for clusters of:

- repeated three-part rhetorical lists without analytical reason;
- repeated *not only ... but also ...* or *while X, Y* templates;
- many paragraphs opening the same way;
- excessive stock transitions;
- excessive em dashes used as generic connective punctuation;
- surface synonym variation that destabilizes technical terms.

These are writing cues, **not evidence of AI authorship**.

Do not optimize for AI-detector scores, promise "undetectability", insert fake errors, or manufacture personal quirks.

## 5. Voice

If `.research-writer/voice.md` exists, use observed author/team habits as positive style evidence.

Voice never overrides:

- evidence;
- uncertainty;
- stable technical terminology;
- venue/reporting requirements.

## Final parity check

After editing, compare before/after for:

- facts and numbers;
- direction/magnitude;
- claim strength;
- causal/mechanistic language;
- scope;
- caveats;
- citations;
- technical terminology.

If a stylistic change alters any of these unintentionally, revert it.
