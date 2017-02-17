from gluon import current
from html import *

class Crawler:
	def crawler_rss(self,link,records=10):
		import gluon.contrib.feedparser as feedparser
		d = feedparser.parse(link)
		i = 0
		div=DIV()
		for entry in d.entries :
			if i == records :
				break
			else :
				ul = UL(_class='contentul row_'+str(i+1)) 
				if self.find_imageURL_in_content(entry.description)!='':
					li= LI(_class='image')
					a = A(_href=entry.link,_target='_blank')
					img = IMG(_src= self.find_imageURL_in_content(entry.description))
					a.append(img)
					li.append(a)
					ul.append(li)
					li1 = LI(_class='name')
				else:
					li1 = LI(_class='name_no_img')
					
				if self.find_price(entry.description)!='':
					li= LI(self.find_price(entry.description),_class='price')
					ul.append(li)
				a1 = A(_href=entry.link,_target='_blank')
				a1.append(entry.title)
				li1.append(a1)
				ul.append(li1)
				div.append(ul)
				i+=1
		return XML(div)

	def crawler_rss_more(self,link):
		import gluon.contrib.feedparser as feedparser
		d = feedparser.parse(link)
		i = 0
		div=DIV()
		for entry in d.entries :
			ul = UL(_class='contentul row_'+str(i+1)) 
			li1 = LI(_class='name field_2')
			a1 = A(_href=entry.link,_target='_blank')
			a1.append(entry.title)
			li1.append(a1)
			ul.append(li1)
			li2 = LI(_class='heading field_3')
			li2.append(XML(entry.description))
			ul.append(li2)
			div.append(ul)
			i+=1
		return div
		
	def crawler_rss_from_bao_moi(self,keyword):
		import gluon.contrib.feedparser as feedparser
		d = feedparser.parse('http://www.baomoi.com/Rss/RssFeed.ashx?ph='+keyword+'&s=')
		i = 0
		print 'http://www.baomoi.com/Rss/RssFeed.ashx?ph='+keyword+'&s='
		div=DIV()
		for entry in d.entries :
			ul = UL(_class='contentul row_'+str(i+1)) 
			li1 = LI(_class='name field_2')
			a1 = A(_href=entry.link,_target='_blank')
			a1.append(entry.title)
			li1.append(a1)
			ul.append(li1)
			li2 = LI(_class='heading field_3')
			li2.append(XML(entry.description))
			ul.append(li2)
			div.append(ul)
			i+=1
		return div 

	def find_imageURL_in_content(self,new_content):	
		link =''
		content = new_content.replace(' ', '')
		n1 = content.find('<img')
		if n1>-1: 
			n1 = content.find('src=', n1)
			if n1>-1: 
				n1 = content.find('"', n1)
				if n1>-1:
					n1+=1
					n2 = content.find('"', n1)
					link = content[n1:n2]
				else:
					n1 = content.find("'", n1)
					if n1>-1:
						n1+=1
						n2 = content.find("'", n1)
						link = content[n1:n2]	
		if (link <>'') & (link[0:7] <> 'http://'):
			ns = link.split('/')
			link = ns[len(ns)-1]
		return link	
		
	def find_price(self,new_content):	
		content = new_content.replace(' ', '')
		link =''
		n1 = content.find('field-name-price') 
		if n1>-1: 
			n1 = content.find('<divclass="field-itemeven">', n1)
			if n1>-1:
				n1+=27
				n2 = content.find('</div>', n1)
				link = content[n1:n2]
		return link