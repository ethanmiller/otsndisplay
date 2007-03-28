#!/usr/bin/env python
from p import *
import pygame, sys, os, time, math, random, datetime
from pygame.locals import *

def rgb_sort(l):
	indexed = {}
	for i, v in enumerate(l):
		indexed[i] =v
	hsbs = [(rgb_hsb(v), k) for k, v in indexed.iteritems()]
	hsbs.sort()
	return [indexed[x[1]] for x in hsbs]
def rgb_hsb(l):
	rgb = (l[0]/255.0, l[1]/255.0, l[2]/255.0)
	rgbmax = max(rgb)
	rgbmin = min(rgb)
	delt = rgbmax - rgbmin
	B = rgbmax
	if delt == 0:
		H = 0
		S = 0
	else:
		S = delt/rgbmax
		deltr = (((rgbmax - rgb[0]) / 6) + (delt/2)) / delt
		deltg = (((rgbmax - rgb[1]) / 6) + (delt/2)) / delt
		deltb = (((rgbmax - rgb[2]) / 6) + (delt/2)) / delt
	
		if rgb[0] == rgbmax: H = deltb - deltg
		if rgb[1] == rgbmax: H = (1/3.0) + deltr - deltb
		if rgb[2] == rgbmax: H = (2/3.0) + deltg - deltr

		if H < 0: H += 1
		if H > 1: H -= 1
	
	return (H,S,B)

