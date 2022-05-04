import shutil
import string
import pandas as pd

from pathlib import Path
from pybtex.database import parse_string
from thefuzz import fuzz

pubdir = Path(r"C:\Users\Nikolas\Documents\Taverne")  # folder with Excel sheets from the library
bibdir = Path(r"D:\Literature")  # folder with a clone of diag-literature

# Create or clean up output directory for PDF files
dstdir = pubdir / "pdf"
if dstdir.exists():
    for pdffile in dstdir.glob("*.pdf"):
        pdffile.unlink()
else:
    dstdir.mkdir()

# Read list of all our publications from bibtex file
with open(bibdir / "fullstrings.bib") as fp:
    bibstr = fp.read()
with open(bibdir / "diag.bib") as fp:
    bibstr += fp.read()

diagbib = parse_string(bibstr, bib_format="bibtex")
print(f"Read details of {len(diagbib.entries)} publications from diag.bib")

# Read list of publications supplied by library
pdfs_missing = set()
pdfs_found = set()
for excel_sheet in pubdir.glob("*.xlsx"):
    print("=" * 50)
    print(f"Reading {excel_sheet}")

    df: pd.DataFrame = pd.read_excel(excel_sheet, header=2)
    print(f"List has {len(df.index)} publications")

    # Filter out those with "pdf opvragen" note
    column_names = list(df.columns)
    df = df.rename(columns={column_names[10]: "PDF"})
    if len(column_names) > 11:
        df = df.drop(columns=column_names[11:])
    df = df.loc[pd.notna(df["PDF"])]
    print(f"Found {len(df.index)} suitable publications that miss a PDF file")

    # Check one-by-one whether we can find the PDF file
    for idx, row in df.iterrows():
        # Assemble BibTex key
        author = row["Auteur(s)"].split(",")[0].strip().split(' ')[-1]
        year = row["Jaar van uitgave"]
        author_year_key = f"{author[:4]}{str(year)[-2:]}"

        title = row["Titel"].lower()
        pdffile = None

        if title.startswith("column"):
            continue

        pdfs_missing.add(author_year_key)

        # Publication might have suffix a, b, c, ...
        for suffix in [""] + list(string.ascii_lowercase):
            k = f"{author_year_key}{suffix}"
            if k not in diagbib.entries:
                break

            # Compare title
            entry = diagbib.entries[k]
            entry_title = (
                entry.fields["title"].lower().replace("{", "").replace("}", "")
            )
            score = fuzz.ratio(entry_title, title)
            if score > 90:
                # Check whether the PDF is linked to this entry
                basename = f"{k}.pdf"
                try:
                    if basename in entry.fields["file"]:
                        pdffile = bibdir / "pdf" / basename
                except KeyError:
                    pass
                finally:
                    break

        if pdffile is None:
            error = "Could not find publication in diag.bib"
        else:
            if pdffile.exists():
                error = None
                shutil.copy(pdffile, dstdir)
                pdfs_found.add(pdffile)
            else:
                errror = "Found publication in diag.bib but there is no PDF"

        if error is not None:
            print("-" * 25)
            print(f"{author} {year} ({author_year_key})")
            print(row["Titel"])
            print(row["Journal"])
            print(f"> {error}")

print('+' * 50)
print(f'Found {len(pdfs_found)} of {len(pdfs_missing)} missing PDFs')
