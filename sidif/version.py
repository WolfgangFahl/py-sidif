"""
Created on 2026-08-11

@author: wf
"""
from dataclasses import dataclass

import sidif


@dataclass
class Version:
    """
    Version handling for py-sidif
    """

    name = "py-sidif"
    version = sidif.__version__
    date = "2020-11-06"
    updated = "2026-08-11"
    description = "SiDIF Simple Data Interchange Format parser"

    authors = "Wolfgang Fahl"

    doc_url = "https://wiki.bitplan.com/index.php/Py-sidif"
    chat_url = "https://github.com/WolfgangFahl/py-sidif/discussions"
    cm_url = "https://github.com/WolfgangFahl/py-sidif"

    license = f"""Copyright 2020-2026 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied."""

    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""
