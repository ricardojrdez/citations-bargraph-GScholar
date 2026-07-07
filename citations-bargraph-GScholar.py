#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''Gets the citation bargraph of a Google Scholar profile 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import os
import re
import requests
from bs4 import BeautifulSoup
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import statistics
import logging
import getopt
import sys
import random
from datetime import datetime


matplotlib.rc('font', **{'family': 'serif', 'serif': ['Times']})
matplotlib.rcParams['text.usetex'] = True

__author__ = "Ricardo J. Rodríguez"
__copyright__ = "Copyright 2021, University of Zaragoza, Spain"
__credits__ = ["Ricardo J. Rodríguez"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Ricardo J. Rodríguez"
__email__ = "rjrodriguez@unizar.es"
__status__ = "Production"

default_log_level = logging.INFO
logger = logging.getLogger('main')
script_name = os.path.basename(__file__)

GSCHOLAR_ID=''
GSCHOLAR_URL="https://scholar.google.es/citations?user="

help_text = f'''usage: {script_name} [-h] [-f FILENAME] [-s start_year] [-e end_year] [-u GSCHOLAR_URL] GSCHOLAR_ID
Gets the citation bargraph of a Google Scholar profile


Options:
    -h, --help
            List all available options.
    -f, --filename=STARTYEAR_ENDYEAR_SCHOLARNAME.pdf
            Output filename of the bargraph (default value is composed by STARTYEAR, ENDYEAR, and abbreviated SCHOLARNAME).
    -s, --year-start=2017
            Init year of the bargraph
    -e, --year-end=2021
            End year of the bargraph
    -u, --gscholar-url={GSCHOLAR_URL}
            Google Scholar URL. If it changes, you can use it this parameter
'''

def usage_error(exit_code=0):
    print(help_text, file=sys.stderr if exit_code else sys.stdout)
    sys.exit(exit_code)

def main(argv):
    logging.basicConfig(level=default_log_level)
    filename = ''
    year_start = -1
    year_end = -1
    gscholar_url = GSCHOLAR_URL
    gscholar_id = GSCHOLAR_ID

    try:
        opts, _args = getopt.getopt(argv, "e:f:hs:u:",["year-end=", "filename=", "help", "year-start=", "gscholar-url="])
    except getopt.GetoptError as e:
        logger.error(e)
        usage_error(2)

    try:
        for opt, arg in opts:
            if opt in ('-h', "--help"):
                usage_error()
            elif opt in ("-s", "--year-start"):
                year_start = int(arg)
            elif opt in ("-e", "--year-end"):
                year_end = int(arg)
            elif opt in ("-f", "--filename"):
                filename = arg
            elif opt in ("-u", "--gscholar-url"):
                gscholar_url = arg
    except ValueError:
        logger.error('Years must be integer values')
        usage_error(2)

    try:
        gscholar_id = _args[0]
    except IndexError:
        logger.error('Required arguments missed')
        usage_error(2)

    soup, cit_years, years = get_citations_years(gscholar_url, gscholar_id)
    researcher_name = get_name(soup)
    researcher_affiliation = get_affiliation(soup)

    if year_start == -1:
        year_start = years[0]
    if year_end == -1:
        year_end= years[-1]

    if filename == '':
        filename = '{}_{}_{}.pdf'.format(year_start, year_end,
                                    ''.join(s[0] for s in researcher_name.split(' ')[:-1]) + researcher_name.split(' ')[-1])

    try:
        idx_start = years.index(year_start)
        idx_end = years.index(year_end) + 1
    except ValueError:
        logger.error('Requested year range [%s, %s] is outside the available range [%s, %s]',
                      year_start, year_end, years[0], years[-1])
        sys.exit(2)
    years = years[idx_start:idx_end]
    cit_years = cit_years[idx_start:idx_end]

    cit_summary = get_citation_summary(soup)
    generate_citation_bargraph(filename, years=years, cit_years=cit_years, name=researcher_name, university=researcher_affiliation, summary=cit_summary, gscholar_id=gscholar_id)


# This data was created by using the curl method explained above
# https://www.scrapehero.com/how-to-fake-and-rotate-user-agents-using-python-3/
headers_list = [
    # Firefox 77 Mac
     {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    # Firefox 77 Windows
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    # Chrome 83 Mac
    {    
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
    },
    # Chrome 83 Windows 
    {
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9"
    }
]

def get_citations_years(gscholar_url=GSCHOLAR_URL, gscholar_id=GSCHOLAR_ID):
    # build URL appropriately
    _headers = random.choice(headers_list)
    try:
        _req = requests.get("{}{}".format(gscholar_url, gscholar_id), headers=_headers, timeout=30)
    except requests.RequestException as e:
        logger.error('Unable to reach Google Scholar: %s', e)
        sys.exit(1)

    if _req.status_code != 200:
        logger.error('Google Scholar returned HTTP %d (profile not found, or requests blocked -- try again later)', _req.status_code)
        sys.exit(1)

    soup = BeautifulSoup(_req.text, features="lxml")
    _hist = soup.find(attrs={'class': 'gsc_md_hist_b'})
    if _hist is None:
        logger.error('Citation histogram not found in the profile page (wrong Scholar ID, empty profile, or CAPTCHA page returned)')
        sys.exit(1)

    _years = [int(_span.text) for _span in _hist.find_all('span', attrs={'class': 'gsc_g_t'})]

    # Years without citations have no bar, so pair each bar with its year
    # through the bar z-index (bars are stacked right-to-left) and fill
    # citation-less years with 0
    _cit_year = [0] * len(_years)
    for _bar in _hist.find_all('a', attrs={'class': 'gsc_g_a'}):
        _z_match = re.search(r'z-index:(\d+)', _bar.get('style', ''))
        if _z_match is None:
            continue
        _cit_year[len(_years) - int(_z_match.group(1))] = int(_bar.text)

    return soup, _cit_year, _years

def get_citation_summary(soup: BeautifulSoup) -> list:
    return [int(_itm.text) for _itm in soup.find_all(attrs={'class': 'gsc_rsb_std'})]

def get_name(soup: BeautifulSoup) -> str:
    _div = soup.find(attrs={'id': 'gsc_prf_in'})
    if _div is None:
        logger.error('Researcher name not found in the profile page')
        sys.exit(1)
    return _div.text

def get_affiliation(soup: BeautifulSoup) -> str:
    _div = soup.find(attrs={'class': 'gsc_prf_il'})
    if _div is None:
        return ''
    return _div.a.text if _div.a is not None else _div.text

def generate_citation_bargraph(filename, years: list, cit_years: list, name: str, university: str, summary: list, gscholar_id: str):
    x = np.arange(len(years))  # the label locations
    width = 0.5  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x, cit_years, width, label='Citations')

    _mean_str = ''
    if len(cit_years) >= 6:
        _mean_last5yrs = statistics.mean(cit_years[-6:-1])
        _mean_str = ' (average of last 5 years, {}/{}: {:.2f})'.format(years[-6],years[-2], _mean_last5yrs)

    summary_str = ''
    if len(summary) >= 5:
        summary_str = '[all] Citations: {}; h-index: {}; i10-index: {}'.format(summary[0], summary[2], summary[4])

    ax.set_ylabel('Citations')
    ax.set_xlabel('Years\n' +
                        '{\\small (data source: {\\tt ' + GSCHOLAR_URL + gscholar_id + '}; fetched on ' +  datetime.now().strftime("%d %b, %Y") + ')}')
    ax.set_title('{\\bf Citations per year' + _mean_str + 
                        '}\nScholar: {\\em ' + name + '} ' + '(' + university +
                        ')\n' + summary_str
                 )
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=90)

    autolabel(ax, rects1)
    fig.tight_layout()
    #plt.show()
    plt.savefig(os.path.join(os.getcwd(), filename), bbox_inches='tight')
    plt.clf()

def autolabel(ax, rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', size=9)

if __name__ == "__main__":
    main(sys.argv[1:])

