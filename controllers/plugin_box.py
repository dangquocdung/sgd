# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 22/02/2012
# Version 0.2 Date: 19/02/2014
###################################################

import os

def index():
	box = cms.define_box()
	box.avatar.requires=IS_NULL_OR(IS_IMAGE())
	box.avatar.uploadfolder=os.path.join(request.folder,'static/plugin_box/avatar')
	box.avatar.represent = lambda value,row: IMG(_src=URL(r=request,c='static',f='plugin_box/avatar',args=[value]),_width="100px")
	box.boxtype.widget = SQLFORM.widgets.autocomplete(request, box.boxtype, limitby=(0,30), min_length=1)
	
	content = SQLFORM.grid(box,args=request.args)
	response.view = 'plugin_cms/content.html'	
	return dict(content=content)

def layout():
	box = get_box()
	for root, dirs, files in os.walk(request.folder+'/views/layout'):
		pass
	op = ['']+[OPTION(file,_value=URL(args=[file]),_selected=(file==request.args(0))) for file in files]
	#op = ['']+[OPTION(file,_value=file,_selected=(file==request.args(0))) for file in files]
	ajax = "ajax('%s',['layout'],'layout')"%(URL(f='get_layout'))	
	files = SELECT(op,_name='layout',_id='filename',_onchange="this.options[this.selectedIndex].value && (window.location = this.options[this.selectedIndex].value);")
	#files = SELECT(op,_name='layout',_id='filename',_onchange=ajax)
	content = DIV(files)
	content.append(INPUT(_type="button",_class="btnsave",_id="btnsave",_value=T("Save"),_onclick="update(0);"))
	content.append(INPUT(_type="button",_class="btnsave",_id="btnnew",_value=T("New layout"),_onclick="update(1);"))
	content.append(DIV(LOAD(f='get_layout',args=request.args),_id='layout'))
	return dict(box=box,content=content)

def get_box():
	box = cms.define_box()
	boxtypes = cms.db(box).select(box.boxtype,orderby=box.boxtype,distinct=True)
	header = UL()
	tabs = []
	i = 1
	for r in boxtypes:
		header.append(LI(A(T(r.boxtype.capitalize()),_href='#tabs-box-%s'%i)))
		rows = cms.db(box.boxtype==r.boxtype).select(orderby=box.name)
		tab = DIV(_id="tabs-box-%s"%i,_class="connectedSortable",_style="height: 300px; overflow-y: scroll;margin:3px;")
		for row in rows:
			tab.append(cms.box(row.name))
		tabs.append(tab)
		i+=1
	content = DIV(header,_id="tabs-box")
	for tab in tabs: 
		content.append(tab)		
	return content

def get_layout():
	import cStringIO
	from bs4 import BeautifulSoup
	layout = request.args(0)
	if not layout: return ''
	try:
		soup = BeautifulSoup(open("%s/views/layout/%s"%(request.folder,layout)))
		soup = soup.select(".container")[0]
		mydivs = soup.findAll('div')
		i= 0
		for div in mydivs: 
			if div.get("class"): 
				div["class"].append("connectedSortable")
			else:
				div["class"] = ["connectedSortable"]		
			if  not div.get("id"): 
				div["id"] =  'connectedSortable_id_%s'%i
			i+=1
		content = response.render(cStringIO.StringIO(str(soup)), {})
		return XML(content)
	except Exception, e:
		return e
	
def update():
	from bs4 import BeautifulSoup
	layout = "%s/views/layout/%s"%(request.folder,request.args(0))
	soup = BeautifulSoup(open(layout))
	container = request.vars.container
	container = container.replace('[[','{{')
	container = container.replace(']]','}}')
	
	soup.select(".container")[0].replace_with('###container###')
	layout = "%s/views/layout/%s"%(request.folder,request.vars.newlayout)
	f = open(layout,'w+')
	html = BeautifulSoup(soup.prettify().replace('###container###',container))
	f.write(html.prettify())	
	f.close()
	if request.args(0) != request.vars.newlayout:
		redirect(URL(f='layout',args=[request.vars.newlayout]),client_side=True)
	
def page():
	return dict()	
		