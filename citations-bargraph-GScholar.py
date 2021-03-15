#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''Gets the citation bargraph of a Google Scholar profile 
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
import configparser
import getopt
import sys
from datetime import datetime


from matplotlib import rc
rc('font',**{'family':'serif','serif':['Times']})
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

help= f'''usage: {script_name} [-h] [-f FILENAME] [-s start_year] [-e end_year] [-u GSCHOLAR_URL] GSCHOLAR_ID
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
    print(help, file=sys.stderr)
    sys.exit(exit_code)

def main(argv):
    logging.basicConfig(level=default_log_level)
    filename = ''
    year_start = -1
    year_end = -1
    gscholar_url = GSCHOLAR_URL
    gscholar_id = GSCHOLAR_ID

    try:
        opts, _args = getopt.getopt(argv, "e:f:hs:u:",["year-end=", "filename=", "help=", "year-start=", "gscholar-url="])
    except getopt.GetoptError as e:
        logger.exception(e)
        usage_error(2)

    for opt, arg in opts:
        if opt in ('-h', "--help"):
            usage_error()
        elif opt in ("-s", "--year-start"):
            year_start = arg
        elif opt in ("-e", "--year-end"):
            year_end = arg
        elif opt in ("-f", "--filename"):
            filename = arg
        elif opt in ("-u", "--gscholar-url="):
            gscholar_url = arg

    try:
        gscholar_id = _args[0]
    except:
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

    idx_start = years.index(year_start)
    idx_end = years.index(year_end) + 1
    years = years[idx_start:idx_end]

    cit_summary = get_citation_summary(soup)
    generate_citation_bargraph(filename, years=years, cit_years=cit_years, name=researcher_name, university=researcher_affiliation, summary=cit_summary, gscholar_id=gscholar_id)

def get_citations_years(gscholar_url=GSCHOLAR_URL, gscholar_id=GSCHOLAR_ID):
    # build URL appropriately
    _req = requests.get("{}{}".format(gscholar_url, gscholar_id))
    soup = BeautifulSoup(_req.text, features="lxml") # make request
    _div =  str(soup.find(attrs={'class': 'gsc_md_hist_b'}))

    _year_regex = 'px">\d+</span>'
    _citation_year_regex = 'class="gsc_g_al">\d+<'

    _cit_year = get_values_from(_citation_year_regex, _div)
    _years = get_values_from(_year_regex, _div)

    return soup, _cit_year, _years

def get_citation_summary(soup: BeautifulSoup) -> str:
    _itms = soup.findAll(attrs={'class': 'gsc_rsb_std'})
    _indexes = []
    for _itm in _itms:
        _soup = BeautifulSoup(str(_itm), features="lxml")
        _indexes.append(int(_soup.td.text))
    
    return _indexes


def get_name(soup: BeautifulSoup) -> str:
    _div = str(soup.find(attrs={'id': 'gsc_prf_in'}))
    _soup = BeautifulSoup(_div, features="lxml")
    return _soup.div.text

def get_affiliation(soup: BeautifulSoup) -> str:
    _div = str(soup.find(attrs={'class': 'gsc_prf_il'}))
    _soup = BeautifulSoup(_div, features="lxml")
    return _soup.a.text

def get_values_from(_regex_str, html=''):
    _regex = re.compile(_regex_str)
    _list = []
    for _itm in re.findall(_regex, html):
        [_val] = re.findall("\d+", _itm) # get the single element from list
        _list.append(int(_val))
    return _list

def generate_citation_bargraph(filename, years: list, cit_years: list, name: str, university: str, summary: str, gscholar_id: str):
    x = np.arange(len(years))  # the label locations
    width = 0.5  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x, cit_years, width, label='Citations')

    _mean_str = ''
    if len(cit_years) >= 6:
        _mean_last5yrs = statistics.mean(cit_years[-6:-1])
        _mean_str = ' (average of last 5 years, {}/{}: {:.2f})'.format(years[-6],years[-2], _mean_last5yrs)

    summary_str = '[all] Citations: {}; h-index: {}; i10-index: {}'.format(summary[0], summary[2], summary[4])

    ax.set_ylabel('Citations')
    ax.set_xlabel('Years\n' +
                        '{\\small (data source: {\\tt ' + GSCHOLAR_URL + gscholar_id + '}; fetched on ' +  datetime.now().strftime("%d %b, %Y") + ')}')
    ax.set_title('{\\bf Citations per year' + _mean_str + 
                        '}\nScholar: {\\em ' + name + '} ' + '(' + university +
                        ')\n' + summary_str
                 )
    ax.set_xticks(x)
    ax.set_xticklabels(years)

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

