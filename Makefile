release:
	python setup.py sdist bdist_wheel

deploy:
	python -m twine upload --repository-url https://pypi.org/ dist/*

clean:
	rm -rf operator_courier.egg-info
	rm -rf build
	rm -rf dist
