# Submission playbook: from repository to indexed preprint

This is the concrete path from the code in this repo to a citable preprint that
Google Scholar can find. It is written for an independent researcher with no
institutional repository and no budget.

The honest summary: publication is three separate acts.

1. **Hosting** — a stable URL with the PDF.
2. **Identification** — a DOI so machines can disambiguate the work.
3. **Indexing** — a crawler deciding to include it. You cannot apply for this.

Doing all three, in order, is what makes a preprint findable. Uploading a PDF to
ResearchGate alone accomplishes none of them reliably.

---

## 0. Minimum viable path (about one hour)

- [ ] Push the repository with a tagged release and `CITATION.cff`.
- [ ] Archive the release on **Zenodo** to mint a DOI.
- [ ] Post the PDF to **arXiv** (if endorsed) or **SocArXiv** (no endorsement needed).
- [ ] Upload the same PDF to **ResearchGate**, labelled *preprint*.
- [ ] Do **not** claim peer review anywhere.

---

## 1. GitHub release (10 minutes)

```bash
git tag -a v0.1.0 -m "AI Prose Clock v0.1.0: first public results"
git push origin v0.1.0
```

Create a release from the tag at `https://github.com/AhmedJaffar/ai-prose-clock/releases/new`.
Release notes should state: what is measured, what data are included, and what is *not*
claimed. Attach the manuscript PDF.

## 2. Zenodo DOI (15 minutes)

1. Sign in at <https://zenodo.org> with GitHub.
2. **Settings → GitHub** → toggle the repository **on**.
3. Back on GitHub, create a *new* release (or edit the existing one). Zenodo mints a DOI
   automatically and displays a badge.
4. Copy the DOI into `README.md` and `CITATION.cff`.

Zenodo gives you a version DOI *and* a concept DOI that always resolves to the latest
version. Cite the concept DOI in the README; cite the version DOI in the manuscript.

## 3. Preprint server

### arXiv (preferred for indexing, but requires endorsement)
- Category suggestion: **cs.CY** (computers and society) with **cs.CL** cross-list, or
  **stat.AP** if framed as applied statistics.
- New submitters in `cs.*` normally need an **endorsement** from an established
  arXiv author. If you lack one, arXiv's endorsement request form is the route; it can
  take days.
- arXiv's own requirement: a PDF or LaTeX source, an abstract, and a licence
  (CC BY 4.0 is fine).

### SocArXiv (no endorsement, Crossref DOI, fast)
- <https://osf.io/preprints/socarxiv> — upload the PDF, supply title/abstract/keywords,
  receive a DOI usually within minutes.
- Excellent fallback and fully Google Scholar indexed.

## 4. ResearchGate (10 minutes)

- Add the work as a **preprint**, not a publication.
- Upload the final PDF; fill title, abstract, and the DOI from Zenodo/arXiv/SocArXiv.
- Do not select a journal; do not mark it peer reviewed.

## 5. Google Scholar indexing

You cannot submit to Google Scholar. It crawls. What you *can* do is make the page
machine-readable:

- A **landing page per paper** with the title, all authors, the full abstract, and the
  publication year as plain HTML text (arXiv, SocArXiv, and Zenodo all do this).
- A PDF whose **first page repeats the title and author names**.
- Consistent author name spelling across every host: `Ahmed Jaffar`.
- A real DOI and correct year in the citation metadata.
- Highwire meta tags on any self-hosted page:
  ```html
  <meta name="citation_title" content="...">
  <meta name="citation_author" content="Jaffar, Ahmed">
  <meta name="citation_publication_date" content="2026/11/07">
  <meta name="citation_pdf_url" content="https://.../paper.pdf">
  <meta name="citation_doi" content="10.5281/zenodo.XXXXXXX">
  ```

Indexing typically takes **2–6 weeks** after the landing page is live. Check by searching
Scholar for the exact title in quotes.

## 6. What not to do

- Do not post the same PDF to five servers under five different titles; duplicate variants
  confuse Scholar and split citations.
- Do not claim "Nobel" or "never researched before" in the abstract. It is the fastest way
  to be dismissed, and it is almost never literally true.
- Do not describe a preprint as peer reviewed.
- Do not submit to a journal that charges a fee without checking its indexing.

## 7. After it is live

- Add the DOI badge to the README and to every figure caption page.
- Post a short summary on your own site with a link to the DOI (this is the crawlable entry
  point that most independent researchers actually get indexed through).
- Cite-check in 4 weeks: search `"The AI Prose Clock"` on Google Scholar.