class World:
	def __init__ (self,map_offset=1.1):
		self.map_offset = map_offset

		self.parser = xml.sax.make_parser()
		self.handler = XMLDataHandler()
		self.parser.setContentHandler(self.handler)

		self.words = {}
		self.domains = {}
		self.links = {}
		self.offset = 0
		self.time = None
		self.last_update = None
	
		pygame.init()
		self.font_sm = pygame.font.Font("resources/arialbd.ttf",10) 
		self.font_lg = pygame.font.Font("resources/arialbd.ttf",30)
		pygame.display.set_caption('SocialVis 0.2') 
		self.screen = pygame.display.set_mode((1024,768),FULLSCREEN)
		#self.screen = pygame.display.set_mode((1024,768))
		pygame.mouse.set_visible(False)
		 
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill((0,0,0))
	
		self.map_background = pygame.Surface((self.screen.get_width(),(self.screen.get_width()*.3625)*self.map_offset))
		self.map_background = self.map_background.convert()
		self.map_background.fill((0,0,0))
			
		self.map = pygame.Surface((self.screen.get_width(),(self.screen.get_width()*.3625)*self.map_offset))
		self.map = self.map.convert()
		self.map.set_colorkey((255,0,0))
		self.map.fill((255,0,0))
	
		self.map_tags = pygame.Surface((self.screen.get_width(),(self.screen.get_width()*.3625)*self.map_offset))
		self.map_tags = self.map.convert()
		self.map_tags.fill((255,0,0))
			
		self.info_top = pygame.Surface((self.screen.get_width(),(self.screen.get_height()-self.map.get_height())/2.0))
		self.info_top = self.info_top.convert()
		self.info_top.fill((0,0,0))
		
		self.info_bottom = pygame.Surface((self.screen.get_width(),(self.screen.get_height()-self.map.get_height())/2.0))
		self.info_bottom = self.info_bottom.convert()
		self.info_bottom.fill((0,0,0))
	
		self.image_inactive = pygame.Surface((10,10))
		self.image_inactive.fill((255,0,0))
		self.image_inactive.set_colorkey((255,0,0))
		pygame.draw.circle(self.image_inactive,[100,100,100],(5,5),5,1)
	
		self.update("resources/words_new.xml")
		self.current_word = [x for x in self.getWord() if x.color_index == 0][0]
		self.draw()
	def draw(self):
		while True:
			n = datetime.datetime.now()
			if n.hour >= 20:
				sys.exit(0)
			for event in pygame.event.get():
				if event.type == QUIT:
					sys.exit(0)
				if event.type == KEYDOWN:
					if event.key == K_q:
						sys.exit(0)
					if event.key == K_UP:
						map_offset = self.map_offset + 0.1
						self.__init__(map_offset)
					if event.key == K_DOWN:
						map_offset = self.map_offset - 0.1
						self.__init__(map_offset)
			if not self.updating:
				for domain in self.getDomain():
					self.map_background.blit(self.image_inactive,(domain.getRelPos(self.map_background)))
				self.current_word.render()	
				#blit down
				self.screen.blit(self.map_background,(0,(self.screen.get_height() - self.map.get_height())/2.0))
				self.screen.blit(self.map,(0,(self.screen.get_height() - self.map.get_height())/2.0))
				self.screen.blit(self.map_tags,(0,(self.screen.get_height() - self.map.get_height())/2.0))
				self.screen.blit(self.info_top,(0,0))
				self.screen.blit(self.info_bottom,(0,((self.screen.get_height() - self.map.get_height())/2.0) + self.map.get_height()))
				
				pygame.display.flip()
				self.map_tags.fill((255,0,0))
				self.info_bottom.fill((0,0,0))
			# Cleanup for the next word. Wait before moving on.
			if len([x for x in self.getLink(self.current_word) if x.line.isDone() and x.tag.isSettled()]) == len(self.getLink(self.current_word)):
				if time.time() - self.last_update >= 14400:
					self.update("resources/words_new.xml")
				else:
					if self.time == None:
						self.time = time.time()
					if time.time() - self.time >= 3:
						self.time = None
							
						self.map.fill((255,0,0))
						self.info_top.fill((0,0,0))

						for domain in self.getLink(self.current_word):
							domain.reset()
						
						self.current_word.reset()
						if [x for x in self.getWord() if x.color_index == self.current_word.color_index + 1]:
							self.current_word = [x for x in self.getWord() if x.color_index == self.current_word.color_index + 1][0]
						else:
							self.current_word = [x for x in self.getWord() if x.color_index == 0][0]
	def addWord(self,id,wordtext,clip,rating):
		self.words[id] = Word(self,id,wordtext,clip,rating)
		self.links[self.words[id]] = {}
		return self.words[id]
	def addDomain(self,id,name,url,pgs_scanned,loc,rating):
		self.domains[id] = Domain(self,id,name,url,pgs_scanned,loc,rating)
		return self.domains[id]
	def getWord(self,id=None):
		if id == None:
			return self.words.values()
		else:
			try:
				return self.words[id]
			except:
				return None
	def getDomain(self,id=None):
		if id == None:
			return self.domains.values()
		else:
			try:
				return self.domains[id]
			except:
				return None
	def addLink(self,word,domain,numpages):
		if isinstance(word,Word) and isinstance(domain,Domain):
			self.links[word][domain] = numpages
		return self
	def getLink(self,word=None,domain = None):
		if word == None and domain == None:
			return self.links
		if domain == None:
			if isinstance(word,Word):
				try:
					return self.links[word]
				except:
					return None
		if isinstance(word,Word) and isinstance(domain,Domain):
			try:
				return self.links[word][domain]
			except:
				return None
	def update(self,xmldata):
		self.updating = True
		self.parser.parse(xmldata)
		for domain in self.handler.getDomains():
			self.addDomain(domain["id"],domain["name"],domain["url"],int(domain["pages_scanned"]),{"name" : domain["loc_name"], "lat" : float(domain["latitude"]), "lon" : float(domain["longitude"])},{"militaristic" : float(domain["ratings"]["militaristic"])*.01, "cultural" : float(domain["ratings"]["cultural"])*.01, "economic" : float(domain["ratings"]["economic"])*.01, "technological" : float(domain["ratings"]["technological"])*.01})
		for word in self.handler.getWords():
			avgs = {"militaristic" : 0.0, "cultural" : 0.0, "economic" : 0.0, "technological" : 0.0, "weight" : 0.0}
			for domain in word["domains"]:
				dom = self.getDomain(domain["domain_id"])
				if not dom: continue
				rating = dom.rating

				rating = self.getDomain(domain["domain_id"]).rating
				domain_weight = int(domain["pages_w_word"])/float(self.getDomain(domain["domain_id"]).pgs_scanned)
				avgs["militaristic"] += rating["militaristic"]*domain_weight
				avgs["cultural"] += rating["cultural"]*domain_weight
				avgs["economic"] += rating["economic"]*domain_weight
				avgs["technological"] += rating["technological"]*domain_weight
				avgs["weight"] += domain_weight
			current_word = self.addWord(word["word_id"],word["wordtext"],word["clip"],{"militaristic" : avgs["militaristic"]/avgs["weight"], "cultural" : avgs["cultural"]/avgs["weight"], "economic" : avgs["economic"]/avgs["weight"], "technological" : avgs["technological"]/avgs["weight"]})
			for domain in word["domains"]:
				self.addLink(current_word,self.getDomain(domain["domain_id"]),int(domain["pages_w_word"]))
			most_pgs_scanned = [x.pgs_scanned for x in self.getLink(current_word)]
			most_pgs_scanned.sort()
			most_pgs_scanned.reverse()
			current_word.most_pgs_scanned = most_pgs_scanned[0]
		to_sort = []
		for word in self.getWord():
			to_sort.append([word.rating["technological"],word.rating["militaristic"],word.rating["cultural"]])
		sorted_rgb = rgb_sort(to_sort)
		for word in self.getWord():
			index_found = sorted_rgb.index([word.rating["technological"],word.rating["militaristic"],word.rating["cultural"]])
			if not [word for x in self.getWord() if word.color_index == index_found]:
				word.color_index = index_found
			else:
				word.color_index = index_found + 1
		
		self.last_update = time.time()
		self.updating = False		
	def nuke(self):
		self.words = {}
		self.domains = {}
		self.links = {}
		return self	
