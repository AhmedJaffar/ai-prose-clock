# Prior art review — *The AI Prose Clock*

**Scope.** Detection-free measurement of LLM-style writing diffusion across corpora, 2019–2026.
**Search performed:** 2026-11-07 / 2026-11-08.
**Channels:** arXiv API (20 phrase queries + 34 ID lookups), Crossref (20 bibliographic queries + ~35 title lookups + DOI resolution), web search (~22 queries), plus targeted full-text fetch of arXiv abstracts and one NBER working-paper page.
**Channels that failed:** Semantic Scholar's unauthenticated `/graph/v1/paper/search` endpoint returned HTTP 429 on every attempt (~15 tries across three sessions, exponential backoff to 120 s). I could not use it for discovery or citation-graph expansion; Crossref and arXiv carried discovery. OpenAlex was skipped as instructed (rate-limited on this IP).

**Headline.** The method is not new, the finding is not new, and the *shape* of the finding has already been published several times — including once in PNAS under the word "diffusion". The specific combination the project proposes (harmonised detection-free excess-vocabulary index → fitted logistic clock with dated onset/half-adoption/saturation → cross-register replication → templated negative control) does not appear to exist. But every individual component does, and two of them were published within the last twelve months.

---

## 1. Kobak et al. — the closest prior art, and its descendants

### 1.1 The original

