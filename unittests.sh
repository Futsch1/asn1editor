rm -f .coverage
shopt -s globstar
for i in **/test_*.py; do
  $PYTHON -m coverage run --source=asn1editor -a -m unittest $i -v
done
$PYTHON -m coverage html -d coverage