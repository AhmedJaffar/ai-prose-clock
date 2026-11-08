---
title: "When Does the Clock Tick? A falsification-first audit of excess-vocabulary estimates of LLM-assisted writing"
author: "Ahmed Jaffar"
date: "2026-11-07"
keywords:
  - LLM-assisted writing
  - excess vocabulary
  - stylometry
  - replication
  - negative controls
  - computational social science
---

# Abstract

**Background.** Excess-vocabulary estimators infer the prevalence of LLM-assisted
writing from the post-2022 rise of words that large language models over-use. They
have become a standard tool for estimating how much of the scientific literature is
LLM-influenced, yet published prevalence estimates span an order of magnitude.

**Objective.** Rather than propose another prevalence figure, we audit the estimator
itself: what does it measure, when does it yield a dated diffusion curve, and when
does it fail?

**Data and method.** We apply one fixed pipeline to three registers, 2019-01 to
2026-10: 93,801 PubMed abstracts, 93,833 arXiv abstracts, and 75,247 NVD CVE
descriptions. The pipeline fits a pre-ChatGPT log-rate trend with seasonality per
word, extrapolates a counterfactual, and forms an index from a **pre-registered**
marker list — never from words chosen for having risen. We fit a logistic diffusion
curve and subject it to four falsification tests: recovery on synthetic corpora with
a known diffusion date, a within-corpus specificity permutation test, a placebo
break date, and a templated negative-control corpus.

**Results.** In PubMed the index rises after November 2022 and is well described by a
diffusion curve: half-adoption **2023-09** (95% CI 2023-05 to 2024-06), R² = 0.78,
with observed marker excess (+0.38) far above the permutation null (+0.01,
p = 0.005). The same estimator is **not identified in arXiv abstracts**: the index
rises in 2023–24 then falls sharply in 2026, R² ≈ 0, specificity p = 0.49. The
templated NVD corpus is **uninformative**: only 1 of 45 pre-registered markers is
estimable, so no index can be built.

**Two failure modes.** (i) Allowing data-driven marker fallback when too few
pre-registered markers survive produces a large, statistically tidy, entirely
spurious diffusion in the control corpus (+1.80 log units, R² = 0.91) — selection on
the outcome. (ii) Templated corpora often contain too little of the marker
vocabulary to serve as controls, so a non-result there is not evidence of method
validity.

**Conclusion.** Excess-vocabulary estimates are register- and design-sensitive. A
prevalence number is only interpretable alongside its marker source, specificity
test, and control diagnostics. We release the pipeline, the diagnostics, and every
number in this paper.

# 1. Introduction

Public estimates of how much text is now written with large language models disagree
by an order of magnitude, from under 10% to over 80%, depending on corpus and
estimator [@lee2026korean; @liang2025widespread; @siler2026diffusion]. The disagreement
is not merely sampling noise: different studies measure different registers with
different instruments.

The most widely used family of instruments is **excess vocabulary**
[@kobak2025delving; @kobak2024delving]. For each word, one fits a counterfactual from
the pre-ChatGPT period and measures how far the observed post-2022 frequency exceeds
it. Words that rise without an innocent explanation are taken as signatures of
LLM-influenced prose, and their excess is converted into a prevalence estimate.

This paper does not introduce a new estimator. It asks a prior question that the
literature has not systematically answered: **under what conditions does this
estimator produce a trustworthy dated result?** We treat the estimator as an
instrument to be calibrated, and we report where it fails as prominently as where it
succeeds.

Our contributions are negative and methodological:

1. A **pre-registered-marker protocol** with an explicit prohibition on data-driven
   fallback, and a demonstration that the fallback manufactures results.
2. A **within-corpus specificity test** (permutation over frequency-eligible
   non-marker words) that does not depend on an external control corpus.
3. A **synthetic recovery test** with a known diffusion date, which the pipeline
   passes in all seeds.
4. Evidence that the **same pipeline gives a clean dated curve in biomedicine and no
   identifiable curve in arXiv abstracts** over the same window — heterogeneity that
   should temper any single prevalence number.

# 2. Related work

**Excess vocabulary.** Kobak et al. introduced the method on more than 15 million
PubMed abstracts and estimated that at least 13.5% of 2024 abstracts had been
LLM-processed, with substantially higher rates in some subcorpora
[@kobak2024delving; @kobak2025delving]. Their 2026 follow-up argues that no existing
method yields reliable per-document estimates and reports much higher corpus shares
[@holzwarth2026most]. We adopt the estimator but not its per-document claims.

