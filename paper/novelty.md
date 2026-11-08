# Novelty assessment — *The AI Prose Clock*

**Verdict in brief.** The estimator is Kobak et al.'s (2024/2025). The cross-domain adoption curve is Liang et al.'s (2025). The word "diffusion" applied to exactly this measurement is already in a PNAS title (Siler 2026) and in an MDPI title about abstracts (Alani & Jansen 2026). The typographic second channel, with preregistration and placebo cut-offs, is Czuma's (2026). What remains unclaimed is narrow but real: a **negative-control register**, **cross-register out-of-sample marker replication**, and a **fitted logistic clock reported as dated phase transitions with intervals**. As currently framed — "detection-free measurement of the diffusion of LLM-style writing across the open web" — the paper claims a niche that three other papers already occupy. As a *falsification-first comparative measurement* paper it is defensible and arXiv-worthy. It is not a new method, and it should not say it is.

---

## (a) What is genuinely new

Ranked by how well it survives a hostile referee.

1. **The negative-control corpus.** No paper I found uses a deliberately templated, low-plausibility-of-LLM-authorship corpus to falsify an excess-vocabulary estimator. Czuma (2026a) uses placebo *cut-off dates*; Lee (2026) uses split-half sets, subject-matter controls and translation-route controls; Holzwarth et al. (2026) validate against known-LLM control abstracts. None of these is a *register-level* negative control. If the design works, this is a real methodological contribution: it converts "our index went up" into "our index went up here and not there, and we said where 'there' was in advance."

2. **The logistic clock as the reported estimand.** Every prevalence paper in this literature reports levels, ratios or bounds: 13.5%, 57%, 89%, 18%/24%/14%, 9% peak. **None reports onset, half-adoption date, saturation level and growth rate with confidence intervals as the headline quantity.** Dating is a different question from sizing, and it is the question a diffusion framing makes natural. This is a genuine, if modest, contribution — but only if the intervals are honest and the model is not over-claimed.

3. **Cross-register out-of-sample marker replication.** Kobak, Holzwarth, Lee, Siler, Matsui, Thelwall, Sanger are all within-corpus. Liang et al. (2025) apply one framework across four domains but do not report "markers discovered in corpus A, evaluated without refitting in corpus B" as an identification test. This is the strongest available defence against the "you found words that happen to trend" objection, and it appears to be unclaimed.

4. **Hacker News as a measured register.** No peer-reviewed measurement exists. (Grey literature: Dead Internet Monitor claims 12.5%.) This is a real gap, but a thin one — a single informal-tech register is not a contribution on its own, and a reviewer may reasonably ask why HN rather than Reddit, which La Cava et al. (2026) have already done properly.

5. **The register-gradient design itself** — several registers measured by one pipeline, spanning technical/scientific → biomedical → informal tech → corporate/legal → templated, with adoption expected to differ sharply. This is the most interesting *scientific* idea in the project, because it turns the paper from "another prevalence estimate" into "a test of whether the same shock propagates at different rates through different institutions." Nobody has done that with a harmonised detection-free estimator. The trouble is that the paper currently frames this as a validation device rather than as the finding.

## (b) What is incremental

- **Excess vocabulary with a pre-period log-rate trend and extrapolated counterfactual.** Kobak et al. 2024/2025. Verbatim.
- **Month-of-year seasonality in the counterfactual.** A sensible engineering addition, not a contribution. Note that Lee (2026) and Holzwarth (2026) already handle period structure; seasonality is a detail.
- **Composite index by median standardised excess.** Reasonable robustness; not novel.
- **Placebo launch dates.** Czuma (2026a) preregistered three placebo cut-offs and reports them null. Lee (2026) reports placebo floors. This is now table stakes, not a novelty.
- **Placebo vocabulary matched on pre-period frequency and trend.** Standard null construction; Lee's split-half re-selection is a stronger version.
- **The typographic channel (em dash, curly quotes, semicolons).** Czuma 2026a and 2026b, preregistered, in two corpora, with within-author panels. The project cannot claim this as new, and — more uncomfortably — Czuma's design is *better* than the one in DESIGN.md §7.
- **Corpus-level inference only, no document labelling.** This is now the explicit stance of Czuma (2026a) ("a population-level marker, not a per-release authorship detector") and the implicit stance of the whole excess-vocabulary literature. It reads as a caveat, not a contribution.
- **Bootstrapped CIs clustered on documents.** Standard.
- **arXiv / PubMed / SEC EDGAR corpora.** All previously studied, some exhaustively (15M abstracts; 7.3M full texts; 7.3M more).

## (c) The single most threatening prior work

**Siler, K. (2026). "The diffusion of large language models in published academic articles." *PNAS* 123(22). DOI 10.1073/pnas.2605754123.**

Why this one, and not Liang et al. or Kobak:

