"""Word lists used by the clock.

``LLM_MARKERS_PRE`` is the **pre-registered** marker set: it is fixed before any
corpus is analysed, so that the composite index is not built from words chosen
after seeing the outcome.  It is compiled from the published literature on
LLM lexical signatures (to be reconciled line-by-line with
``paper/marker_sources.md``; changes are versioned in git).

``DISCOVERY_BLACKLIST`` words are excluded from data-driven marker discovery
because they are boilerplate, corpus-specific metadata, or numbers - not prose.
"""

# Pre-registered markers. Lowercase, single tokens.
LLM_MARKERS_PRE = [
    # the "delve" cluster
    "delve",
    "delves",
    "delving",
    "intricate",
    "intricacies",
    "pivotal",
    "underscore",
    "underscores",
    "underscoring",
    "meticulous",
    "meticulously",
    # hedging / booster adverbs over-represented in LLM prose
    "notably",
    "arguably",
    "ultimately",
    "crucially",
    "importantly",
    # evaluative adjectives
    "multifaceted",
    "nuanced",
    "holistic",
    "seamless",
    "seamlessly",
    "comprehensive",
    "robust",
    "transformative",
    "unprecedented",
    "paramount",
    # academic-LLM verbs
    "leverage",
    "leverages",
    "leveraging",
    "harness",
    "harnessing",
    "foster",
    "fostering",
    "garner",
    "garnered",
    "bolster",
    "bolsters",
    "bolstered",
    # nouns
    "realm",
    "tapestry",
    "landscape",
    "paradigm",
    "synergy",
    "journey",
    "endeavor",
]

# Boilerplate / metadata tokens that must never be treated as discovered markers.
DISCOVERY_BLACKLIST = {
    "et", "al", "fig", "figure", "table", "eq", "ref", "http", "https", "www",
    "arxiv", "doi", "abstract", "introduction", "conclusion", "references",
    "we", "our", "this", "that", "the", "and", "of", "to", "in", "is", "are",
}