**Diffusion curves.** Siler fits adoption curves to 7.3 million full-text articles
and reports prevalence rising from roughly 12% (2023) to 57% (2025)
[@siler2026diffusion]. Liang et al. report monthly adoption across several
non-academic registers [@liang2025widespread; @liang2024monitoring]. Visokay et al.
estimate web-scale prevalence with detector error modelling [@visokay2026uneven], and
La Cava et al. study Reddit communities [@lacava2026machines]. Interrupted
time-series designs at the November 2022 breakpoint have also been published
[@hubarava2026accelerated].

**Discontinuity is contested.** Czuma finds no sharp discontinuity at the ChatGPT
release in preregistered congressional press releases, only post-period acceleration
[@czuma2026congress]. Kosch et al. find word-level shifts that predate LLM use
[@kosch2026chi]. A single-onset logistic curve is therefore a simplification, which we
report rather than hide.

**Detection.** Per-document detectors are unreliable and biased against non-native
writers [@sadasivan2023reliable; @liang2023detectors; @weberwulff2023detectors], which
motivates corpus-level estimation.

# 3. Data

Study window 2019-01 to 2026-10. Up to 1,000 documents per corpus per month.

| Corpus | Source | Documents | Tokens | Distinct words |
|---|---|---:|---:|---:|
| PubMed | Europe PMC (MED, abstract required) | 93,801 | 21,103,921 | 17,282 |
| arXiv | arXiv API, eight categories | 93,833 | 15,609,614 | 10,577 |
| NVD | NIST NVD API 2.0, English descriptions | 75,247 | 3,703,607 | 3,607 |

arXiv categories: cs.CL, cs.LG, cs.AI, stat.ML, math.NT, math.CO, hep-th,
cond-mat.stat-mech. The NVD corpus is a templated negative control: short,
formulaic security descriptions.

**Known data limitations.** NVD months 2024-07, 2025-03, 2026-09 and 2026-10 are
empty after repeated rate-limit failures. Every arXiv month contains ~1,000 documents
and the computer-science share is stable at roughly 70% across the window, so the sharp
index decline in late 2026 is **not** explained by document counts or gross category
composition. Its cause is unresolved. Candidate explanations include within-month API
ordering (each month is the most recent 1,000 matching submissions) and a genuine
vocabulary shift; we do not adjudicate between them and we do not use the late-2026
points to support any claim.

# 4. Method

## 4.1 Excess

For word *w* and month *m*, rate *r = count / tokens*. On the pre-period
(2019-01 … 2022-10) we fit

```
log r(w,m) = a_w + b_w t + c_w sin(2πm/12) + d_w cos(2πm/12) + e
```

and extrapolate. **Excess** is `log(observed) − log(predicted)`.

## 4.2 Index

The composite index is the **median** excess over the marker set, with a standard
error from the dispersion of the markers. Only **pre-registered** markers
(`src/wordlists.py`) that occur at least 3 times per month in the pre-period may enter
the index. If fewer than five qualify, the corpus is declared uninformative. Words
discovered from their own post-2022 rise are reported descriptively but **never** used
to build the index, because that is selection on the outcome.

## 4.3 Clock

`index(t) = K / (1 + exp(−g(t − t0)))`, fitted by bounded least squares. We report
onset (10%), half-adoption (50%), saturation (90%), and R², with parametric-bootstrap
intervals. A fit with R² < 0.40 or an implausible growth rate is reported as **not
identified** rather than extrapolated.

# 5. Falsification

**Synthetic recovery.** Corpora with 500 words and 20 injected markers following a
logistic lift (K = 0.5, g = 2.5, true inflection 2022-12) were passed through the full
pipeline. Across three seeds the top-ranked words were **100%** injected markers, the
recovered inflection was **2022-11** against a true 2022-12 (one month early), and the
placebo-word index was ≈ 0.000–0.005.

**Specificity permutation test.** For each corpus we draw 1,000 random sets of *n*
frequency-eligible non-marker words and compare their mean post-2022 excess with the
marker index.

**Placebo break.** Refit with the pre-period ending 2020-10 and evaluate 2021-01 to
2022-10. A sound estimator should show little excess under this fake break date.

**Negative control.** NVD descriptions should show no diffusion — *if* the marker
vocabulary is present at all.

# 6. Results

## 6.1 PubMed: a well-identified clock

The index rises after November 2022. Half-adoption is **2023-09** (95% CI 2023-05 to
2024-06); onset 2022-12; saturation 2024-05; R² = 0.78. Pre-period excess is 0.023
and post-period excess 0.455, a change of **+0.432**.

