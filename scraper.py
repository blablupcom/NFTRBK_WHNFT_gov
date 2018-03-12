# -*- coding: utf-8 -*-

#### IMPORTS 1.0

import os
import re
import scraperwiki
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup

#### FUNCTIONS 1.0

def validateFilename(filename):
    filenameregex = '^[a-zA-Z0-9]+_[a-zA-Z0-9]+_[a-zA-Z0-9]+_[0-9][0-9][0-9][0-9]_[0-9QY][0-9]$'
    dateregex = '[0-9][0-9][0-9][0-9]_[0-9QY][0-9]'
    validName = (re.search(filenameregex, filename) != None)
    found = re.search(dateregex, filename)
    if not found:
        return False
    date = found.group(0)
    now = datetime.now()
    year, month = date[:4], date[5:7]
    validYear = (2000 <= int(year) <= now.year)
    if 'Q' in date:
        validMonth = (month in ['Q0', 'Q1', 'Q2', 'Q3', 'Q4'])
    elif 'Y' in date:
        validMonth = (month in ['Y1'])
    else:
        try:
            validMonth = datetime.strptime(date, "%Y_%m") < now
        except:
            return False
    if all([validName, validYear, validMonth]):
        return True


def validateURL(url):
    try:
        r = urllib2.urlopen(url)
        count = 1
        while r.getcode() == 500 and count < 4:
            print ("Attempt {0} - Status code: {1}. Retrying.".format(count, r.status_code))
            count += 1
            r = urllib2.urlopen(url)
        sourceFilename = r.headers.get('Content-Disposition')

        if sourceFilename:
            ext = os.path.splitext(sourceFilename)[1].replace('"', '').replace(';', '').replace(' ', '')
        else:
            ext = os.path.splitext(url)[1]
        validURL = r.getcode() == 200
        validFiletype = ext.lower() in ['.csv', '.xls', '.xlsx', '.pdf']
        return validURL, validFiletype
    except:
        print ("Error validating URL.")
        return False, False


def validate(filename, file_url):
    validFilename = validateFilename(filename)
    validURL, validFiletype = validateURL(file_url)
    if not validFilename:
        print filename, "*Error: Invalid filename*"
        print file_url
        return False
    if not validURL:
        print filename, "*Error: Invalid URL*"
        print file_url
        return False
    if not validFiletype:
        print filename, "*Error: Invalid filetype*"
        print file_url
        return False
    return True


