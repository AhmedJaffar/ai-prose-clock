.PHONY: all venv corpora features analysis figures verify clean

PY := ./.venv/bin/python

all: venv corpora features analysis figures verify

venv:
	python3 -m venv .venv
	$(PY) -m pip install -q --upgrade pip
	$(PY) -m pip install -q -r requirements.txt

corpora:
	$(PY) scripts/fetch_scholarly.py all
	$(PY) scripts/build_corpora_web.py all

features:
	$(PY) scripts/extract_features.py

analysis:
	$(PY) scripts/simulate_validation.py
	$(PY) scripts/run_analysis.py

figures:
	$(PY) scripts/make_figures.py

verify:
	$(PY) scripts/verify_claims.py

clean:
	rm -rf data/cache data/generated analysis/*.json figures/*.png
