from scripts.get_biblatex import GetBiblatex

diag_bib = r"C:\Users\drepeeters\OneDrive - Radboudumc\Desktop\webteam\Literature\diag.bib"
doi = "10.1186/s12903-023-03362-8"
reader = GetBiblatex(diag_bib=diag_bib, doi=doi)

response = reader.get_bib_text()
print(response)