The specificity test is decisive: the marker index averages +0.38 against a
permutation null of +0.01 (SD 0.15) over 5,855 eligible words, **p = 0.005**. The
placebo break at 2020 produces a mean excess of −0.225, which we report as an
imperfect but clearly smaller disturbance than the real break.

The words driving the rise are exactly the expected LLM signature: *underscoring*
(2.48), *underscores* (2.04), *underscore* (2.02), *fostering* (1.90), *encompassing*
(1.77), alongside topic words (*chatgpt*, *prompting*) that we do not use as markers.

## 6.2 arXiv: not identified

The same estimator fails in arXiv abstracts. The index rises modestly in 2023 (+0.17)
and 2024 (+0.28) but falls sharply in 2026 (−0.70), leaving the logistic fit
unidentified (R² ≈ 0, implausible growth rate) and the specificity test null
(observed −0.04 vs null −0.05, **p = 0.49**). The top data-driven words are pure topic
drift (*llm*, *llms*, *llama*, *rag*, *vlms*, *lora*), not style.

We do not claim arXiv abstracts contain no LLM-assisted prose. We claim the instrument
cannot date it here, and we flag late-2026 sampling as a likely artefact.

## 6.3 The control corpus is uninformative, and the fallback is dangerous

Only **1 of 45** pre-registered markers (*leverage*) meets the pre-period frequency
threshold in NVD, so the control cannot be estimated. This is itself a finding: a
templated register may contain too little of the marker vocabulary to falsify
anything.

More importantly, our first implementation fell back to data-driven markers when fewer
than five pre-registered markers qualified. On NVD that produced a large, tidy,
entirely spurious diffusion: half-adoption 2023-06, R² = 0.91, post-pre excess
**+1.80** — larger than the real PubMed effect. The markers were *handles*, *inline*,
*mdm*, *chakra*, *sharepoint*: technology vocabulary that changed with the CVE
population, selected precisely because it rose. We removed the fallback. This is the
paper's central methodological warning.

# 7. Discussion

Three results matter.

First, the estimator **works where the marker vocabulary is dense and stable**: in
biomedical abstracts it recovers a clean, well-powered, specificity-confirmed
diffusion dated to late 2023, consistent with independent estimates
[@kobak2025delving; @siler2026diffusion].

Second, it **does not generalise automatically across registers**. The same pipeline,
same markers, same window yields no identified curve in arXiv abstracts. Prevalence
claims should therefore be register-specific, not "the web".

Third, **the most dangerous design choice is invisible in the output**. Data-driven
marker fallback produced a stronger, better-fitting, more statistically impressive
result in the control corpus than the real effect in the treatment corpus. Any
excess-vocabulary study that selects markers after observing their rise, without a
preregistered list and a specificity test, can generate a publishable-looking finding
from noise.

Relative to Siler [@siler2026diffusion] and Liang et al. [@liang2025widespread], we do
not add a prevalence estimate. We add the diagnostics that determine whether such an
estimate means anything.

# 8. Limitations

- Corpus-level inference only; no document-level authorship claims.
- The marker list is a moving target as models change; we report sensitivity by
  withholding the fallback and by reporting marker counts.
- The index is median-standardised, so K is not in physical units and "onset = 10% of
  K" is partly a normalisation artefact. We therefore emphasise half-adoption and the
  specificity test over K.
- A single logistic curve cannot represent a slope change on pre-existing drift
  [@czuma2026congress; @kosch2026chi]; model comparison against trend-break
  alternatives is the natural next step.
- arXiv's late-2026 sampling is asymmetric, and NVD has missing months.
- Our literature search could not use Semantic Scholar (persistent HTTP 429), so
  citation-graph expansion was unavailable.

# 9. Conclusion

Excess-vocabulary estimation is a real instrument with real failure modes. In
biomedical abstracts it dates the diffusion of LLM-style writing to late 2023 with a
specificity p-value of 0.005. In arXiv abstracts it produces no identifiable curve,
and in a templated control corpus it produces nothing at all. The difference between a
credible prevalence estimate and a spurious one is not the sophistication of the model
but the pre-registration of the markers, the specificity test, and the honesty of the
control diagnostics. We release all three.

# Data and code availability

Code, pipeline, diagnostics and every number in this paper:
`https://github.com/AhmedJaffar/ai-prose-clock`. Raw third-party text is not
redistributed; aggregate word counts and all derived statistics are generated by the
pipeline from public APIs.

# References

Generated into `paper/bibliography.bib` from live Crossref and arXiv metadata; every
DOI and arXiv identifier was resolved and title-matched. See `paper/prior_art.md` for
the full search log and `paper/novelty.md` for the honest novelty assessment.
