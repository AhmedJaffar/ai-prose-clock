# When Does the Clock Tick?

**A falsification-first audit of excess-vocabulary estimates of LLM-assisted writing, 2019–2026.**

Excess-vocabulary estimators infer how much text is LLM-influenced from the post-2022
rise of words that language models over-use. They are now used to produce widely quoted
prevalence numbers — which disagree by an order of magnitude. This repository asks a
prior question: **under what conditions does the estimator produce a trustworthy dated
result, and when does it fail?**

## Headline results

| Corpus | Register | Documents | Verdict |
|---|---|---:|---|
| PubMed | biomedical abstracts | 93,801 | **Clock identified**: half-adoption **2023-09** (95% CI 2023-05..2024-06), R² = 0.78, specificity **p = 0.005** |
| arXiv | CS / maths / physics abstracts | 93,833 | **Not identified**: index non-monotonic, R² ≈ 0, specificity p = 0.49 |
| NVD | templated CVE descriptions | 75,247 | **Uninformative control**: only 1 of 45 pre-registered markers estimable |

Three findings:

1. The same pipeline, markers and window give a clean, specificity-confirmed diffusion in
   biomedical abstracts and **no identifiable curve** in arXiv abstracts. Prevalence claims
   must be register-specific.
2. **Data-driven marker fallback manufactures results.** Our first implementation fell back
   to the words with the largest rise when too few pre-registered markers qualified. On the
   control corpus this produced half-adoption 2023-06, R² = 0.91 and a spurious effect of
   +1.80 log units — four times the real biomedical effect. Selection on the outcome looks
   *better* in every output. The fallback was removed.
3. Templated corpora often lack the marker vocabulary entirely, so a null there is not
   evidence that the method is valid.

## What this project does not claim

- It does **not** introduce the excess-vocabulary method — that is Kobak et al.
  (*Science Advances* 2025).
- It does **not** report a new prevalence estimate; diffusion curves have already been
  published (e.g. Siler, *PNAS* 2026).
- It does **not** label individual documents as AI-written.

See [`paper/prior_art.md`](paper/prior_art.md) for the full, deliberately hostile prior-art
review and [`paper/novelty.md`](paper/novelty.md) for the honest novelty assessment.

## Method in one paragraph

For every word, fit `log(rate) = a + b·t + seasonal(t)` on 2019-01…2022-10 and extrapolate
the counterfactual; define **excess** as the log ratio of observed to predicted. Build an
index as the median excess over a **pre-registered** marker list — never from words chosen
for having risen. Fit a logistic diffusion curve and report onset, half-adoption and
saturation with bootstrap intervals, gated on R². Falsify with (i) synthetic recovery,
(ii) a within-corpus permutation specificity test, (iii) a placebo break date, and (iv) a
templated negative control.

## Reproduce

```bash
git clone https://github.com/AhmedJaffar/ai-prose-clock
cd ai-prose-clock
make all        # venv + corpora + features + validation + analysis + figures + checks
```

Corpora are public APIs (Europe PMC, arXiv, NIST NVD) and are cached and resumable. Raw
third-party text is not redistributed.

## Layout

```
src/            estimator, clock, features, simulation, corpus modules
scripts/        fetch -> features -> analysis -> figures -> verify_claims
paper/          manuscript, article, prior art, novelty assessment, bibliography
analysis/       results.json, tables.md, simulation_validation.json  (generated)
figures/        five publication figures, 300 dpi                     (generated)
```

## Status

Working paper / preprint draft. Every number quoted in `paper/manuscript.md` is generated
from `analysis/results.json` and checked by `scripts/verify_claims.py`.

## Citation

```bibtex
@misc{jaffar2026clocktick,
  author = {Jaffar, Ahmed},
  title  = {When Does the Clock Tick? A Falsification-First Audit of
            Excess-Vocabulary Estimates of LLM-Assisted Writing},
  year   = {2026},
  note   = {Preprint. Code: https://github.com/AhmedJaffar/ai-prose-clock}
}
```

## License

Code MIT; derived aggregates CC BY 4.0. Third-party raw text remains under its original
terms and is not redistributed.