**Kobak, González-Márquez, Horvát & Lause**, "Delving into LLM-assisted writing in biomedical publications through excess vocabulary".
arXiv:2406.07016 (v1 June 2024; earlier versions through v4 circulated as *"Delving into ChatGPT usage in academic writing through excess vocabulary"*).
Published as **Science Advances 11(27): eadt3813, 2 July 2025**, DOI [10.1126/sciadv.adt3813](https://doi.org/10.1126/sciadv.adt3813).

*What it did.* More than **15 million PubMed abstracts, 2010–2024**. For each word, it compared observed frequency in the post-ChatGPT window against a counterfactual extrapolated from the pre-period, and defined "excess" words as those whose frequency rose far above trend. It then inverted the excess into a **lower bound on the share of abstracts that had been LLM-processed**: **at least 13.5% of 2024 abstracts**, reaching **~40% in some subcorpora** (by discipline, country, journal). It argued the effect exceeded that of COVID on biomedical vocabulary.

*What it did not do — this matters for the novelty claim.*

| Design element of the AI Prose Clock | Present in Kobak et al.? |
|---|---|
| Per-word log-rate pre-trend, extrapolated counterfactual | **Yes** — this is their method |
| Explicit month-of-year seasonality in the counterfactual | **No** (annual/period aggregation; no seasonal term) |
| More than one corpus *family* (non-biomedical) | **No** |
| Markers discovered in one register, evaluated out-of-sample in another | **No** — everything is within PubMed |
| Logistic diffusion curve fitted to a composite index | **No** |
| Dated onset / half-adoption / saturation with CIs | **No** — reports period-level prevalence bounds |
| A templated / low-adoption **negative-control corpus** | **No** |
| Typographic second channel (em dash, etc.) | **No** |
| Placebo launch dates | **No** (they do robustness on word sets, not on fake break dates) |

So: the *estimator* is Kobak's. The contribution cannot be "we invented excess vocabulary for LLM detection".

### 1.2 The same lab has already superseded it

**Holzwarth, González-Márquez & Kobak (2026)**, "Most biomedical publications show signs of LLM-assisted writing", arXiv:2608.10715, 11 Aug 2026.

This is the single most important paper in this review after Siler (below), because it is the **direct successor by the same authors** and it explicitly repudiates the reliability of prior prevalence estimates:

> "Despite some recent progress in this direction, **no existing method can produce reliable estimates.** Here we suggest and validate a new unbiased approach to estimate LLM usage in a corpus of texts based on changing word frequencies."

It applies the new estimator to **PubMed Central full texts** and reports that by end-2025 **89% of papers show excess of LLM-associated vocabulary**, with **68%** of Discussion paragraphs vs **32%** of Methods paragraphs affected (i.e. >50% even in Methods).

Consequences for this project, stated bluntly:
1. The 13.5% lower bound is dead as a headline number; 89% is the current estimate for biomedical full text.
2. If the AI Prose Clock uses the Kobak-2024 estimator unmodified, a reviewer will point at Holzwarth 2026 and ask why the project is using the version its own authors have replaced.
3. The paper must engage with Holzwarth's claim that frequency-based estimators were previously *biased*, and say which estimator it is using and why.

### 1.3 Replications, extensions, and critiques (ordered by relevance)

- **Siler (2026)**, "The diffusion of large language models in published academic articles", *PNAS* **123**(22), DOI [10.1073/pnas.2605754123](https://doi.org/10.1073/pnas.2605754123), 29 May 2026. See §5 — this is the most threatening single paper.
- **Lee (2026)**, "An LLM-Associated Register Shift in Korean Journal Abstracts: A Morphology-Aware Excess-Vocabulary Study, 2018–2026", arXiv:2609.07447. 398,296 KCI abstracts + 47,165 Vietnamese abstracts. Adds a serious falsification apparatus that the AI Prose Clock should note it does **not** own: **placebo floors** (0.1–2.2 points for the single-word statistic, ≤2.9 for a re-selected split-half set statistic), **split-half set bounds**, and subject-matter and translation-route controls. Reports: nothing in 2023, **onset late 2024**, rise through 2025, flattening mid-2026. Conditional lower bounds 3.5% / 10.5% / 16.1% for 2024–26; split-half bounds 7.8% / 20.6% / 33.0%. Also reports that under Holzwarth et al.'s estimator the same data give 41.9% and 72.1% — i.e. the estimator choice moves the answer by a factor of ~2–4. This is a direct empirical demonstration that the AI Prose Clock's headline number is estimator-dependent, and it is the best available evidence for how much.
- **Alani & Jansen (2026)**, "Are Scientists Starting to Sound like ChatGPT? **Stylistic Diffusion** in Biomedical Abstracts in the LLM Era", *Machine Learning and Knowledge Extraction* **8**(8):223, DOI [10.3390/make8080223](https://doi.org/10.3390/make8080223). The word "diffusion" applied to stylistic change in abstracts — same conceptual frame as the AI Prose Clock.
- **Thelwall & Kousha (2026)**, "Have LLM-associated terms increased in article full texts in all fields?", arXiv:2604.07565.
- **Sanger & Maurer (2026)**, "Have Large Language Models Enhanced the Way Civil & Environmental Engineers Write?", arXiv:2602.03864 — a discipline-specific replication.
- **Matsui (2025)**, "Delving Into PubMed Records: How AI-Influenced Vocabulary has Transformed Medical Writing since ChatGPT", *Perspectives on Medical Education* **14**(1):882–890, DOI [10.5334/pme.1929](https://doi.org/10.5334/pme.1929).
- **Lin, Zhao, Tian & Li (2025)**, "Large language models reshape the language of science", arXiv:2504.12317.
- **Paklina, Parshakov & Rapoport (2026)**, "LLM-assisted writing and citation advantage", *Scientometrics* **131**(10):7611–7636, DOI [10.1007/s11192-026-05805-9](https://doi.org/10.1007/s11192-026-05805-9) — links the excess measure to an outcome (citations).
- **Wolfrath et al. (2026)**, "Rising Prevalence of Detected AI-Generated Text in Medical Literature: Longitudinal Analysis in Open Access Articles", arXiv:2603.19316 — longitudinal, but **detector-based**, so it belongs to the tradition the project argues against; still a direct competitor for the "longitudinal prevalence in medicine" slot.
- **Gray (2024)**, "ChatGPT 'contamination': estimating the prevalence of LLMs in the scholarly literature", arXiv:2403.16887.
- **Geng & Trotta (2024)**, "Is ChatGPT Transforming Academics' Writing Style?", arXiv:2404.08627.
- **Juzek & Ward (2024)**, "Why Does ChatGPT 'Delve' So Much? Exploring the Sources of Lexical Overrepresentation in Large Language Models", arXiv:2412.11385 (COLING 2025) — the mechanistic account of *why* the marker vocabulary exists (pretraining-corpus overrepresentation, RLHF register). Essential citation for the "markers are real, not artefacts" premise.
- **Nakajima & Mizuno (2026)**, "Large Language Model Turnover Undermines Screening for Artificial Intelligence-Assisted Scientific Writing", arXiv:2610.11599 — the marker-decay problem, i.e. the project's own stated limitation (§9 of DESIGN.md) already has a dedicated paper.
- **Grey-literature replication wave (Zenodo, 2026).** At least two further single-register excess-vocabulary studies with explicit placebo machinery: *"A register shift consistent with generative-AI writing in Japan's domestic society journals: **placebo tests for seven excess-vocabulary instruments** on 88,036 abstracts"* (Zenodo 22043702) and *"Beyond Mere Words: Tracing Large-Language-Model Style in Korean Academic Writing through Excess Vocabulary"* (Zenodo 22103158). I did not read these in full (Zenodo records, code-and-results deposits); I record them because their existence indicates the method is now a widely-replicated template, and that "placebo tests" are no longer a differentiating move.

**Net assessment of the Kobak line.** Excess vocabulary is a mature, contested, rapidly-replicating measurement tradition with a 2025 Science Advances paper, a 2026 PNAS paper, and a 2026 methodological revision by the original authors. A new paper in this space is entering a crowded field, not opening one.

---

## 2. Other excess-vocabulary / word-frequency / stylometric studies

- **Juzek, Ming & Hernandez (2026)**, "Fully Automated Identification of Lexical Alignment and Preference-Stage Shifts in Large Language Models", LREC 2026, pp. 6116–6131 — separates *pretraining* lexical bias from *preference-tuning* register, which is the mechanism behind marker drift.
- **Czuma (2026a)**, "The em-dash em-beds in Congress: A population-level rise in em-dash frequency in U.S. congressional press releases at the dawn of the large-language-model era, 2021–2025", arXiv:2608.05889. **This is the most methodologically sophisticated paper in the typographic-marker space and it largely pre-empts the project's "second channel".** Preregistered (OSF DOI 10.17605/OSF.IO/U5NEY); 146,239 releases from 480 House and Senate offices; Poisson/negative-binomial with length offset and office clustering; **three placebo cut-offs, all null**; within-author panel (75.6% of 262 continuous offices increased); segmented regression. Findings: density flat at 0.10–0.12 per 1,000 chars 2021–2024, then **0.217 in 2025**; share of releases with an unspaced em dash **13% → 24.8%**; primary ratio 1.55 (95% CI 1.28–1.93). Critically: **"A segmented regression finds no step at the ChatGPT cut-off but a clear post-period acceleration."** The author explicitly frames the em dash as "a population-level marker, not a per-release authorship detector" — i.e. the exact epistemic stance the AI Prose Clock adopts, published first.
- **Czuma (2026b)**, "Em-ergence of the em-dash: a population-level rise in em-dash frequency in medRxiv preprints…", arXiv:2606.29540 — the same design in a second corpus. So even "the typographic channel replicates across two corpora" is taken.
- **Kosch, Welsch, Hedderich & Katins (2026)**, "How Did Writing Change at CHI? Analyzing 44 Years of CHI Writing Before and After the Introduction of Large Language Models", arXiv:2609.23090. 14,262 papers, all 44 CHI proceedings (1982–2026); readability, register, lexical diversity, LLM marker words. Two findings that directly threaten the project's premise: prose **did not homogenise**, and **"the word-level shift began before any author used LLMs, so LLMs did not start the change but accelerated it."** That is a pre-trend problem for any design that dates an onset at 2022-11.
- **Guo et al. (2025)**, "Measuring Human Involvement in AI-Generated Text: A Case Study on Academic Writing", arXiv:2506.03501 — graded rather than binary involvement; relevant to the project's "stylistic drift is consistent with, not proof of, LLM assistance" caveat.
- **Fraser, Dawkins & Kiritchenko (2025)**, "Detecting AI-Generated Text: Factors Influencing Detectability with Current Methods", *JAIR* **82**:2233–2278, DOI [10.1613/jair.1.16665](https://doi.org/10.1613/jair.1.16665) — the best current review of *which* stylistic features are and are not diagnostic; should be cited for the marker-feature choice.

---

## 3. Prevalence / adoption estimates in specific corpora

This is the most crowded area of all. Table of published prevalence estimates, with corpus and method:

| Work | Corpus | Window | Estimate | Method |
|---|---|---|---|---|
| Kobak et al. 2025 (Sci Adv) | 15M PubMed abstracts | 2010–2024 | ≥13.5% of 2024 abstracts; ~40% some subcorpora | excess vocabulary, lower bound |
| Holzwarth et al. 2026 | PMC full texts | –2025 | **89%** of papers by end-2025; 68% Discussion / 32% Methods paragraphs | revised frequency estimator |
| Siler 2026 (PNAS) | 7.3M articles, Elsevier/Frontiers/MDPI/PLoS | 2020–2025 | **57%** in 2025, **12%** in 2023 | 228 focal words, article scoring, DiD |
| Lee 2026 | 398k KCI abstracts | 2018–2026 | 3.5–33% conditional bounds; 42–72% under Holzwarth estimator | excess vocabulary + placebos |
| Liang et al. 2025 (Patterns) | 687k consumer complaints; 537k corporate press releases; 304.3M job postings; 15,919 UN releases | Jan 2022–Sep 2024 | **18%** complaints, **24%** press releases, **<10%** small-firm job postings, **~14%** UN | population-level word-frequency framework |
| Visokay et al. 2026 | >5M crawlable webpages | –2026 | rising, uneven by TLD/language/web-centrality | multi-detector + Bayesian hierarchical correction |
| La Cava, Aiello & Tagarelli 2026 | 51 subreddits | 2022–2024 | "marginally present", peaks **9%** | statistical MGT detection |
| Bloom et al. 2026 (NBER w35546) | LinkedIn profile revisions, 2020–2026 | 2020–2026 | 19.7% retroactively edit past roles; LLM markers surge post-ChatGPT | marker counts in edited text |
| Russo et al. 2025 (PACM HCI) | ICLR/NeurIPS/ICML peer reviews | –2024 | widespread AI-assisted reviewing, raises scores | LLM-modified-text fraction |
| Liang et al. 2024a | AI conference peer reviews | –2024 | measurable post-ChatGPT increase | modified-text fraction |
| Liang et al. 2024b | arXiv/PMC scientific papers | –2024 | increasing LLM-modified fraction | modified-text fraction |
| Wolfrath et al. 2026 | Open-access medical literature | longitudinal | rising detected share | detectors |

**Reading of the table.** Prevalence estimation is saturated. The numbers range from 9% (Reddit) to 89% (PMC full text) and the *between-study variance is driven mostly by method and corpus definition, not by the underlying phenomenon*. Any new prevalence number has to justify itself against this spread. The most useful thing a new paper can do here is not produce another point estimate but explain the spread — which the AI Prose Clock is accidentally well positioned to do, and does not currently claim.

**Signals about the project's chosen corpora.**
- **Hacker News** has no peer-reviewed academic measurement that I could find, but has commercial/grey measurement: *Dead Internet Monitor* reports 12.5% of HN as AI-generated (<https://deadinternetmonitor.com/source/hackernews>). So HN is a live target but not an academically occupied one — a genuine gap, though a thin one, and the grey estimate is a number reviewers may know.
- **NVD CVE descriptions** are *not* a safe negative control. There is public evidence that CVE descriptions are themselves being LLM-generated and that this degrades data quality (e.g. "LLM Generated CVE Descriptions Undermine Security Data Quality and Trust", VulDB, 2026), and NVD has had well-publicised enrichment backlogs. A "negative control" that is plausibly positive is a liability, not an asset. See novelty.md §(d).

---

## 4. Detection literature and its critiques

The project's "detection-free" positioning is well-supported by this literature, but it is also *well-trodden* — the argument that per-document detection is unreliable is now the consensus position, not a novel stance.

**Bias and unreliability.**
- **Liang, Yuksekgonul, Mao, Wu & Zou (2023)**, "GPT detectors are biased against non-native English writers", *Patterns* **4**(7):100779, DOI [10.1016/j.patter.2023.100779](https://doi.org/10.1016/j.patter.2023.100779) — the canonical citation; detector false-positive rates on non-native-written TOEFL essays are very high, and the paper's headline finding is that detectors penalise exactly the writers detection-free measurement is meant to protect.
- **Sadasivan, Kumar, Balasubramanian, Wang & Feizi (2023)**, "Can AI-Generated Text be Reliably Detected?", arXiv:2303.11156 — the impossibility/paraphrase argument. I could not verify a peer-reviewed venue in Crossref; cite the arXiv version.
- **Krishna, Song, Karpinska, Wieting & Iyyer (2023)**, "Paraphrasing evades detectors of AI-generated text, but retrieval is an effective defense", *NeurIPS 36*:27469–27500, DOI [10.52202/075280-1195](https://doi.org/10.52202/075280-1195).
- **Kirchenbauer et al. (2023)**, "A Watermark for Large Language Models", arXiv:2301.10226 — watermarking works only with generator cooperation, which is the structural reason detection-free measurement is attractive.
- **Mitchell, Lee, Khazatsky, Manning & Finn (2023)**, "DetectGPT", arXiv:2301.11305.
- **Ghosal et al. (2023)**, "Towards Possibilities & Impossibilities of AI-Generated Text Detection: A Survey", arXiv:2310.15264.
- **Wu et al. (2025)**, "A Survey on LLM-Generated Text Detection: Necessity, Methods, and Future Directions", *Computational Linguistics* **51**(1):275–338, DOI [10.1162/coli_a_00549](https://doi.org/10.1162/coli_a_00549) — the standard current survey.
- **Fraser et al. (2025)**, JAIR (above).

**The important complication for this project.** The strongest recent web-scale prevalence paper, **Visokay et al. (2026)**, does *not* abandon detection — it uses multiple detectors and corrects for their error rates in a Bayesian hierarchical model, propagating detector uncertainty into prevalence. That is a serious alternative to detection-free measurement, and it answers the objection "your index has no known sensitivity/specificity". A reviewer who knows this paper will ask why an excess-vocabulary index is preferable to a detector ensemble with explicit error modelling. The honest answer is: because detectors' error rates are themselves corpus-dependent and unvalidated out of distribution — which Liang 2023 and Sadasivan 2023 establish — but the project must make that argument explicitly, not assume it.

---

## 5. Time course, diffusion curves, structural breaks — the decisive question

### 5.1 The direct answer

**Yes. Cross-corpus temporal adoption curves of LLM-style writing already exist, in at least four independent published forms.**

1. **Siler (2026), PNAS** — "**The diffusion of** large language models in published academic articles". 7.3M full-text articles, four publishers, 2020–2025, a 228-word focal lexicon derived from sharp post-2022 frequency increases, per-article scoring, a year-by-year prevalence trajectory (12% → 57%), and difference-in-differences across region, institutional rank, publisher, discipline and journal tier. *This is, functionally, the paper the AI Prose Clock proposes to write, for the academic register, at 100× the corpus scale, in a top-5 venue, under the same word.*
2. **Liang, Zhang, Codreanu, Wang, Cao & Zou (2025)**, "The widespread adoption of large language model-assisted writing across society", *Patterns* **6**(12):101366, DOI [10.1016/j.patter.2025.101366](https://doi.org/10.1016/j.patter.2025.101366) (arXiv:2502.09747). **Four independent registers** — consumer complaints, corporate press releases, job postings, UN press releases — Jan 2022 to Sep 2024, monthly adoption series, per-domain prevalence (18%, 24%, <10%, ~14%), and an explicit saturation claim ("growth appears to have stabilized by 2024, reflecting either saturation in LLM adoption or increasing subtlety of more advanced models"). This is *cross-corpus temporal adoption curves of LLM-assisted writing*, which is the project's core sentence.
3. **Visokay et al. (2026)**, "The uneven rise of AI-generated web content", arXiv:2610.36631. >5M webpages, share containing AI-generated text rising over time, stratified by language, TLD and position in the web graph, detector-error-corrected. A temporal diffusion curve on the open web.
4. **La Cava, Aiello & Tagarelli (2026)**, *Online Social Networks and Media* **55**:100355 — monthly MGT prevalence across 51 subreddits, 2022–2024.

Plus, in the "structural break" idiom specifically: **Hubarava & Ineichen (2026)**, "Accelerated Drift of Scientific Prose in the LLM Era: Evidence from an **Interrupted Time-Series Analysis**", EMNLP 2026, pp. 50910–50931, DOI [10.18653/2026.emnlp-main.2237](https://doi.org/10.18653/2026.emnlp-main.2237). This compares pre- and post-2022 trajectories across vocabulary, punctuation, readability and syntax in arXiv (cs.AI, stat, q-bio) and medRxiv abstracts, using interrupted time-series regression with November 2022 as the breakpoint. That is the project's identification strategy, across the project's primary corpora, already published at a top NLP venue — and it reaches a *more nuanced* conclusion: different feature families behave differently ("some lexical markers accelerate persistently, while others rise and then recede").

### 5.2 What I could *not* find

After 20 arXiv phrase queries, 20 Crossref bibliographic queries, ~35 title verifications and ~22 web searches, I found **no** paper that:

- fits a **logistic (or Bass) diffusion curve** to an LLM-style index and reports **onset, half-adoption date, saturation level and growth rate with confidence intervals** as the headline estimand;
- uses a **templated / provably-low-adoption corpus as a negative control** for an excess-vocabulary estimator (Czuma 2026a uses placebo *cut-offs*, not a placebo *corpus*; Lee 2026 uses split-half and subject-matter controls);
- discovers markers in one register and evaluates them **out-of-sample, without refitting, in a different register** (Kobak, Holzwarth, Lee, Siler are all within-corpus; Liang 2025 applies one framework across domains but does not report cross-register marker replication as an identification test).

Searches that specifically targeted these and returned nothing: `"structural break" AND "text" AND "corpus"` (1 irrelevant hit), `"diffusion" AND "AI-generated text"` (5 hits, all image-diffusion models), `"adoption" AND "generative AI" AND "text" AND "corpora"` (0 hits), `Bass model logistic fit AI writing adoption S-curve` (no relevant academic hit), plus web searches for a fitted logistic/Bass curve and for a "negative control corpus" in this literature.

**Caveat on coverage.** With Semantic Scholar unavailable I could not do backward/forward citation expansion from Kobak 2024. That is the one channel most likely to have missed a paper — specifically, a 2026 paper citing Kobak that does the clock. The claim above should be read as "not found under a fairly thorough but citation-graph-blind search", not "does not exist".

### 5.3 The uncomfortable finding inside the time-course literature

Two papers independently undercut the clean-onset premise the logistic model encodes:

- **Czuma (2026a)**: segmented regression on congressional press releases finds **no discontinuity at the ChatGPT cut-off, only a post-period acceleration**.
- **Kosch et al. (2026)**: in 44 years of CHI, "the word-level shift **began before any author used LLMs**".

A logistic with a single onset parameter `m0` will fit these data by placing `m0` somewhere in 2023–2024, but the underlying process looks more like a **change in slope on top of a pre-existing drift** than a diffusion-from-zero. The project's own modelling choice (`K / (1 + exp(-g(m - m0)))`) implicitly asserts the former. This is the substantive scientific risk, distinct from the novelty risk.

---

## 6. Summary table — novelty-relevant claims vs. the literature

| Project claim | Closest prior work | Status |
|---|---|---|
| "Excess vocabulary measures LLM influence" | Kobak 2024/2025 | **Taken** |
| "Estimator improved / made unbiased" | Holzwarth 2026 | **Taken, by the original authors** |
| "Cross-domain adoption curves" | Liang et al. 2025 (4 registers) | **Taken** |
| "Diffusion of LLM writing, measured, 2020–2025" | Siler 2026 (PNAS) | **Taken, in the title** |
| "Stylistic diffusion in abstracts" | Alani & Jansen 2026 | **Taken** |
| "Structural break / interrupted time series at 2022-11" | Hubarava & Ineichen 2026 | **Taken** |
| "Typographic second channel (em dash), population-level, not a detector" | Czuma 2026a/b | **Taken, preregistered, with placebos** |
| "Placebo launch dates / placebo vocabulary" | Czuma 2026a; Lee 2026 | **Largely taken** |
| "Web-scale temporal prevalence with uncertainty" | Visokay et al. 2026 | **Taken (detection-based)** |
| "Reddit / social-media register" | La Cava et al. 2026 | **Taken** |
| "Hacker News as a register" | none academic (grey: 12.5%) | **Open, thin** |
| "Fitted logistic clock: onset / half-adoption / saturation + CIs" | none found | **Open** |
| "Negative-control corpus as falsification" | none found | **Open — but empirically fragile (CVE)** |
| "Cross-register out-of-sample marker replication" | none found | **Open** |
| "Harmonised single estimator across a register gradient incl. a control" | none found | **Open** |

---

## 7. Search log (for reproducibility)

**arXiv queries** (phrase queries against `all:`): `"excess vocabulary"`, `"excess words"`, `"LLM-assisted writing"`, `"AI-assisted writing" AND prevalence`, `"ChatGPT" AND "abstracts" AND "prevalence"`, `"AI-generated text" AND "detection" AND "survey"`, `"stylometric" AND "ChatGPT"`, `"LLM-generated text" AND "detection"`, `"scientific writing" AND "large language models"`, `"peer review" AND "large language models" AND "prevalence"`, `"ChatGPT" AND "academic writing" AND "corpus"`, `"watermark" AND "language model"`, `"paraphrase" AND "detection" AND "evade"`, `"lexical" AND "large language models" AND "change"`, `"diffusion" AND "AI-generated text"`, `"adoption" AND "generative AI" AND "text" AND "corpora"`, `"Hacker News" AND "large language models"`, `"CVE" AND "large language models"`, `"structural break" AND "text" AND "corpus"`, `"AI-generated" AND "prevalence" AND "estimate"`. Note: `"excess vocabulary"` returns only **3** arXiv records in total — Kobak, Lee, and one unrelated 2021 paper. The phrase itself is a tight namespace.

**Crossref:** ~20 `query.bibliographic` searches on the topic families above, plus ~35 exact-title lookups for verification, plus DOI resolution for 10.1073/pnas.2605754123.

**Web:** ~22 queries across the five required areas, including checks for a fitted diffusion curve, a negative-control corpus, an "AI prose clock" prior use of the name (none found), and critiques of Kobak.

**Not searched:** Google Scholar (no API), OpenAlex (excluded), Semantic Scholar (blocked by 429). Citation-graph expansion was therefore not performed — the principal residual risk in this review.
