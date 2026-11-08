# The AI-writing detector that works in medicine and fails in physics

*Draft article — for a blog / Substack / LinkedIn post. Every number below is produced by the pipeline in this repository and checked by `scripts/verify_claims.py`.*

---

Everyone wants to know how much of what you read was written by an AI. The honest answer is that nobody knows, and the numbers in circulation disagree wildly — some studies say under 10% of new academic text, others say more than 80%.

So I built the instrument and tried to break it.

The method is called **excess vocabulary**, and it is the best idea anyone has had about this problem. You don't try to detect a single document (detectors are unreliable and biased against non-native English writers). Instead you ask: which *words* got suddenly more common after ChatGPT came out? Fit each word's frequency trend from 2019 to October 2022, extrapolate what should have happened, and measure how far reality beats the prediction. Words that overshoot are the fingerprint of LLM prose — *delve*, *underscore*, *intricate*, *pivotal*, *fostering*.

I applied one fixed pipeline to 263,000 documents across three registers, from January 2019 to October 2026:

- **93,801 PubMed abstracts** (biomedicine)
- **93,833 arXiv abstracts** (computer science, maths, physics)
- **75,247 NVD CVE descriptions** (templated security text — the control)

Then I fitted a diffusion curve to date the shift.

## What happened

**In biomedicine, the clock ticks cleanly.** The index rises right after November 2022. Half-adoption lands at **September 2023** (95% confidence interval: May 2023 to June 2024), with R² = 0.78. The words driving it are exactly the ones you would guess: *underscoring*, *underscores*, *underscore*, *fostering*, *encompassing*.

Crucially, I checked whether *any* ten frequent words could have produced that curve. They could not: the marker words average +0.38 excess against a null of +0.01 over 5,855 eligible words — **p = 0.005**.

**In arXiv abstracts, the same instrument produces nothing.** The index rises a little in 2023–24, then collapses in 2026, and no diffusion curve fits (R² ≈ 0). The words that rise most are *llm*, *llms*, *llama*, *rag*, *lora* — not style, just the field changing its subject matter.

**In the control corpus, the control doesn't work.** Only 1 of my 45 pre-registered marker words appears often enough in CVE descriptions to estimate anything. There is no index to check. A templated corpus is not automatically a good control.

## The finding that matters most

My first version of the code had a sensible-looking fallback: if fewer than five pre-registered markers qualified for a corpus, use the words that showed the largest rise instead.

On the CVE corpus, that fallback produced a **beautiful result**. Half-adoption June 2023. R² = 0.91. Effect size +1.80 log units — nearly four times the real biomedical effect. A p-value a reviewer would love.

It was completely spurious. The "markers" were *handles*, *inline*, *mdm*, *chakra*, *sharepoint* — technology words that changed because the population of software being catalogued changed. I had selected words *because* they rose, then measured how much they rose.

That is the trap. And because it makes results look **better**, not worse, nothing in a standard analysis pipeline catches it.

I removed the fallback and rebuilt the index so that only pre-registered markers can enter it. The arXiv and CVE results above are what the honest version produces.

## Why this matters beyond my project

Several 2026 papers have estimated how much scientific writing is LLM-assisted. A PNAS paper puts it at roughly 12% (2023) rising to 57% (2025) across millions of full-text articles. The original PubMed study estimated at least 13.5% of 2024 abstracts, and its own authors later argued that no existing method yields reliable per-document estimates. Estimates across the literature span an order of magnitude.

Those studies are not wrong. But the number depends on the register, the marker list, and — as my control corpus showed — on design choices that can silently manufacture a result.

A prevalence number without a specificity test is not a measurement. It is an assertion with decimals.

## What I'm releasing

- The full pipeline, reproducible from public APIs
- A synthetic recovery test: three corpora with a known diffusion date, all recovered within one month
- The specificity permutation test
- The control-corpus diagnostics
- Every number in the paper generated from one `results.json`

The honest summary is in the title of the paper: **the clock ticks in medicine and fails in physics.** That should change how you read the next headline saying "X% of the internet is AI-generated."

---

*Code and paper: [github.com/AhmedJaffar/ai-prose-clock](https://github.com/AhmedJaffar/ai-prose-clock)*
