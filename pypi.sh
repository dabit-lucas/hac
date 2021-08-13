rmdir /s /q build
rmdir /s /q dist
rmdir /s /q pyhac.egg-info
python setup.py sdist
python setup.py bdist_wheel --universal
twine upload dist/*