class WordTitle:
	def __init__(self,parent,render_surface):
		self.x = 10
		self.y = -2
		self.parent = parent
		self.render_surface = render_surface
		self.rendered = False
		
		self.font = self.parent.parent.font_lg
		self.image = self.font.render(parent.wordtext.upper(),1,(255*parent.rating["technological"],255*parent.rating["militaristic"],255*parent.rating["cultural"]))
		self.background = self.font.render(parent.wordtext.upper(),1,(255,255,255))
	def render(self):
		if not self.rendered:
			self.render_surface.blit(self.background,(self.x-1,self.y+1))
			self.render_surface.blit(self.image,(self.x,self.y))
			self.rendered = True
class WordRating:
	def __init__(self,parent,render_surface):
		self.x = 10
		self.y = 35
		self.parent = parent
		self.render_surface = render_surface
		self.rendered = False		

		self.font = self.parent.parent.font_sm
		self.image = pygame.Surface((195,55))
		self.bar = pygame.Surface((100,10))
		self.bar.fill([0,0,0])

		pygame.draw.rect(self.bar,[255,0,0],self.bar.get_rect(),1)
		self.bar_fill = pygame.Surface((self.parent.rating["technological"]*self.bar.get_width(),self.bar.get_height()))
		self.bar_fill.fill((255,0,0))
		self.text = self.font.render("TECHNOLOGICAL",1,[255,255,255])
		self.image.blit(self.bar,(self.image.get_width()-self.bar.get_width(),0))
		self.image.blit(self.bar_fill,(self.image.get_width()-self.bar.get_width(),0))
		self.image.blit(self.text,(self.image.get_width()-self.bar.get_width()-self.text.get_width()-5,-3))

		pygame.draw.rect(self.bar,[0,255,0],self.bar.get_rect(),1)
		self.bar_fill = pygame.Surface((self.parent.rating["militaristic"]*self.bar.get_width(),self.bar.get_height()))
		self.bar_fill.fill((0,255,0))
		self.text = self.font.render("MILITARISTIC",1,[255,255,255])
		self.image.blit(self.bar,(self.image.get_width()-self.bar.get_width(),self.bar.get_height()+5))
		self.image.blit(self.bar_fill,(self.image.get_width()-self.bar.get_width(),self.bar.get_height()+5))
		self.image.blit(self.text,(self.image.get_width()-self.bar.get_width()-self.text.get_width()-5,self.bar.get_height()+5-3))

		pygame.draw.rect(self.bar,[0,0,255],self.bar.get_rect(),1)
		self.bar_fill = pygame.Surface((self.parent.rating["cultural"]*self.bar.get_width(),self.bar.get_height()))
		self.bar_fill.fill((0,0,255))
		self.text = self.font.render("CULTURAL",1,[255,255,255])
		self.image.blit(self.bar,(self.image.get_width()-self.bar.get_width(),(self.bar.get_height()*2)+10))
		self.image.blit(self.bar_fill,(self.image.get_width()-self.bar.get_width(),(self.bar.get_height()*2)+10))
		self.image.blit(self.text,(self.image.get_width()-self.bar.get_width()-self.text.get_width()-5,(self.bar.get_height()*2)+10-3))

		pygame.draw.rect(self.bar,[255,255,255],self.bar.get_rect(),1)
		self.bar_fill = pygame.Surface((self.parent.rating["economic"]*self.bar.get_width(),self.bar.get_height()))
		self.bar_fill.fill((255,255,255))
		self.text = self.font.render("ECONOMIC",1,[255,255,255])
		self.image.blit(self.bar,(self.image.get_width()-self.bar.get_width(),(self.bar.get_height()*3)+15))
		self.image.blit(self.bar_fill,(self.image.get_width()-self.bar.get_width(),(self.bar.get_height()*3)+15))
		self.image.blit(self.text,(self.image.get_width()-self.bar.get_width()-self.text.get_width()-5,(self.bar.get_height()*3)+15-3))
	def render(self):
		if not self.rendered:
			self.render_surface.blit(self.image,(self.x-3,self.y))
			self.rendered = True
