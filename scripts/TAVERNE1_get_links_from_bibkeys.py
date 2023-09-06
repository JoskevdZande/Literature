import requests
# import lxml
from bs4 import BeautifulSoup
import unicodedata
import bibtexparser
from bibreader import parse_bibtex_file, get_bib_blocks
# from processbib import read_bibfile
import latexcodec
import codecs
from difflib import SequenceMatcher
import time
import pandas as pd
import os

def get_match_data(bibkey, sleep_time=5):
    best_match_url = None
    best_match_title = None
    best_match_doi = None
    title_match_ratio = None
    search_string = None

    bib = diag_bib[bibkey]
    bib_title = bib['title'].strip()
    if 'doi' in bib:
        bib_doi = bib['doi']
    else:
        bib_doi = None
    bib_authors_name_string = ' '.join([name[2] for name in bib['author']])
            
    # SEARCH
    search_string = bib_title.strip() + ' ' + bib_authors_name_string
    search_string = search_string.replace(':', '')
    plus_search_string = search_string.replace(' ', '+')
    search_url = f'https://repository.ubn.ru.nl/discover?query={plus_search_string}&scope='
    time.sleep(sleep_time)
    additional_sleep_time = 10
    good_response = False
    while good_response == False:
        r_search = requests.get(search_url)
        if r_search.status_code == 429:
            time.sleep(additional_sleep_time)
            print(f'----429 response, slept for {additional_sleep_time} seconds (search request)')
            # sleep_time += 5
        else:
            good_response = True
    bs_search = BeautifulSoup(r_search.text, 'lxml')
    search_results = bs_search.find('div', id='aspect_discovery_SimpleSearch_div_search-results')

    # SEACH RESULTS
    results = search_results.find_all('div', class_='artifact-description')
    len_results = len(results)
    # If no results found
    if len_results == 0:
        return [bibkey, best_match_url,
                bib_title, bib_doi,
                best_match_title, best_match_doi,
                title_match_ratio, (bib_doi == best_match_doi) if bib_doi != None else False, search_string]

    # If results: find best title match
    ratios = []
    for result in results:
        match_title = result.a.h4.text.strip()
        a = bib_title.strip().lower()
        b = match_title.strip().lower()
        # TITLE RATIO
        title_match_ratio = SequenceMatcher(a=a, b=b).ratio()
        ratios.append(title_match_ratio)
    best_ratio_index = ratios.index(max(ratios))

    # try:
    if True:
        best_result = results[best_ratio_index]
        best_match_slug = best_result.a['href']
        best_match_title = best_result.a.h4.text.strip()
        a = bib_title.strip().lower()
        b = best_match_title.strip().lower()
        # TITLE RATIO
        title_match_ratio = SequenceMatcher(a=a, b=b).ratio()

        # First result page
        repo_url_base = "https://repository.ubn.ru.nl"
        best_match_url = repo_url_base + best_match_slug
        time.sleep(sleep_time)
        good_response = False
        while good_response == False:
            r_best_match = requests.get(best_match_url)
            if r_best_match.status_code == 429:
                time.sleep(additional_sleep_time)
                print(f'----429 response: slept for {additional_sleep_time} seconds (best match request) ')
                # sleep_time += 5
            else:
                good_response = True
        bs_best_match = BeautifulSoup(r_best_match.text, 'lxml')
        best_match_doi_div = bs_best_match.find('div', class_='simple-item-view-doi')
        # DOI
        if best_match_doi_div == None:
            best_match_doi = None
        else:
            best_match_doi = best_match_doi_div.a['href']
    # except Exception as e:
    #     print("--IN SEARCH LOOP--")
    #     print(bibkey, repr(e))
    #     exception = repr(e)

    # if title_match_ratio > 0.9 and bib_doi == best_match_doi:
    return [bibkey, best_match_url,
            bib_title, bib_doi,
            best_match_title, best_match_doi,
            title_match_ratio, (bib_doi == best_match_doi) if bib_doi != None else False, search_string]
    # else:
    #     return [bibkey, bib_title, bib_doi, None, title_match_ratio, best_match_doi]


# LOAD BIB FILES
diag_bib_path = r'..\diag.bib'  # r'C:\Users\joeyspronck\Downloads\diag.bib'
fullstrings_path = r'..\fullstrings.bib'  # r'C:\Users\joeyspronck\Downloads\fullstrings.bib'

diag_bib = parse_bibtex_file(diag_bib_path, fullstrings_path)\

with open(r'script_data\taverne_bibkeys.txt', 'r') as file:
    bibkeys = file.read().splitlines()    
    
match_data_list = []
founds = []
not_found_in_bib = []
not_found_in_taverne = []
columns = ['bibkey', 'url',
           'bib_title', 'bib_doi',
           'match_title', 'match_doi',
           'title_match_ratio', 'same_doi', 'search_string']

for idx, bibkey in enumerate(bibkeys):
    if idx % 1 == 0:
        print(f'---[{idx+1}/{len(bibkeys)}]---')
    print(bibkey)

    if True:
    # try:
        match_data = get_match_data(bibkey.lower())
        [print(col+':', val) for col, val in zip(columns, match_data)];
        print('\n')
    # except Exception as e:
    #     print('--IN BIBKEY LOOP--')
    #     print(bibkey, '  \t', repr(e))
    #     not_found_in_bib.append([bibkey, e])
    #     # publication_page_url = repr(e)
    #     continue               

    match_data_list.append(match_data)
print('DONE')

df = pd.DataFrame(match_data_list, columns=columns)
df.to_csv(r'script_data\taverne_links.csv', index=False)
