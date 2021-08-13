rm -rf build
rm -rf dist
rm -rf pyhac.egg-info
python setup.py sdist
python setup.py bdist_wheel --universal
twine upload dist/*