class WordTextClip:
	def __init__(self,parent,render_surface):
		self.parent = parent
		self.render_surface = render_surface
		self.chars_in_line = 50
		self.num_lines = 5
		self.lines = []
		self.url = self.parent.clip["page"]
		self.textclip = self.parent.clip["text"]
		if len(self.textclip) > self.chars_in_line*self.num_lines:
			self.textclip = self.textclip[:(self.chars_in_line*self.num_lines)]
		l = 0
		while l < self.num_lines:
			if len(self.textclip) > 1:
				if len(self.textclip) <= self.chars_in_line-2:
					self.lines.append(self.textclip[:self.chars_in_line])
					self.textclip = self.textclip[self.chars_in_line:]
				else: 
					self.lines.append(self.textclip[:(self.chars_in_line)-2]+"..")	
					self.textclip = self.textclip[self.chars_in_line-2:]
			l+=1
		if len(self.url) >= 35:
			self.url = "-"+self.url[:35]+".."
		else:
			self.url = "-"+self.url[:33]+".."
		self.image = pygame.Surface((265,105))
		
		self.font = self.parent.parent.font_sm

		offset = 0
		for line in self.lines:
			if not line == "":
				self.text = self.font.render(line,0,(255,255,255))
				self.image.blit(self.text,(5,15*offset))
				offset += 1
		self.text = self.font.render(self.url,0,(255,255,255))
		self.image.blit(self.text,(5,(15*offset)+5))
	def render(self):
		self.render_surface.blit(self.image,((self.render_surface.get_width()-self.image.get_width())-5,5))
