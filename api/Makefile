.PHONY: clean venv requirements.txt build_requirements
PIP=`. venv/bin/activate; which pip`

pyclean:
	@find . -name *.pyc -delete

clean%: pyclean
	@rm -rf venv

venv: clean
	virtualenv -p `which python3` venv
	$(PIP) install -U "pip"
	$(PIP) install -r requirements-root.txt

build_requirements: venv
	$(PIP) freeze -r requirements-root.txt > requirements.txt

requirements.txt: | build_requirements clean2
	@echo "Fresh requirements"

isort:
	isort -ac -rc -sg "*migrations/*.py" -s .tox .
