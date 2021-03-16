# citations-bargraph-GScholar 

`citations-bargraph-GScholar` is a Python3 script to scrap a Google Scholar web profile, get citations per year, and generate a bargraph (similar to the one you can get in a Google Scholar profile when clicking on the image at the right-side panel). It only needs the Google Scholar ID of the profile that you want to retrieve!

This script relies on `BeautifulSoup` to scrap the HMTL and `matplotlib` to generate the bargraph. In addition, the bargraph also shows other statistical data, such as the citation average of last 5 years, the total number of citations, h-index, and i10-index. It also shows the URL scrapped and the date when data was fetched on.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Requirements

- Python 3.5 (tested on Python 3.8.4rc1 on top of Debian GNU/Linux bullseye/sid 8.11)
- BeautifulSoup

## Usage

```
usage: citations-bargraph-GScholar.py [-h] [-f FILENAME] [-s start_year] [-e end_year] [-u GSCHOLAR_URL] GSCHOLAR_ID
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
    -u, --gscholar-url=https://scholar.google.es/citations?user=
            Google Scholar URL. If it changes, you can use it this parameter
```
## Usage example

```
$ python3 citations-bargraph-GScholar.py HlQC1OcAAAAJ
```

It will generate a PDF file, containing the bargraph with citations per year of the Google Scholar profile indicated as parameter. For instance, the previous command will generate a PDF as this one:

![example of bargraph](/images/2010_2021_RJRodriguez.pdf "Example of bargraph generated with the tool")


## License

Licensed under the [GNU GPLv3](LICENSE) license.