class WordLineBlock:
	def __init__(self,parent,render_surface):
		self.parent = parent
		self.render_surface = render_surface
		self.rendered = False
	def render(self):
		width = float(self.render_surface.get_width())/float(len(self.parent.parent.getWord()))
		if self.rendered == False:
			if len(self.parent.wordtext) > 15:
				bartext = self.parent.wordtext[:13] + ".."
			else:
				bartext = self.parent.wordtext
			self.image = pygame.Surface((width+(width/2.0),width))
			self.image.fill((255*self.parent.rating["technological"],255*self.parent.rating["militaristic"],255*self.parent.rating["cultural"]))
			self.font = self.parent.parent.font_sm
			self.text = self.font.render(bartext,1,(255*self.parent.rating["technological"],255*self.parent.rating["militaristic"],255*self.parent.rating["cultural"]))
			self.text = pygame.transform.rotate(self.text,-90)
			self.text_active = self.font.render(bartext,1,(255,255,255))
			self.text_active = pygame.transform.rotate(self.text_active,-90)

			self.rendered = True
		self.render_surface.blit(self.image,(width*self.parent.color_index,0))
		if not self.parent.parent.current_word == self.parent:
			self.render_surface.blit(self.text,((width*self.parent.color_index)+(self.text.get_width()*.25),self.image.get_height()+2))
		else:
			self.render_surface.blit(self.text_active,((width*self.parent.color_index)+(self.text.get_width()*.25),self.image.get_height()+2))
class Word:
	def __init__(self,parent,id,wordtext,clip,rating):
		self.parent = parent
		self.id = id
		self.wordtext = wordtext
		self.clip = clip
		self.rating = rating
		self.hsb = rgb_hsb(self.rating.values())
		self.color_index = None

		#self.color_line = WordColorLine(self,self.parent.info_bottom)
		self.line_block = WordLineBlock(self,self.parent.info_bottom)
		self.title = WordTitle(self,self.parent.info_top)
		self.rating_bars = WordRating(self,self.parent.info_top)
		self.text_clip = WordTextClip(self,self.parent.info_top)
	
			
		self.marker_offset_left = 0
		self.marker_offset_right = 0
		self.render_marker_right = True	
	def render(self):
		self.rating_bars.render()
		self.title.render()
		self.text_clip.render()
		#self.color_line.render()
		i = 0
		while i < len(self.parent.getWord()):
			for word in self.parent.getWord():
				if word.color_index == i:
					word.line_block.render()
			i+=1
		for domain in self.parent.getLink(self):
			domain.render()
	def reset(self):
		self.title = WordTitle(self,self.parent.info_top)
		self.rating_bars = WordRating(self,self.parent.info_top)
class DomainDot:
	def __init__(self,parent,render_surface):
		self.parent = parent
		self.render_surface = render_surface
		
		self.rendered = False

		self.image = pygame.Surface((10,10))
		self.image.set_colorkey((255,0,0))
		self.image.fill((255,0,0))
		pygame.draw.circle(self.image,[0,0,0],(5,5),5,0)
		
		self.color = pygame.Surface((10,10))
		self.color.set_colorkey((255,0,0))
		self.color.fill((255,0,0))
		self.color.set_alpha(255*parent.rating["economic"])
		pygame.draw.circle(self.color,[255,255,255],(5,5),5,0)
		
		self.outline = pygame.Surface((10,10))
		self.outline.set_colorkey((0,0,0))
		pygame.draw.circle(self.outline,[255*self.parent.rating["technological"],255*self.parent.rating["militaristic"],255*self.parent.rating["cultural"]],(5,5),5,1)
		
		self.image.blit(self.color,(0,0))
		self.image.blit(self.outline,(0,0))
		self.x = (render_surface.get_width()*((self.parent.loc["lon"]+180.0)/360.0))-self.image.get_width()/2.0
		self.y = (render_surface.get_height()*(((self.parent.loc["lat"]*-1.0)+90)/180))-self.image.get_height()/2.0
		if self.y > (render_surface.get_height()/2):
			self.y += 15
	def render(self):
		if isinstance(self.render_surface,pygame.Surface):
			if not self.rendered:
				self.render_surface.blit(self.image,(self.x,self.y))
				self.rendered = True
