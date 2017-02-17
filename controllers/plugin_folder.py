###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 1.0 Date: 27/02/2015
###################################################
# -*- coding: utf-8 -*-

FOLDER_PARENT = 60

from plugin_folder import Folder
cms.define_folder()
folder = Folder(cms.db,auth,parent=FOLDER_PARENT)

def index():
	content = folder.display_tree()
	return dict(content=content)

def update_display():
	try:
		db = folder.db
		old_parent = int(request.vars.old_parent)
		parent = int(request.vars.parent)
		new_position = int(request.vars.new_position)
		old_position = int(request.vars.old_position)
		rows = db((db.folder.parent==parent)).select(orderby=db.folder.display_order)
		i = 1
		for row in rows:
			row.update_record(display_order=i)
			i+=1
		if old_parent == parent:		
			rows = db((db.folder.parent==parent)&(db.folder.display_order>old_position)&(db.folder.display_order<=new_position)).select()
			for row in rows:
				row.update_record(display_order=row.display_order-1)
			rows = db((db.folder.parent==parent)&(db.folder.display_order>=new_position)&(db.folder.display_order<old_position)).select()
			for row in rows:
				row.update_record(display_order=row.display_order+1)
		else:
			rows = db((db.folder.parent==parent)&(db.folder.display_order>=new_position)).select()
			for row in rows:
				row.update_record(display_order=row.display_order+1)	
		db(db.folder.id==request.vars.id).update(parent=parent,display_order=new_position)
		return ''	
	except Exception, e:
		return 'Báo lỗi: %s'%e
		
def form():
	try:
		from plugin_folder import FolderCrud
		folder = FolderCrud(cms.db,auth,parent=FOLDER_PARENT)	
		id = request.vars.folder
		form = folder.form(id)
		ajax = "ajax('%s',['name','label','parent','description','display_order','layout'],'')"%URL(f='update',args=[id] if id else None)
		form.append(INPUT(_type='button',_value=T('Submit'),_onclick=ajax))
		return form	
	except Exception, e:
		return e
	
def update():
	try:
		from plugin_folder import FolderCrud
		folder = FolderCrud(cms.db,auth,parent=FOLDER_PARENT)
		id = request.args(0)
		folder.update(id,request.vars)
	except Exception, e:
		print e
	redirect(URL(f='index'),client_side=True)