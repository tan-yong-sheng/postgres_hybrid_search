# Guide to Pytest

1. Pytest directory

```
project\
  └── ....

test\
  └── __init__.py # very important file to initialize pytest
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