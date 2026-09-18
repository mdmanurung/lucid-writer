# Methodological sources and design provenance

This skill is an original synthesis. These sources explain the principles behind it; they are not runtime dependencies.

## Scientific and academic writing

### Gopen & Swan — reader expectations

Gopen, G. D., & Swan, J. A. (1990). The science of scientific writing. *American Scientist, 78*(6), 550–558.

Contribution used here: scientific clarity depends on reader expectations, information placement, topic continuity, and positions of emphasis.

### Mensh & Kording — central contribution and structure

Mensh, B., & Kording, K. (2017). Ten simple rules for structuring papers. *PLOS Computational Biology, 13*(9), e1005619.  
https://doi.org/10.1371/journal.pcbi.1005619

Contribution used here: organize scientific communication around a central contribution and reader-oriented structure across document scales.

### Swales — research-space introductions

Swales, J. M. (1990). *Genre Analysis: English in Academic and Research Settings*. Cambridge University Press.

Contribution used here: introductions establish a research territory, identify a niche, and occupy that niche with the present work.

### Sword — readable scholarly prose

Sword, H. (2012). *Stylish Academic Writing*. Harvard University Press.

Contribution used here: rigorous academic writing does not require inflated, abstract, or impersonal prose; structural and stylistic choices can improve readability.

### Pinker — cognitive approach to style

Pinker, S. (2014). *The Sense of Style: The Thinking Person's Guide to Writing in the 21st Century*. Viking.

Contribution used here: write for the reader rather than from the writer's private knowledge state; prefer concrete, intelligible prose over rigid folklore about style.

### Minto — hierarchical argument architecture

Minto, B. (2009 edition and earlier editions). *The Pyramid Principle: Logic in Writing and Thinking*. Pearson/Financial Times Prentice Hall.

Contribution used here: answer-first reasoning where appropriate, question–answer hierarchy, and logically grouped support. Research Writer does not force consulting conventions onto research-paper genres.



### Kobak et al. — LLM-associated vocabulary in biomedical writing

Kobak, D., González-Márquez, R., Horvát, E.-Á., & Lause, J. (2025). Delving into LLM-assisted writing in biomedical publications through excess vocabulary. *Science Advances*. PubMed PMID: 40601754.  
https://pubmed.ncbi.nlm.nih.gov/40601754/

Contribution used here: corpus-level evidence that the post-ChatGPT biomedical literature shows abrupt excess use of style vocabulary. Research Writer uses these observations only as review cues; it does not infer authorship from individual words or documents.

### Cheng et al. — corpus comparison of AI and human academic prose

Cheng and colleagues (2024). A corpus-driven comparative analysis of AI in academic discourse: Investigating ChatGPT-generated academic texts in social sciences. *Lingua, 312*, 103838.  
https://doi.org/10.1016/j.lingua.2024.103838

Contribution used here: caution against flowery vocabulary, formulaic sequences, and surface synonym substitution as substitutes for genuine academic style.

## Research reporting standards

### EQUATOR Network

EQUATOR Network. *Reporting guidelines library*.  
https://www.equator-network.org/reporting-guidelines/

Contribution used here: route manuscripts to the reporting standard appropriate to the study design and use the current authoritative checklist for completeness.

### CONSORT 2025

Hopewell, S., Chan, A.-W., Collins, G. S., et al. (2025). CONSORT 2025 statement: updated guideline for reporting randomised trials. *BMJ, 389*, e081123.  
https://doi.org/10.1136/bmj-2024-081123

Current-version note used here: CONSORT 2025 supersedes CONSORT 2010 for randomised-trial reports.

### PRISMA 2020

Page, M. J., McKenzie, J. E., Bossuyt, P. M., et al. (2021). The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. *BMJ, 372*, n71.  
https://doi.org/10.1136/bmj.n71

### ARRIVE 2.0

Percie du Sert, N., Hurst, V., Ahluwalia, A., et al. (2020). The ARRIVE guidelines 2.0: Updated guidelines for reporting animal research. *PLOS Biology, 18*(7), e3000410.  
https://doi.org/10.1371/journal.pbio.3000410

### TRIPOD+AI

Collins, G. S., Moons, K. G. M., Dhiman, P., et al. (2024). TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ, 385*, e078378.  
https://doi.org/10.1136/bmj-2023-078378

## Agent-skill architecture

### Anthropic Agent Skills

Anthropic. (2025). *Equipping agents for the real world with Agent Skills*.  
https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

Design principles used here:

- `SKILL.md` as a discoverable entry point;
- progressive disclosure;
- references and scripts loaded only when needed;
- deterministic code for mechanical tasks;
- evaluation-driven iteration.

### OpenAI Skills / Agent Plugins

OpenAI Developers. *Skills* and *Plugins* documentation.  
https://developers.openai.com/docs/build-skills  
https://developers.openai.com/docs/build-plugins

Design principles used here:

- portable `SKILL.md` packages;
- root `plugin.json` for distributable Agent Plugins;
- representative trigger and edge-case evaluations;
- clear skill descriptions for reliable routing.

## Public implementation inspirations

The following open repositories influenced the architectural comparison that led to this synthesis. Research Writer uses original wording and workflow design rather than copying their text.

### WenyuChiou/academic-writing-skills
https://github.com/WenyuChiou/academic-writing-skills

Notable ideas considered: manuscript-as-evidence-system, extended outlines, explicit nonclaims, top-down/bottom-up integrity, cross-artifact synchronization, and separate review mode.

### keithhegit/sci-using-kit
https://github.com/keithhegit/sci-using-kit

Notable ideas considered: evidence-bounded revision, literature vetting, comparative legitimacy, figure-as-claim discipline, and reviewer preflight.

### YuanZHAO321/Academic-Writing
https://github.com/YuanZHAO321/Academic-Writing

Notable ideas considered: progressive reference modules spanning paper structure, paragraph/sentence craft, figures/tables, review, and submission.


### ericmjl/skills — coherent-writing
https://github.com/ericmjl/skills/tree/main/skills/coherent-writing

License: MIT.

Notable ideas considered: diagnose-first coherence editing; separate checks for whole-draft conflicts, within-paragraph logic, section boundaries, paragraph boundaries, and a final full-draft audit; preserve voice, facts, claims, and length while forbidding new arguments/evidence during coherence repair.

### sdi2200262/elements-of-style-for-agents
https://github.com/sdi2200262/elements-of-style-for-agents

Notable ideas considered: a compact plain-English default layer and fuller guidance loaded only for substantial prose.

## Licensing note

The instructions and code in this repository are original and distributed under the MIT License. Referenced books, articles, documentation, and third-party repositories retain their own copyrights and licenses.