- **It owns the word.** The paper the project wants to write is titled *"The AI Prose Clock: measurement of the **diffusion** of LLM-style writing."* Siler's title is *"The **diffusion** of large language models in published academic articles."* A referee who has read it will regard the framing as occupied, and the project's own title as an unearned appropriation of it.
- **It uses the same measurement logic.** A lexicon of 228 "focal words" exhibiting sharp post-2022 frequency increases "consistent with LLM output," then per-article scoring on focal-word rate. That is excess vocabulary → marker set → index, i.e. the AI Prose Clock's pipeline, minus the logistic curve.
- **It already produces the time course.** 12% of articles in 2023 → **57% in 2025**, over 7.3M full texts from Elsevier, Frontiers, MDPI and PLoS, 2020–2025. The project's "clock" would have to produce a materially different or better-resolved trajectory to matter, and it will be working with corpora that are one to three orders of magnitude smaller.
- **It already does the heterogeneity analysis** the project would want to claim as its payoff: difference-in-differences across region, institutional rank, publisher, discipline and journal tier, with economic development and anglophone proximity as predictors, and the counter-intuitive finding that lower-ranked institutions show *higher* rates than elite universities.
- **It is peer-reviewed at a top venue.** This matters for how the project's own claims will be weighted. "We measure diffusion across the open web" is a weaker sentence when a PNAS paper has measured it across 7.3M articles, and a 2025 *Patterns* paper has measured it across four non-academic domains.
- **It is recent enough to be missed.** May 2026. A paper drafted against the 2024–2025 literature — which is what the current DESIGN.md reference frame looks like — will not cite it, and that omission alone signals to a referee that the authors are not current.

**Runner-up, and in some ways more damaging: Holzwarth, González-Márquez & Kobak (2026), arXiv:2608.10715.** Not because it competes on scope, but because the original authors of the method state that **"no existing method can produce reliable estimates"** and then supply a replacement. If the AI Prose Clock uses the 2024 estimator unchanged, it is using the version its own inventors have disavowed, in a paper whose central claim is precision of dating. That is a harder objection to answer than "Siler did it bigger."

**Third: Czuma (2026a).** It does not compete for the headline, but it takes the second channel, the preregistration, the placebo discipline and the "population-level marker, not a detector" framing — and it reaches a finding that contradicts the project's model: **no discontinuity at the ChatGPT cut-off, only post-period acceleration.**

## (d) Top three reviewer objections, and the best pre-emptive response

### Objection 1 — "This is Kobak/Siler with extra corpora. What is new?"

The most likely rejection reason, and the one the current framing invites.

**Response.** Concede the estimator immediately and in the first paragraph, then relocate the contribution. The defensible claim is not "we measure diffusion" but:

> *Prior prevalence estimates disagree by a factor of twenty — 9% (Reddit), 13.5% (PubMed abstracts, 2024 estimator), 57% (publisher full texts), 89% (PMC full texts, 2026 estimator). That spread is not measurement error around a true value; it is estimator-and-corpus dependence. We hold the estimator fixed, vary the register, and report where and when the shift appears — including a register where it should not.*

That is a real question, it is not Siler's question, and the project's design already answers it. Concretely, the paper must: (i) cite Kobak 2025, Holzwarth 2026, Siler 2026, Liang 2025 and Lee 2026 in the introduction and state the delta explicitly; (ii) include a **head-to-head comparison** — run the project's estimator on a PubMed subsample and check it against Kobak's published number, and on PMC-style full text against Holzwarth's; (iii) drop "we introduce" language for anything that is borrowed.

An even stronger move, if there is time: make the estimator comparison the paper. Lee (2026) reports 3.5–33% under one discipline and 42–72% under Holzwarth's estimator **on the same data**. Nobody has published a systematic head-to-head of excess-vocabulary prevalence estimators on shared corpora. That paper does not exist, it is more useful than another point estimate, and this project has most of the machinery to write it.

### Objection 2 — "Your negative control is not a negative control."

This is the objection that can falsify the paper rather than merely diminish it, and DESIGN.md currently treats the CVE corpus as the design's strongest feature.

The problem is empirical, not rhetorical: **CVE descriptions are themselves increasingly LLM-generated.** There is public evidence of exactly this and of the resulting data-quality damage ("LLM Generated CVE Descriptions Undermine Security Data Quality and Trust", VulDB, 2026), and NVD has had well-documented enrichment backlogs that would themselves produce non-stationarity. So the control is (i) plausibly contaminated, (ii) subject to its own structural breaks, and (iii) templated in a way that makes the pre-period trend fit unstable. If CVE descriptions show excess, the project cannot distinguish "the method is broken" from "people are using LLMs to write CVE descriptions" — which destroys the falsification logic entirely.

