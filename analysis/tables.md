# Result tables

Generated from `analysis/results.json`.

## Table 1. Corpora

| Corpus | Months | Tokens analysed | Distinct words | Role |
|---|---:|---:|---:|---|
| arxiv | 94 | 15,609,614 | 10,577 | treated |
| pubmed | 94 | 21,103,921 | 17,282 | treated |
| nvd | - | - | - | skipped: insufficient_estimable_markers |

## Table 2. Diffusion clock

| Corpus | Onset (10%) | Half-adoption (50%) | Saturation (90%) | R² |
|---|---|---|---|---:|
| pubmed | 2022-12 | **2023-09** | 2024-05 | 0.78 |

## Table 3. Half-adoption dates with bootstrap CIs and diagnostics

| Corpus | Half-adoption | 95% CI | Pre-period excess | Post-period excess | Change | Placebo (fake 2020 break) |
|---|---|---|---:|---:|---:|---:|
| arxiv | - | - .. - | 0.050 | -0.007 | -0.057 | -0.009 |
| pubmed | 2023-09 | 2023-05 .. 2024-06 | 0.023 | 0.455 | 0.432 | -0.225 |

## Table 4. Largest post-2022 excess words (data-driven)

**arxiv:** llm (4.45), llms (3.94), llama (3.80), cot (3.19), rag (3.14), vlms (3.03), pmod (2.89), mllms (2.88), chatgpt (2.77), instruct (2.66), lora (2.66), qwen (2.60), icl (2.50), gemini (2.49), agentic (2.47)

**pubmed:** underscoring (2.48), pcv (2.26), tibia (2.21), landmark (2.19), chatgpt (2.16), prompting (2.15), underscores (2.04), underscore (2.02), sox (1.95), fostering (1.90), dengue (1.85), pms (1.85), ptb (1.84), establishes (1.84), encompassing (1.77)

## Table 5. Pre-registered markers available per corpus

| Corpus | Markers used | Source |
|---|---:|---|
| arxiv | 11 | pre_registered |
| pubmed | 10 | pre_registered |

## Table 6. Typographic channel clock

| Corpus | Half-adoption | Onset | Saturation |
|---|---|---|---|
