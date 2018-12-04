.PHONY: clean venv requirements.txt build_requirements
PIP=`. venv-requirements/bin/activate; which pip`

pyclean:
	@find . -name *.pyc -delete

clean%: pyclean
	@rm -rf venv-requirements

venv: clean
	virtualenv -p python3.6 venv-requirements
	$(PIP) install -U "pip"
	$(PIP) install -r requirements-root.txt

build_requirements: venv
	$(PIP) freeze -r requirements-root.txt > requirements.txt

requirements.txt: | build_requirements clean2
	@echo "Fresh requirements"

isort:
	isort -ac -rc -s .tox .