class DomainMarker:
	def __init__(self,parent,render_surface):
		self.parent = parent
		self.render_surface = render_surface
		self.rendered = False
		self.x = 0
		self.y = 0
	def isRendered(self):
		return self.rendered
	def render(self):
		if not self.rendered:
			if float(self.parent.parent.map.get_width())/len(self.parent.parent.getLink(self.parent.parent.current_word)) > 10:
				width = 5
			else:
				width = float(self.parent.parent.map.get_width())/len(self.parent.parent.getLink(self.parent.parent.current_word))
			if 85.0/(self.parent.parent.current_word.most_pgs_scanned/self.parent.pgs_scanned) < 1:
				height = 1
			else:
				height = 85.0/(self.parent.parent.current_word.most_pgs_scanned/self.parent.pgs_scanned)
			self.image = pygame.Surface((width,height))
			self.image.fill([255*self.parent.rating["technological"],255*self.parent.rating["militaristic"],255*self.parent.rating["cultural"]])
			pgs_w_word = self.parent.parent.getLink(self.parent.parent.current_word,self.parent)
			#self.bar_fill = pygame.Surface((width,self.image.get_height()/(float(self.parent.pgs_scanned)/pgs_w_word)))
		
			#self.bar_fill.fill([255*self.parent.rating["technological"],255*self.parent.rating["militaristic"],255*self.parent.rating["cultural"]])
			#self.image.blit(self.bar_fill,(0,self.image.get_height()-self.bar_fill.get_height()))

			active_markers = len([x for x in self.parent.parent.getLink(self.parent.parent.current_word) if x.marker.isRendered()])
			mid = (self.render_surface.get_width()/2.0)-(width/2.0)
			if self.parent.parent.current_word.render_marker_right:
				self.x = mid+((active_markers*width)/2.0)
				self.y = self.render_surface.get_height()-self.image.get_height()
				self.render_surface.blit(self.image,(self.x+1,self.y))
			else:
				self.x = mid-(((active_markers+1)*width)/2.0)
				self.y = self.render_surface.get_height()-self.image.get_height()
				self.render_surface.blit(self.image,(self.x+1,self.y))
			self.rendered = True

			if self.parent.parent.current_word.render_marker_right:
				self.parent.parent.current_word.render_marker_right = False
			else:
				self.parent.parent.current_word.render_marker_right = True

