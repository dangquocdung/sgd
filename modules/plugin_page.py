###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 22/02/2012
# Version 0.2 Date: 20/01/2014
###################################################
from gluon import current, HTTP
from html import *
from gluon.dal import Field
from validators import IS_EMPTY_OR, IS_NOT_EMPTY, IS_IMAGE, IS_NULL_OR, IS_IN_DB, IS_IN_SET, IS_NOT_IN_DB
import os


#####################################################################
## BOX TABLE

	

class Page:
	def __init__(self,**attr):
		self.object = attr.get('object',None)
		try:
			self.db = self.object.db
			self.auth = self.object.auth
			self.div_id = self.object.div_id
			self.folder = self.object.folder.id
			self.vars = current.request.vars
		except:
			self.db = current.globalenv['db']
			self.auth = current.globalenv['auth']
			self.div_id = ''
			self.folder = current.request.vars.folder_id
			self.vars = None		
			
		#self.box = define_box(self.db,self.auth) 
		#self.fbox = define_folder_box(self.db,self.auth) 

	def define_page(self,migrate=False):	
		db = self.db
		if 'page' in db.tables: return db.page
		return db.define_table('page',
			Field('name',unique=True,requires=IS_NOT_EMPTY()),
			Field('description','text',default=''),
			Field('content','text',default=''),
			migrate=migrate)					
			
	def show(self,name,context={}):
		try:
			import cStringIO
			box = self.box(name) if isinstance(name,int) else self.db(self.box.name==name).select().first() 
			if not box: return 'Box %s not exist'%name
			content = box.content
			content = content.replace('&quot;', "'")
			content = content.replace('&#39;', '"')	
			content = '<div id="box%s" class="box %s"> %s %s</div>'%(box.id,box.name,box.data,content)
			try:
				if 'header' not in context.keys(): context['header'] = H3(current.T(box.name))
				settings = eval(box.setting.replace(chr(13),''))
				for key in settings.keys(): context[key] = settings[key]
			except: pass
			content = current.response.render(cStringIO.StringIO(content), dict(context=context))
			return XML(content)
		except:
			return 'Box %s error: %s'%(box.name,box.content)
		
	def render_box(self,box,context={}):
		try:
			import cStringIO
			content = box.content
			content = content.replace('&quot;', "'")
			content = content.replace('&#39;', '"')	
			content = '<div id="box%s" class="box %s"> %s %s</div>'%(box.id,box.name,box.data,content)
			try:
				if 'header' not in context.keys(): context['header'] = H3(current.T(box.name))
				settings = eval(box.setting.replace(chr(13),''))
				for key in settings.keys(): context[key] = settings[key]
			except: pass
			content = current.response.render(cStringIO.StringIO(content), dict(context=context))
			return XML(content)
		except:
			return 'Box %s error: %s'%(box.name,box.content)

	def render(self,div='left',type=None):
		links = ''
		db = self.db
		if not type: 
			if self.object:
				type='content' if self.object.id else 'folder'
			elif self.folder: type = 'folder'
			else: type = 'link'
		query = (db.folder_box.active==True)&(db.folder_box.divid==div)&(db.folder_box.folder==self.folder)&(db.box.id==db.folder_box.box)
		rows = db(query&(db.folder_box.type==type)).select(db.folder_box.box,db.folder_box.position,orderby=db.folder_box.position,distinct=True)
		for row in rows: links += str(self.render_box(db.box(row.box),{}))
		if (type=='folder')&(links!=''):
			position = rows[0].position 
			rows = db(query&(db.folder_box.position<=position)&(db.folder_box.type=='link')).select(db.box.id,orderby=db.folder_box.position,distinct=True)
			for row in rows: links = str(self.render_box(db.box(row.id))) + links 
			rows = db(query&(db.folder_box.position>position)&(db.folder_box.type=='link')).select(db.box.id,orderby=db.folder_box.position,distinct=True)
			for row in rows: links = links + str(self.render_box(db.box(row.id))) 
		return XML(links)
		