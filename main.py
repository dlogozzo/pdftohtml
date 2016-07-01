#Code to take a PDF document and scrape information
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from bs4 import BeautifulSoup
from cStringIO import StringIO
from pandas import Series, DataFrame
import pandas as pd
import time
import re


# file paths
path = "insert path here"

def convert_pdf_to_html(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = HTMLConverter(rsrcmgr, retstr, codec = codec, laparams = laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages = maxpages, password = password, caching = caching, check_extractable = True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str

#conversion to html
text = convert_pdf_to_html(path)

soup = BeautifulSoup(text2, 'lxml')  #remove HTML tags
document_text = soup.get_text()     #cleaned up text

#class to preprocess all files
class Doc(object):
    def __init__(self, html, f="document"):
            self.html = self.BeautifulSoup(text, 'lxml')

    def extract_text(self, text):
        document_text = soup.get_text()

print "Currency Code: " 
print(re.findall(r"""
    \((\w{3})\)
    """, text2,re.X))


print(re.findall(r"""
	((?:[\S,]+\s+){0,3})on,?\s+((?:[\S,]+\s*){0,3})
	""",text, re.X))


rebal_per = re.findall(r'\b(quarterly|annually|semi-annually)\b', text3)
if rebal_per:
    print "Rebalance Periodicity: " + str(rebal_per).title()
else:
    print "Not Found"

# to download files automatically from a link
import urllib2

def main():
    download_file("http://www.cboe.com/micro/spx/pdf/spx_qrg2.pdf")

def download_file(download_url):
    response = urllib2.urlopen(download_url)
    file = open("__main__", 'wb')
    file.write(response.read())
    file.close()
    print("Completed")

if __name__ == "__main__":
    main()
