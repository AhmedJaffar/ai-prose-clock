# The AI Prose Clock

**Dating and measuring the diffusion of LLM-style writing across the open web, 2019–2026**

Design document v1 · 2026-11-07 · Lead

---

## 1. The question

Generative language models became publicly available in late 2022. Since then, an unknown
share of new public text has passed through them. We do not know how large that share is,
when it began to rise, or whether it has plateaued — because individual-document AI
detection is unreliable.

This project answers a question that can be answered without a detector:

> **How fast did the *distribution of prose* in public corpora shift toward the
> distribution produced by large language models — and when did that shift begin?**

We introduce a **corpus-internal, detection-free clock**: a procedure that estimates the
monthly prevalence of LLM-style prose in any text stream, with falsifiable placebos.

## 2. Why detection-free

Per-document AI detectors are (a) unreliable out of distribution, (b) biased against
non-native English writers, and (c) impossible to validate at web scale. They also answer a
question nobody can operationalise: "was *this specific document* written by a model?"

The population question — *what fraction of new text carries LLM stylistic signatures?* — is
estimable without classifying documents. If models systematically over-use a set of words and
typographic habits, then a rise in a corpus's use of those features is evidence of a rise in
LLM-influenced text, even if no single document can be labelled.

**What this measures:** stylistic drift *consistent with* LLM assistance.
**What this does not measure:** whether any document was authored by a model, or authorship
attribution. All claims are about corpus-level distributions.

## 3. Corpora

Monthly samples, 2019-01 → 2026-10 (93 months). Five registers chosen so that adoption should
differ sharply, giving internal replication and a negative control.

| Corpus | Register | Expected adoption | Role |
|---|---|---|---|
| arXiv abstracts (`cs.CL`, `cs.LG`, `physics`, `math`) | technical/scientific | high in CS | primary |
| Europe PMC / PubMed abstracts | biomedical | medium (Kobak et al. 2024) | replication |
| Hacker News comments | informal tech discourse | medium-high | primary |
| SEC EDGAR 10-K filings | formal corporate/legal | low-medium | secondary (phrase-level) |
| NVD CVE descriptions | formulaic security boilerplate | ~none | **negative control** |

The control corpus matters: if the clock ticks in CVE descriptions, the method is broken,
because those descriptions are templated and not plausibly LLM-written at scale.

## 4. Features

Computed per document:

1. **Word unigrams** — for excess-vocabulary discovery (lowercased, alphabetic, ≥3 chars).
2. **Typographic features** — em dash `—`, en dash `–`, semicolon, curly quotes, bullet lists.
3. **Formulaic LLM tells** — `not only ... but also`, `it is important to note`,
   `it is worth noting`, `in today's`, ordinal-heavy enumeration.
4. **Sentence statistics** — mean sentence length, dispersion, type-token ratio.

Typographic and formulaic features are a *second, independent channel* from vocabulary. A
genuine diffusion should move both; a corpus-formatting artefact should move only one.

## 5. Estimator: excess vocabulary

For corpus *c*, word *w*, month *m*: rate `r = count / total tokens`.

**Counterfactual.** Fit a log-linear model with month-of-year seasonality on the *pre-period*
(2019-01 … 2022-10):

```
log r(w,m) = a_w + b_w * t + seasonal(m) + e
```

Extrapolate to 2022-11 … 2026-10. **Excess** = `log(observed / predicted)`.

**Marker discovery.** Rank words by mean excess in 2023-01 … 2026-10. Candidate markers must:

- have a stable pre-period trend (|b_w| small, no structural break before 2022),
- replicate in *at least two corpora independently*, and
- match the published LLM lexical profile (delve, intricate, pivotal, underscore,
  meticulous, bolster, realm, tapestry, comprehensive, multifaceted, nuanced, …).

**Composite index.** For a validated marker set `M`, the corpus-month index is the median
standardised log-excess over `M`. Median (not mean) protects against a single word driving
the result.

**Validation is out-of-sample.** Markers discovered in arXiv are evaluated in PubMed and HN
without re-fitting. Replication is the test.

## 6. The clock

Fit a logistic diffusion curve to the index by month:

```
index(m) = K / (1 + exp(-g (m - m0)))
```

Report: **onset** (10% of K), **half-adoption date** (50% of K), **saturation** (90% of K),
growth rate `g`, and bootstrap CIs clustered on documents. The half-adoption date is the
headline "clock" number per corpus.

## 7. Identification and falsification

The project is judged on whether it can fail.

1. **Placebo launch dates.** Re-run the analysis pretending the shock occurred in 2020 and in
   2021. A real break at 2022-11 should not appear at fake dates.
2. **Placebo vocabulary.** Draw random words matched on pre-period frequency and trend; their
   post-2022 excess distribution is the null.
3. **Negative control corpus.** NVD descriptions should show ~zero excess. A positive result
   there falsifies the method.
4. **Within-topic analysis.** Restrict arXiv to a single category to rule out topic-mix drift.
5. **Formatting artefacts.** Check whether the effect survives after excluding LaTeX/markup
   tokens and after controlling for document length.
6. **Second channel.** The typographic index must agree in sign and timing with the lexical
   index.

## 8. Deliverables

- Reproducible pipeline (`src/corpora/`, `src/features.py`, `src/excess.py`, `src/clock.py`).
- `analysis/results.json` — every number in the paper, machine-generated.
- `scripts/verify_claims.py` — asserts each manuscript claim against `results.json`.
- Publication figures (300 dpi) and a full manuscript with a real bibliography.
- Fitted clock: onset / half-adoption / saturation per corpus, with CIs.

## 9. Limits (stated in the paper)

- Corpus-level inference only; no document labelling.
- Stylistic drift is *consistent with* LLM assistance, not proof of authorship.
- Corpora are not representative of the whole web; they are selected registers.
- Models changed over the window, so the marker set is a moving target; we report sensitivity
  to marker choice rather than a single number.
- Observational design: the 2022-11 break is dated, not causally identified.
