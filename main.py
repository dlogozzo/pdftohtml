#Code to take a PDF Methodology document and scrape meta data information

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
path = "F:\Desktop/msci-eafe-index-usd-net.pdf"

month_regex = r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\b"

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

#CLEANUP SECTION

def clean_val(string):
	"""
	Args:
		string(str):
	Returns:
    	Tuple[str, int]:
	"""
	num_is_neg = False 
	if string[0] == "(" and string[-1] == ")":
		num_is_neg = True
		string = string[1:-1]
	if string[0] == r"$":
		string = string[1:].strip()
		if string[0] == "(" and string[-1] == ")":
			num_is_neg = True
			string = string[1:-1]
	if string == '-0-':
		string = '0'
	if string[0] == '(':
		num_is_neg = True
		string = string[1:]
	if num_is_neg:
		string = "-" + string
	elif re.match(r"^(?:-|\s+)$", string):
		string = '0'
	val_int = convert_str_to_int(string)
	return string, val_int


def replace_nonalphanum(string):
	"""
	Cleans unicode punctuation characters, replaces
	with ascii equivalents.
	Args:
		string str
	Returns:
		string str:
	"""
	string = string.replace(u'\u2013', '-')
	string = string.replace(u'\u2014', '-')
	return string.replace(u'\u2019', "'")

def convert_str_to_int(string):
	"""
	Args:
		string (str):
	Returns:
		int or str if fails
	"""
	if re.match(r"\-?\d[0-9\,\.\.]*", string):
		try:
			string = int(''.join([char for char in string if char != "," and
                                  char != "."]))
		except:
			logging.warn("Value Cleaning Error")
	return string


#CLASS Object

class Doc(object):
	def __init__(self, html, f="document"):
		try:
			self.html = self.clean_ascii(html)
		except:
			self.html = unicode(re.sub(r'&#160;', ' ', html))
		self.found_tables = []
		self.document = f   ## return to this later
		self.num_tables = 0
		self.max_year = 0
		self.all_tables_found = False

	def remove_formatting_tags(self, text):
		text = re.sub(ur'<\![^>]+>', '', text)
		text = re.sub(ur'<(?:br|BR)\/?>', ' ', text)
		text = re.sub(ur'style=".*?"', '', text)
		text = re.sub(ur'<sup[^>]*>[^<]{0,5}<\/sup>', '', text)
		text = re.sub(ur'(?ims)<(?:p|div|font|b|i).*?>', ' ', text)  #remove superscripts
		return re.sub(ur'(?ims)<\/(?:p|div|font|b|i)>', ' ', text)

	def clean_beforeafter_html(self, text):
		text = re.sub(r'^.*?<html>', '<html>', text)
		text = re.sub(r'^.*?<HTML>', '<HTML>', text)
		text = re.sub(r'</html>.*$', '</html>', text)
		return re.sub(r'</html>.*$', '</html>', text)

	def replace_html_junk(self, text):
		logging.info("Replace junk in HTML")
		text = re.sub(r'(?:\\n|\n)', ' ', text)
		text = re.sub(r'—', r'-', text)
		text = re.sub(r'&lt;', r'<', text)
		text = re.sub(r'&gt;', r'>', text)
		text = self.clean_beforeafter_html(self.clean_ascii(text))
		text = re.sub(r'&quot;', r'"', text)
		text = re.sub(r'&amp;', r'&', text)
		text = self.remove_formatting_tags(text)

	def get_html_tag_re(self, regex, text, tag = "tag"):
		tag_re = re.compile(regex)
		tags = tag_re.findall(text)
		logging.info('Regex for %s: %s', tag, len(tags))
		souped_tags = []
		for tag in tags:
			try:
				souped_tags.append(BeautifulSoup(tag))
			except:
				logging.warn("Unicode Error Converting Table to Soup")
		return souped_tags

	def clean_ascii(self, text):
		text = text.replace('&nbsp;', ' ')
		text = re.sub(r'&nbsp;', " ", text)
		text = re.sub(hyphen, '-', text)
		text = re.sub(r'[\x92]', "'", text)
		text = text.replace(u'\u2013'.encode('utf8'), '-')
		text = text.replace(u'\u2014'.encode('utf8'), '-')
		text = text.replace(u'\u2019'.encode('utf8'), "'")
		text = text.replace(r'’', "'")
		text = re.sub(r'&#160;', ' ', text)
		return text

	def extract_text(self, start_regex, end_regex):
		found_text = re.findall(r">([^<]+\w[^<]+)<", self.html)
		selection_text = ""
		for index, text in enumerate(found_text):
			if re.search("^\s*" + start_regex, text):
				found_text = found_text[index + 1:]
				for text in found_text:
					if re.search("^\s*" + end_regex, text):
						break
					selection_text += " " + text
				return selection_text
		text_regex = r"(?ms)" + start_regex + r"([\W\w]*?)" + end_regex
		m = re.search(text_regex, self.html)
		if m:
			return m.group(1).strip().strip("-").strip()
		# if no html formatting search through full text


	def get_provider(self):
		#grabs index provider




	def get_currency(self):
		#grabs index currency
		return self.extract_text(r"\((\w{3})\)")


	def get_index_type(self):
		#grabs index type


	def get_isup_name(self):
		#grabs index long name


	def get_rebalance(self):
		#grabs rebalance dates


	def group_type(self):
		#grabs group type


	def get_base_date(self):
		#grabs base/launch date
		date_text = self.extract_text(r"((?:[\S,]+\s+){0,3})\bon,?\s+((?:[\S,]+\s*){0,3})")
		if date_text:
			m = re.search(r"(" + month_regex + r".*$)", date_text)
			if m:
				m = re.search(r"^(.*?\b\d{4}\b)", m.group(1).strip())
				if m:
					return m.group(1)
