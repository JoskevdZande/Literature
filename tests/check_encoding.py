"""
Script that analyzes .bib files for encoding mistakes that occur when a UTF-8
encoded file is interpreted as latin-1 encoded (or similar) and is then saved
as UTF-8 encoded file. Characters like ö appear then as Ã¶ even though the file
is now UTF-8 encoded and should be perfectly capable of containing this
character.
"""

import pytest
import re

from pathlib import Path


def recode(chars):
    for possible_encoding in ("latin_1", "windows-1252"):
        try:
            return chars.encode(possible_encoding).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

    raise ValueError(f"Could not recode '{chars}'")


@pytest.mark.parametrize("bibfile", ["diag.bib", "diagnoweb.bib", "fullstrings.bib", "medlinestrings.bib"])
def check_encoding(bibfile):
    # Compile regular expression that looks for two successive uncommon characters
    double_chars = re.compile(r"([^0-9a-zA-Z\s{}()\[\]<>.,;:?!_\-+=&/\\]{2,})")

    # Read all bib files and check if they have pairs of characters that translate
    # into a single character in UTF-8
    errors = 0
    warnings = 0

    bibfile = Path(bibfile)
    with bibfile.open("r", encoding="utf-8") as fp:
        for i, line in enumerate(fp):
            for match in double_chars.finditer(line):
                chars = match.group(0)

                try:
                    recoded = recode(chars)
                except ValueError:
                    print(
                        f"Could not interpret suspicious sequence in file {bibfile.name}, "
                        f"line {i + 1}: '{chars}'"
                    )
                    warnings += 1
                else:
                    if len(recoded) == 1:
                        print(
                            f"Found suspicious character sequence in file {bibfile.name}, "
                            f"line {i + 1}: '{chars}' which might once have been '{recoded}'"
                        )

                        # For now, treat encoding errors in diag.bib as errors and everything else
                        # only as warnings (since there are so many errors in diagnoweb.bib)
                        if bibfile.name == "diag.bib":
                            errors += 1
                        else:
                            warnings += 1

    print(f"{errors} errors, {warnings} warnings")

    # Exit with status "failed" if there were any errors
    assert errors == 0