**Response, in order of preference.**
1. **Pre-register the control before looking at it**, and define in advance what counts as failure (e.g. post-2022 mean excess above the 95th percentile of the placebo-word null). A control that can only be interpreted after the fact is not a control.
2. **Show the control is clean.** Report the CVE corpus's own pre-trend stability, its markup/templating share, and — critically — evidence about whether its text is machine-generated. If it is not clean, say so and demote it from "negative control" to "low-adoption register," which is what it actually is.
3. **Add a genuinely machine-generated control.** The only corpus whose text is certainly not LLM-written is one that is provably machine-produced by a fixed template (structured schema fields, generated boilerplate, or text produced by a deterministic generator). This is unglamorous but unimpeachable, and it is the version of the control that a referee cannot argue with.
4. **Report the control's excess rather than asserting it is ~zero.** If it is not ~zero, that is a finding about NVD, and it belongs in the paper.

### Objection 3 — "The logistic model is not identified, and the break is not identified."

Two distinct problems that the DESIGN.md currently conflates.

*(i) Statistical.* `K / (1 + exp(-g(m - m0)))` has three free parameters fitted to a standardised index whose **scale is arbitrary** — the index is a median standardised log-excess, so `K` is not identified in any interpretable unit, and `K` and `g` trade off against each other along a ridge. Reported "onset = 10% of K" and "saturation = 90% of K" are therefore artefacts of a normalisation choice, not physical quantities. Bootstrap CIs on `m0` will be optimistic if the ridge is not handled.

*(ii) Substantive.* The literature has already found that the clean-onset premise is false. Czuma (2026a): **no step at the ChatGPT cut-off, only post-period acceleration.** Kosch et al. (2026): in 44 years of CHI, **the word-level shift began before any author used LLMs**. Nakajima & Mizuno (2026): marker sets decay as models turn over. A single-onset logistic cannot represent a change in slope on top of pre-existing drift, which is what the evidence describes.

**Response.** Reframe the clock as a **model-comparison** rather than a single fit: compare (1) constant trend, (2) break in level at 2022-11, (3) break in slope at 2022-11, (4) logistic saturation, by information criterion and out-of-sample predictive accuracy. Then report `m0` **conditional on the logistic being the best-supported form**, and report the slope-break date as the primary estimate if it is. This is more honest, it is more interesting, and it directly engages Czuma's and Kosch's findings instead of being contradicted by them. Additionally: fix the index scale by anchoring to a physical unit (e.g. excess per 10,000 tokens) or report `K` only as a ratio to a reference corpus; and pre-register the marker set so that `K` is not re-estimated post hoc.

**Honourable mentions** worth a sentence each in the limitations: the index has unknown sensitivity/specificity, whereas Visokay et al. (2026) propagate explicit detector error rates through a Bayesian hierarchy — the paper should say why it prefers an uncalibrated index to a calibrated one (answer: because detector error rates are corpus-dependent and unvalidated out of distribution, per Liang 2023 and Sadasivan 2023 — but say it); and stylistic drift is consistent with, not proof of, LLM assistance, which every paper in this literature now says and which therefore buys no credit.

## (e) Is this arXiv-worthy as-is?

**Yes — as an arXiv preprint, with two conditions. No — as a submission to a selective venue, in its current framing.**

*Why arXiv-worthy.* The corpora are assembled, the pipeline is reproducible, the falsification plan is more explicit than most of the literature's, and the register-gradient question is genuinely open. An arXiv paper that says "here is a harmonised detection-free clock applied across five registers, with a pre-registered negative control, and here is where the existing estimates disagree" is a useful contribution and will be cited, particularly if it also reports the estimator disagreement.

*Why not selective-venue-ready.* Three reasons, all fixable but none trivially:
1. The headline claim ("we measure the diffusion of LLM-style writing across the open web") is already published, at higher prestige and larger scale, under the same noun.
2. The negative control — the design's best idea — is empirically compromised as specified, and fixing it means either finding a genuinely machine-generated corpus or demoting the CVE corpus and losing the falsification story.
3. The logistic-with-onset model is contradicted by two 2026 papers that find no discontinuity at the cut-off. A referee in this area will know both.

*What would make it strong.* Reframe from "we introduce a clock" to "**we compare clocks**": hold the estimator fixed, vary the register, report where the shift does and does not appear, and use the disagreement between published prevalence estimates as the motivating puzzle rather than as an inconvenience. If the paper also reports a head-to-head of the Kobak-2024 and Holzwarth-2026 estimators on shared corpora, it becomes the paper that explains why the field's numbers range from 9% to 89% — which is a more valuable contribution than a sixth point estimate, and one that nobody has made.

**Timing.** Siler (May 2026), Holzwarth (Aug 2026), Czuma (Aug 2026), Kosch (Sep 2026), Hubarava & Ineichen (Oct 2026), Visokay (Oct 2026). The niche is being closed in real time. Post to arXiv soon and revise; do not wait for a polished version, because the polished version's claim will be staler than the draft's.

**One thing to stop saying.** "Detection-free" is not a differentiator. Visokay et al. (2026) achieve web-scale prevalence with detectors *and* explicit error modelling, and Liang et al. (2025) use word frequencies at scale. Detection-free is a *design constraint with a known cost* (no sensitivity/specificity), not a selling point. It should be presented as a trade-off the paper accepts and defends, not as an advance.