class DomainTag:
	def __init__(self,parent,render_surface):
		self.parent = parent
		self.render_surface = render_surface

		self.x = (render_surface.get_width()*((self.parent.loc["lon"]+180.0)/360.0)) + 5
		self.y = (render_surface.get_height()*(((self.parent.loc["lat"]*-1.0)+90)/180.0)) - 9

		
		self.settled = True		

		self.font = self.parent.parent.font_sm
		if len(parent.name) <= 25:
			self.text = self.font.render(parent.name,0,(255,255,255))
		else:
			self.text = self.font.render(parent.name[:23]+"..",0,(255,255,255))
		
		self.image = pygame.Surface((self.text.get_width()+5,self.text.get_height()+1))
		self.image.set_colorkey([255,0,0])
		self.image.fill((255,0,0))

		if self.y > render_surface.get_height()/2.0:
			self.y += self.image.get_height()
		
		if self.x + self.image.get_width() > self.parent.parent.screen.get_width():
			self.x = self.x - self.image.get_width() - 10
		
		self.image.blit(self.text,((self.image.get_width() - self.text.get_width())/2.0,1))
		
	def adjPos(self, xadj, yadj):
		self.settled = False
		self.x += xadj
		self.y += yadj
	def isSettled(self):
		return self.settled
	def force_place(self):
		force = 0.05
		domains = [x for x in self.parent.parent.getLink(self.parent.parent.current_word) if x.line.isDone()]
		if domains:
			tags = [x.tag for x in domains if not x.id == self.parent.id]
			if tags:
				for tag2 in tags:
					if self.y + self.image.get_height() < tag2.y:
						tag2.settled = True
						continue # bottom of label above top of label2
					if self.y > tag2.y + tag2.image.get_height():
						tag2.settled = True
						continue # top of label below bottom of label2
					if self.x + self.image.get_width() < tag2.x:
						tag2.settled = True
						continue # right of label to the left of left side of label2
					if self.x > tag2.x + tag2.image.get_width():
						tag2.settled = True
						continue # left of label to the right of right side of label2
					mid = (self.x + self.image.get_width()/2, self.y + self.image.get_height()/2)
					mid2 = (tag2.x + tag2.image.get_width()/2, tag2.y + tag2.image.get_height()/2)
					xdiff, ydiff = (mid2[0] - mid[0], mid2[1] - mid[1])
					dist = math.sqrt(xdiff*xdiff + ydiff*ydiff)
					pushx = xdiff*(force/2)*0.5
					pushy = ydiff*force*0.5
					if self.x - pushx < 0 or self.x - pushx > self.parent.parent.map_tags.get_width() - self.image.get_width() or self.y - pushy < 0 or self.y -pushy > self.parent.parent.map_tags.get_height() - self.image.get_height(): 
						if self.x -pushx < 0 or self.x -pushx > self.parent.parent.map_tags.get_width():
							self.adjPos(0, -pushy)
						if self.y - pushy < 0 or self.y -pushy > self.parent.parent.map_tags.get_height():
							if not self.x - pushx > self.screen.get_width() - self.image.get_width():
								self.adjPos(-pushx, 0)
					
					if tag2.x -pushx < 0 or tag2.x -pushx > tag2.parent.parent.map_tags.get_width() - self.image.get_width() or tag2.y - pushy < 0 or tag2.y -pushy > tag2.parent.parent.map_tags.get_height() - self.image.get_height(): 
						if tag2.x -pushx < 0 or tag2.x -pushx > tag2.parent.parent.map_tags.get_width():
							tag2.adjPos(0, -pushy)
						if tag2.y - pushy < 0 or tag2.y -pushy > tag2.parent.parent.map_tags.get_height():
							tag2.adjPos(-pushx, 0)
					else:
						self.adjPos(-pushx, -pushy)
						tag2.adjPos(pushx, pushy)
	def render(self):
		if isinstance(self.render_surface,pygame.Surface):
			self.force_place()
			self.render_surface.blit(self.image,(self.x,self.y))
class DomainLine:
	def __init__(self,parent,render_surface):
		self.parent = parent	
		self.render_surface = render_surface
		
		self.image = None
		self.line_pts = None
		self.active_pts = None
	def isDef(self):
		if not self.image == None:
			return True
		else:
			return False
	def isDone(self):
		if not self.line_pts == None and not self.active_pts == None and len(self.line_pts) == len(self.active_pts):
			return True
		else:
			return False
	def addSegment(self):
		if not self.isDone():
			line_pts = list(self.line_pts)
			self.active_pts = list(self.active_pts)
			self.active_pts.append(line_pts[len(self.active_pts)])
			self.active_pts = tuple(self.active_pts)

	def defLine(self,points,render_surface):		
		self.image = pygame.Surface(render_surface.get_size())
		self.image.set_colorkey([0,0,0])
		self.line_pts = points
		self.line_pts.append((self.parent.dot.x+(self.parent.dot.image.get_width()/2.0),self.parent.dot.y+2))
		self.active_pts = ()
		self.addSegment()
	def resetLine(self):
		self.line_pts = None
		self.active_pts = None
	def render(self):
		if isinstance(self.render_surface,pygame.Surface):
			if self.isDef():
				if not self.isDone():
					self.addSegment()
					pygame.draw.lines(self.image,[255*self.parent.rating["technological"],255*self.parent.rating["militaristic"],255*self.parent.rating["cultural"]],False,self.active_pts,3)
					self.render_surface.blit(self.image,(0,0))