def convert_mth_strings ( mth_string ):
    month_numbers = {'JAN': '01', 'FEB': '02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 'JUL':'07', 'AUG':'08', 'SEP':'09','OCT':'10','NOV':'11','DEC':'12' }
    for k, v in month_numbers.items():
        mth_string = mth_string.replace(k, v)
    return mth_string

#### VARIABLES 1.0

entity_id = "NFTRBK_WHNFT_gov"
url = "https://www.walsallhealthcare.nhs.uk/Default.aspx?pageid=2638&mid=73&ItemID=30"
errors = 0
data = []

#### READ HTML 1.0
import ssl
req = urllib2.Request(url)
gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
html = urllib2.urlopen(req, context=gcontext)
soup = BeautifulSoup(html, 'lxml')


#### SCRAPE DATA

blocks_links = soup.find('ul', 'linkitem').find_all('a')
links = set()
for block_links in blocks_links:
    links.add(block_links['href'])
for link in links:
    html = urllib2.urlopen(link)
    soup = BeautifulSoup(html, 'lxml')
    page_title = soup.find('h1', ' moduletitle').text.strip()
    if 'Trust Expenditure' in page_title:
        blocks = soup.find('div', id='ctl00_mainContent_ctl00_divContent').find_all('a')
        for block in blocks:
            l = block['href']
            if '.csv' in l:
                url = 'https://www.walsallhealthcare.nhs.uk'+l
                title = block.text
                csvMth = title.split('for ')[-1].split(' -')[0][:3]
                csvYr = title.split('for ')[-1].split(' -')[0].replace(u' - csv format', '')[-4:]
                csvMth = convert_mth_strings(csvMth.upper())
                data.append([csvYr, csvMth, url])
    if '2014 Expenditure' in page_title:
        blocks = soup.find('div', id='ctl00_mainContent_ctl00_divContent').find_all('a')
        for block in blocks:
            l = block['href']
            if '.csv' in l or '.xls' in l or 'xlsx' in l:
                url = 'https://www.walsallhealthcare.nhs.uk'+l
                title = block.previousSibling.previousSibling.previousSibling
                if '20' in title:
                    url = url
                    title = title.strip()
                    csvMth = title[:3]
                    csvYr = title[-4:]
                    csvMth = convert_mth_strings(csvMth.upper())
                    data.append([csvYr, csvMth, url])
    if '2015 Expenditure' in page_title:
        blocks = soup.find('div', id='ctl00_mainContent_ctl00_divContent').find_all('a')
        for block in blocks:
            l = block['href']
            if '.csv' in l:
                url = 'https://www.walsallhealthcare.nhs.uk'+l
                title = block.text
                csvMth = title.split('for ')[-1].split(' -')[0][:3]
                csvYr = title.split('for ')[-1].split(' -')[0].replace(u' - csv format', '')[-4:]
                csvMth = convert_mth_strings(csvMth.upper())
                data.append([csvYr, csvMth, url])
    if '2012 Expenditure' in page_title:
        blocks = soup.find('div', id='ctl00_mainContent_ctl00_divContent').find_all('a')
        for block in blocks:
            l = block['href']
            if '.csv' in l or '.xls' in l or 'xlsx' in l:
                if 'http://' not in l:
                    url = 'https://www.walsallhealthcare.nhs.uk'+l
                title = block.find_previous('p').find_previous('p').text.strip()
                csvMth = title[:3]
                csvYr = title[-4:]
                csvMth = convert_mth_strings(csvMth.upper())
                data.append([csvYr, csvMth, url])

    if '2011 Expenditure' in page_title:
        blocks = soup.find('div', id='ctl00_mainContent_ctl00_divContent').find_all('a')
        for block in blocks:
            url = block['href']
            if '.csv' in url or '.xls' in url or '.xlsx' in url:
                title = block.find_previous('p').find_previous('p').text.strip()
                csvMth = title[:3]
                csvYr = title.split(' ')[1]
                if 'Ple' in csvMth:
                    title = block.previousSibling.previousSibling.previousSibling.strip()
                    csvMth = title[:3]
                    csvYr = title.split(' ')[1]
                csvMth = convert_mth_strings(csvMth.upper())
                data.append([csvYr, csvMth, url])

    if '2010 Expenditure' in page_title:
        blocks = soup.find('div', id='ctl00_mainContent_ctl00_divContent').find_all('span', style='color: #333333; line-height: 16px; background-color: #ffffff;')
        for block in blocks:
            if '2010' in block.text and 'csv format' in block.text:
                 title = block.text.strip()
                 if 'for' in title:
                     csvYr = title.split(' for ')[-1].strip().split(' ')[1]
                     csvMth = title.split(' for ')[-1].strip().split(' ')[0][:3]
                     url = block.find_previous('a')['href']
                 if 'between' in title:
                     csvMth = 'Q0'
                     csvYr = '2010'
                     url = block.find_previous('a')['href']
                 csvMth = convert_mth_strings(csvMth.upper())
                 data.append([csvYr, csvMth, url])


#### STORE DATA 1.0

for row in data:
    csvYr, csvMth, url = row
    filename = entity_id + "_" + csvYr + "_" + csvMth
    todays_date = str(datetime.now())
    file_url = url.strip()

    valid = validate(filename, file_url)

    if valid == True:
        scraperwiki.sqlite.save(unique_keys=['l'], data={"l": file_url, "f": filename, "d": todays_date })
        print filename
    else:
        errors += 1

if errors > 0:
    raise Exception("%d errors occurred during scrape." % errors)


#### EOF

