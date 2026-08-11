# py-sidif
SiDIF (Simple Data Interchange Format) parser

[![pypi](https://img.shields.io/pypi/pyversions/py-sidif)](https://pypi.org/project/py-sidif/)
[![Github Actions Build](https://github.com/WolfgangFahl/py-sidif/actions/workflows/build.yml/badge.svg)](https://github.com/WolfgangFahl/py-sidif/actions/workflows/build.yml)
[![PyPI Status](https://img.shields.io/pypi/v/py-sidif.svg)](https://pypi.python.org/pypi/py-sidif/)
[![GitHub issues](https://img.shields.io/github/issues/WolfgangFahl/py-sidif.svg)](https://github.com/WolfgangFahl/py-sidif/issues)
[![GitHub closed issues](https://img.shields.io/github/issues-closed/WolfgangFahl/py-sidif.svg)](https://github.com/WolfgangFahl/py-sidif/issues/?q=is%3Aissue+is%3Aclosed)
[![API Docs](https://img.shields.io/badge/API-Documentation-blue)](https://WolfgangFahl.github.io/py-sidif/)
[![License](https://img.shields.io/github/license/WolfgangFahl/py-sidif.svg)](https://www.apache.org/licenses/LICENSE-2.0)

What it is
==========
Parser for Simple Data Interchange Format [SiDIF](http://wiki.bitplan.com/index.php/SiDIF)

Installation
============
```bash
pip install py-sidif
```

Get Sources
===========
```bash
git clone https://github.com/WolfgangFahl/py-sidif
cd py-sidif
scripts/install
```

Testing
=======
```bash
scripts/test
```

Usage
=====
Command line
------------
The `sidif` command syntax checks SiDIF files given as paths or URLs (http, https, ftp, file):
```bash
sidif --help
```
```bash
sidif sidif_examples/example1.sidif
```
```
sidif_examples/example1.sidif: ok - 10 lines, 11 triples, 0 comments
```

Library
-------
```python
from sidif.sidif import SiDIFParser

sp = SiDIFParser()
path = f"{SiDIFParser.examples_path()}/example1.sidif"
result, error = sp.parseFile(path)
assert error is None
dif = result["links"][0]
for triple in dif.triples:
    print(triple)
```

Examples
--------
The [sidif_examples](https://github.com/WolfgangFahl/py-sidif/tree/main/sidif_examples) folder ships with the package; `SiDIFParser.examples_path()` returns its location. For more see the [test cases](https://github.com/WolfgangFahl/py-sidif/tree/main/tests).

## Documentation
[Wiki](http://wiki.bitplan.com/index.php/py-sidif)

### Authors
* [Wolfgang Fahl](http://www.bitplan.com/Wolfgang_Fahl)
