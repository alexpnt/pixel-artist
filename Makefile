.PHONY: docs

init:
	virtualenv venv
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements/requirements-dev.txt

build:
	python setup.py sdist bdist_wheel

dist:
	pip install --upgrade build
	python -m build

publish:
	pip install --upgrade twine
	twine upload dist/*

publish-test:
	pip install --upgrade twine
	twine upload --verbose --repository testpypi dist/*

clean:
	rm -rf build dist .egg pixel_artist.egg-info
