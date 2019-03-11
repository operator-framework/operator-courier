release:
	python setup.py sdist bdist_wheel

deploy:
	twine upload dist/*

clean:
	rm -rf operator_courier.egg-info
	rm -rf build
	rm -rf dist
