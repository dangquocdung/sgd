# -*- coding: utf-8 -*-
###################################################
# This content was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 27/02/2015
###################################################

from gluon import current
from html import *
T = current.T
request = current.request

#####################################################################


			
class Folder:

	def __init__(self,db,auth,**attr):
		self.db = db		
		self.auth = auth
		self.tablename = attr.get('tablename','folder')
		self.parent = attr.get('parent',None)
		self.id = attr.get('id',None)
		
	def display_tree(self):
		tree = self.menu(self.parent)
		return tree		
		
	def menu(self,folder=None,deep=1,**attr):
		table = self.db[self.tablename]
		rows = self.db(table.parent==folder).select(orderby=table.display_order)
		if len(rows)==0: return ''
		content = UL(_class=attr.get('ul_class_%s'%deep,attr.get('ul_class')),_id=attr.get('ul_id_%s'%deep,attr.get('ul_id')))
		for row in rows:
			try:
				if (row.display_order==0):
					pass
				else:
					cls_li = attr.get('li_class_%s'%deep,attr.get('li_class'))
					cls_a = attr.get('a_class_%s'%deep,attr.get('a_class'))
					folder_name =''
					p = self.db(self.db.folder.name==current.request.args(0)).select().first()
					if p:
						if p.parent==folder:
							folder_name = current.request.args(0)
						elif p.parent:
							folder_name = p.parent.name
					if row.name == folder_name:
						cls_li = str(attr.get('li_class_%s'%deep,attr.get('li_class'))) +' folder_act'
						cls_a = str(attr.get('a_class_%s'%deep,attr.get('a_class'))) +' a_act'
					link = A(row.label,_href='#',_onclick='',_class=cls_a,_id=attr.get('a_id_%s'%deep,attr.get('a_id')))
					content.append(LI(link,self.menu(row.id,deep+1,**attr),_class=cls_li,_id=attr.get('li_id_%s'%deep,row.id)))
			except Exception, e: 
				print e
		if attr.get('div_class_%s'%deep,attr.get('div_id_%s'%deep)):
			content = DIV(content,_class=attr.get('div_class_%s'%deep),_id=attr.get('div_id_%s'%deep))
		elif attr.get('div_class',attr.get('div_id')):
			content = DIV(content,_class=attr.get('div_class'),_id=attr.get('div_id'))		
		return content


		
class FolderCrud(Folder):

	def widget_folder(self, field, value):
		from plugin_app import select_option
		widget = SELECT(['']+select_option(self.db,self.auth,self.tablename,id=self.parent,selected=[value],field='label'),_name=field.name,_id=field._tablename+'_'+field.name,requires=field.requires)
		return widget	
		
	def widget_layout(self, field, value):
		import os
		for root, dirs, files in os.walk(current.request.folder+'/views/layout'):
			pass
		op = [OPTION(file,_value=file,_selected=(value==file)) for file in files]
		widget = SELECT(op,_name=field.name,_id=field._tablename+'_'+field.name)
		return widget
		
	def widget_label(self, field, value):
		widget =''
		if value:
			widget = INPUT(_class='string',_id='folder_label', _name='label',_type='text',_value=value)
		else:
			widget = INPUT(_class='string',_id='folder_label', _name='label',_type='text',_value=value,_onkeyup='remove_unicode()')
		return widget
		
	def form(self,id=None):	
		from sqlhtml import SQLFORM
		table = self.db[self.tablename]
		table.parent.widget = self.widget_folder
		table.layout.widget = self.widget_layout
		table.setting.readable = False
		table.setting.writable = False
		
		form = SQLFORM(table,id,showid=False,buttons=[])
		return form
										
	def update(self,id,vars):	
		table = self.db[self.tablename]
		val = {}
		for field in table.fields:
			if field in vars.keys(): val[field] = vars[field]
		id = self.db(table.id==id).update(**val) if id else table.insert(**val)
		return id
		
	def delete(self,id):	
		table = self.db[self.tablename]
		val = {}
		if id:
			self.db(table.id==id).delete()
		return ''
																				