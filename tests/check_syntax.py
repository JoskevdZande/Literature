import pytest

from pybtex.database import parse_string, BibliographyData


@pytest.mark.parametrize("bibfile", ["diag.bib"])
@pytest.mark.parametrize("strfile", ["fullstrings.bib"])
def check_syntax(bibfile, strfile, subtests):
    # Read file with variable names and the bib file into a single string
    with open(strfile) as fp:
        bibstr = fp.read()
    with open(bibfile) as fp:
        bibstr += fp.read()

    # Try to parse the BibTex
    diagbib = parse_string(bibstr, bib_format="bibtex")
    assert isinstance(diagbib, BibliographyData)

    # Check individual entries
    for key in diagbib.entries:
        with subtests.test(key=key):
            fields = diagbib.entries[key].fields
            assert "journaltitle" not in fields or "journal" in fields
