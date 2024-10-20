# Guide to Pytest

1. Pytest directory

```
project\
  └── ....

test\
  └── __init__.py # very important file to initialize pytest
  └── conftest.py
  └── project/
      └── ....
```


2. Common pytest commands:

`pytest tests`

Print out the output that you call via `print()` inside the tests:
`pytest tests -s`

Verbose mode
`pytest tests -v`

3. Generate a pytest coverage report

`pytest --cov --cov-report=html:coverage_re`

4. Set up automated pytest & coverage report via github actions

Reference: https://pytest-with-eric.com/integrations/pytest-github-actions/

```yml
name: Run Unit Test via Pytest  
  
on: [push]  
  
jobs:  
  build:  
    runs-on: ubuntu-latest  
    strategy:  
      matrix:  
        python-version: ["3.10"]  
  
    steps:  
      - uses: actions/checkout@v3  
      - name: Set up Python ${{ matrix.python-version }}  
        uses: actions/setup-python@v4  
        with:  
          python-version: ${{ matrix.python-version }}  
      - name: Install dependencies  
        run: |  
          python -m pip install --upgrade pip  
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi  
      - name: Lint with Ruff  
        run: |  
          pip install ruff  
          ruff --format=github --target-version=py310 .  
        continue-on-error: true  
      - name: Test with pytest  
        run: |  
          coverage run -m pytest  -v -s  
      - name: Generate Coverage Report  
        run: |  
          coverage report -m
```