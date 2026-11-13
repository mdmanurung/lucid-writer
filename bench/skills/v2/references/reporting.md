# Reporting completeness

Use for full manuscripts/protocols with a recognizable study design.

## Rule

Identify the study design, retrieve the **current authoritative reporting guideline and relevant extensions** when tools permit, and use it as a completeness checklist.

Do not:

- use an outdated checklist when a newer authoritative version exists;
- treat a reporting checklist as a study-quality/risk-of-bias instrument unless designed for that purpose;
- invent methods or procedures to make the checklist complete;
- mechanically reorder the manuscript into checklist order.

## Common health-research routes

| Study type | Reporting family |
|---|---|
| Randomized trial | CONSORT |
| Observational study | STROBE |
| Systematic review/meta-analysis | PRISMA |
| Trial protocol | SPIRIT |
| Review protocol | PRISMA-P |
| Diagnostic accuracy | STARD |
| Prediction model | TRIPOD / TRIPOD+AI where applicable |
| Case report | CARE |
| Qualitative research | SRQR / COREQ |
| Animal preclinical study | ARRIVE |
| Quality improvement | SQUIRE |
| Economic evaluation | CHEERS |

Use relevant extensions when the intervention, outcome, technology, or design requires them.

At release, classify each applicable item:

- reported;
- partial;
- not reported;
- not applicable;
- cannot verify.

Distinguish **not reported** from **not done**.

## Preflight table

For a release preflight, return one row per applicable guideline item, using `assets/reporting-preflight.csv`:

`guideline | version | item_id | item | manuscript_location | status`

`status` is one of the five classes above (`reported`, `partial`, `not reported`, `not applicable`, `cannot verify`). Copy `item_id` and `item` from the retrieved guideline; never write an item from memory. Give `manuscript_location` as a section and paragraph, table or figure. Leave it empty for `not reported` and `not applicable`.

Report study validity separately. A completed table shows what the manuscript reports, not whether the study is sound, and a checklist is not a risk-of-bias instrument.

## Assay-level standards

Use alongside the design guideline when the study's data come from the assay. Citations were checked in PubMed and Europe PMC on 2026-11-13.

| Assay | Standard | Citation | Status |
|---|---|---|---|
| Flow cytometry | MIFlowCyt, the Minimum Information about a Flow Cytometry Experiment, version 1.0 | Lee JA, Spidlen J, Boyce K, et al. Cytometry A 2008;73(10):926-930. [doi:10.1002/cyto.a.20623](https://doi.org/10.1002/cyto.a.20623). PMID 18752282. | An ISAC recommendation. The ISAC page links the 1.0 specification as the latest, and a 2010 checklist note is numbered to "MIFlowCyt 1.0" (PMID 20737419). I found no newer version, but that search was not exhaustive. For extracellular vesicles, MIFlowCyt-EV extends it: Welsh JA, et al. J Extracell Vesicles 2020;9(1):1713526, [doi:10.1080/20013078.2020.1713526](https://doi.org/10.1080/20013078.2020.1713526), PMID 32128070. |
| Single-cell RNA sequencing | minSCe, the Minimum Information about a Single-Cell Experiment ("Guidelines for reporting single-cell RNA-seq experiments") | Füllgrabe A, George N, Green M, et al. Nat Biotechnol 2020;38(12):1384-1386. [doi:10.1038/s41587-020-00744-z](https://doi.org/10.1038/s41587-020-00744-z). PMID 33188371. Items: its Supplementary Note (a 27-page PDF, "in the format provided by the authors and unedited"). | Covers scRNA-seq only; the article says single-cell ATAC-seq and other assays are not covered. Built on MIAME and MINSEQE with additions. The note lists eight components (biosource; single cell isolation; library construction; sequencing assay; raw data; processed data and post-analysis information; protocols; study and publication) and rates each attribute 1 mandatory, 2 essential or 3 additional. It does not use the words "required" or "recommended". Mandatory (1) attributes: organism; library construction method; end bias; library strand; technical replicate group or library reference; the UMI, cell-barcode and cDNA read, offset and size; and the read and index files. Use the note, not this summary, as the checklist. TODO(maintainer): spot-check the significance numbers against the PDF pages; I read them from text extracted in layout mode. |

Do not add an assay standard that has not been verified against a primary source.

Authoritative library: EQUATOR Network  
https://www.equator-network.org/reporting-guidelines/
