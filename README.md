## Bakula

### Testing

All test files in Bakula should be written with unittest, and should live
inside *_test.py files in the same directory as the unit under test. To run
all unit tests, execute the following command (this will install nose as
a test dependency):

```bash
python setup.py test
```

### Formatting

To check the formatting of all code against PEP8, run the following command:

```bash
python setup.py pep8
```