class Domain:
	def __init__ (self,parent,id,name,url,pgs_scanned,loc,rating):
		self.parent = parent
		self.id = id
		self.name = name
		self.url = url
		self.pgs_scanned = pgs_scanned			
		self.loc = loc
		self.line_done = False
		self.rating = rating

		self.dot = DomainDot(self,parent.map)
		self.line = DomainLine(self,parent.map)			
		self.tag = DomainTag(self,parent.map_tags)
		self.marker = DomainMarker(self,parent.info_top)
		
		self.markerx = self.parent.screen.get_width()/2
		self.markery = 0

		self.ratio = pygame.Surface((14,40))
		self.ratio.fill((255,0,0))
		self.ratio.set_colorkey((255,0,0))
		pygame.draw.polygon(self.ratio,[128,128,128],((0,0),(self.ratio.get_width(),0),(self.ratio.get_width(),self.ratio.get_height()-10),(self.ratio.get_width()/2.0,self.ratio.get_height()),(0,self.ratio.get_height()-10)))		
	def curve_points(self,start, end):
		midpoint_variance, curve_push = (20, 30)
		base_divisions, add_divisions = (40, 40)

		divisions = random.randint(base_divisions, base_divisions + add_divisions)
		# determine control points
		midy = (end[1] - start[1])/2.0 + start[1]
		control1 = (start[0] + (random.random()*midpoint_variance - midpoint_variance/2.0), midy + curve_push + (random.random()*midpoint_variance - midpoint_variance/2.0))
		control2 = (end[0] + (random.random()*midpoint_variance - midpoint_variance/2.0), midy - curve_push + (random.random()*midpoint_variance - midpoint_variance/2.0))
		pts = []
		for i in range(divisions):
			pts.append(self.calc_curve_pt(i*1.0/divisions, [start, control1, control2, end]))
		return pts
	def calc_curve_pt(self,inc, pts):
		def mid_pt(a, b):
			return (a[0] + (b[0] - a[0])*inc, a[1] + (b[1] - a[1])*inc)
		# 4 points to 3
		temp = [mid_pt(pts[0], pts[1]), mid_pt(pts[1], pts[2]), mid_pt(pts[2], pts[3])]
		# 3 points to 2
		pts = [mid_pt(temp[0], temp[1]), mid_pt(temp[1], temp[2])]
		# 2 points to 1
		return mid_pt(pts[0], pts[1])
	def render(self):
		if not self.line.isDef():
			to_draw = [x for x in self.parent.getLink(self.parent.current_word) if not x.line.isDone()]
			if self.id == to_draw[0].id:
				self.marker.render()
				x = self.parent.map_background.get_width()*((self.loc["lon"]+180.0)/360.0)
				y = self.parent.map_background.get_height()*(((self.loc["lat"]*-1.0)+90)/180)
				ox = self.marker.x+(self.marker.image.get_width()/2.0)
				oy = 0

				self.line.defLine(self.curve_points((ox,oy),(x,y)),self.parent.map)
				self.line.render()
		else:
			self.marker.render()
			self.line.render()
		if self.line.isDone():
			self.dot.render()
			self.tag.render()
	def reset(self):
		self.tag = DomainTag(self,self.parent.map_tags)
		self.line = DomainLine(self,self.parent.map)
		self.marker = DomainMarker(self,self.parent.info_top)
		self.dot = DomainDot(self,self.parent.map)
	def getRelPos(self,render_surface):
		x = (render_surface.get_width()*((self.loc["lon"]+180.0)/360.0))-self.dot.image.get_width()/2.0
		y = (render_surface.get_height()*(((self.loc["lat"]*-1.0)+90)/180))-self.dot.image.get_height()/2.0
		if y > (render_surface.get_height()/2):
			y+=15
		return (x,y)
	def getRelX(self,render_surface):
		return (render_surface.get_width()*((self.loc["lon"]+180.0)/360.0))
	def getRelY(self,render_surface):
		y = (render_surface.get_height()*(((self.loc["lat"]*-1.0)+90)/180))
		if y > (render_surface.get_height()/2.0):
			y+=15
		return y
		
world = World()
