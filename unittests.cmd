del .coverage
for /r . %%f in (test_*.py) DO python -m coverage run --source=asn1editor -a -m unittest %%f -v
python -m coverage html -d coverage