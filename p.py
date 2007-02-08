import xml.sax
import xml.sax.handler

class XMLDataHandler(xml.sax.handler.ContentHandler):
	def __init__(self):
		#global
		self.__domains = []
		self.__words = []
		self.__inotsn = False
		self.__indomains = False
		self.__indomain = False

		#domains
		self.__inid = False
		self.__inratings = False
		self.__inmilitaristic = False
		self.__incultural = False
		self.__ineconomic = False
		self.__intechnological = False
		self.__inname = False
		self.__inurl = False
		self.__inlongitude = False
		self.__inlatitude = False
		self.__inloc_name = False
		self.__inpages_scanned = False

		#words
		self.__inwords = False
		self.__inword = False
		self.__inpages_w_word = False
		self.__indomain_id = False
		self.__inwordtext = False
		self.__inclip = False
		self.__intext = False
		self.__inpage = False
		self.__inword_id = False
	def startElement(self,name,attributes):
		#global
		if name == "otsn":
			self.__inotsn = True
		if name == "domains":
			if self.__inword:
				self.__tempdomains = []
			self.__indomains = True
		if name == "domain":
			self.__domain = {}
			self.__indomain = True

		#domains
		if name == "id":
			self.__inid = True
		if name == "ratings":
			self.__domain["ratings"] = {}
			self.__inratings = True
		if name == "militaristic":
			self.__inmilitaristic = True
		if name == "cultural":
			self.__incultural = True
		if name == "economic":
			self.__ineconomic = True
		if name == "technological":
			self.__intechnological = True
		if name == "name":
			self.__inname = True
		if name == "url":
			self.__inurl = True
		if name == "longitude":
			self.__inlongitude = True
		if name == "latitude":
			self.__inlatitude = True
		if name == "loc_name":
			self.__inloc_name = True
		if name == "pages_scanned":
			self.__inpages_scanned = True
	
		#words
		if name == "words":
			self.__inwords = True
		if name == "word":
			self.__word = {}
			self.__inword = True
		if name == "pages_w_word":
			self.__inpages_w_word = True
		if name == "domain_id":
			self.__indomain_id = True
		if name == "wordtext":
			self.__inwordtext = True
		if name == "clip":
			self.__clip = {}
			self.__inclip = True
		if name == "text":
			self.__intext = True
		if name == "page":
			self.__inpage = True
		if name == "word_id":
			self.__inword_id = True

	def characters(self,data):
		if self.__inotsn:
			if self.__indomains:
				if self.__indomain:
					if self.__inratings:
						if self.__inmilitaristic:
							self.__domain["ratings"]["militaristic"] = str(data)
						if self.__incultural:
							self.__domain["ratings"]["cultural"] = str(data)
						if self.__ineconomic:
							self.__domain["ratings"]["economic"] = str(data)
						if self.__intechnological:
							self.__domain["ratings"]["technological"] = str(data)
					if self.__inname:
						self.__domain["name"] = str(data)
					if self.__inurl:
						self.__domain["url"] = str(data)
					if self.__inlongitude:
						self.__domain["longitude"] = str(data)
					if self.__inlatitude:
						self.__domain["latitude"] = str(data)
					if self.__inloc_name:
						self.__domain["loc_name"] = str(data)
					if self.__inpages_scanned:
						self.__domain["pages_scanned"] = str(data)
					if self.__inid:
						self.__domain["id"] = str(data)
			if self.__inwords:
				if self.__inword:
					if self.__indomains:
						if self.__indomain:
							if self.__inpages_w_word:
								self.__domain["pages_w_word"] = str(data)
							if self.__indomain_id:
								self.__domain["domain_id"] =  str(data)
					if self.__inwordtext:
						self.__word["wordtext"] = str(data)
					if self.__inclip:
						if self.__intext:
							self.__clip["text"] = str(data)
						if self.__inpage:
							if not str(data) == "\n":
								self.__clip["page"] = str(data)
					if self.__inword_id:
						self.__word["word_id"] = str(data)
	def endElement(self,name):
		#global
		if name == "otsn":
			self.__inotsn = False
		if name == "domains":
			if self.__inword:
				self.__word["domains"] = self.__tempdomains
			self.__indomains = False
		if name == "domain":
			if not self.__inword:
				self.__domains.append(self.__domain)
			if self.__inword:
				self.__tempdomains.append(self.__domain)
			self.__indomain = False

		#domains
		if name == "id":
			self.__inid = False
		if name == "ratings":
			self.__inratings = False
		if name == "militaristic":
			self.__inmilitaristic = False
		if name == "cultural":
			self.__incultural = False
		if name == "economic":
			self.__ineconomic = False
		if name == "technological":
			self.__intechnological = False
		if name == "name":
			self.__inname = False
		if name == "url":
			self.__inurl = False
		if name == "longitude":
			self.__inlongitude = False
		if name == "latitude":
			self.__inlatitude = False
		if name == "loc_name":
			self.__inloc_name = False
		if name == "pages_scanned":
			self.__inpages_scanned = False

		#words
		if name == "words":
			self.__inwords = False
		if name == "word":
			self.__words.append(self.__word)
			self.__inword = False
		if name == "pages_w_word":
			self.__inpages_w_word = False
		if name == "domain_id":
			self.__indomain_id = False
		if name == "wordtext":
			self.__inwordtext = False
		if name == "clip":
			self.__word["clip"] = self.__clip
			self.__inclip = False
		if name == "text":
			self.__intext = False
		if name == "page":
			self.__inpage = False
		if name == "word_id":
			self.__inword_id = False
	def getDomains(self): return self.__domains
	def getWords(self): return self.__words
