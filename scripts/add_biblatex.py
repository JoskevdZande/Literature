from scripts.get_biblatex import GetBiblatex
import os


def get_citations(ss_id):
    from semanticscholar import SemanticScholar
    sch = SemanticScholar()
    paper = sch.get_paper(ss_id)

    return len(paper['citations'])


cwd = os.getcwd()
diag_bib_path = os.path.join(cwd, 'diag.bib')

with open(diag_bib_path, encoding="utf8") as bibtex_file:
    diag_bib = bibtex_file.read()


doi = "10.1016/j.modpat.2023.100233"
ss_id = ""

# citations = get_citations(ss_id)
citations = 0
reader = GetBiblatex(diag_bib=diag_bib, doi=doi, num_citations=citations)

response = reader.get_bib_text()
print(response)
