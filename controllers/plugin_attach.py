# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 22/02/2012
###################################################
import os
from gluon import current
from plugin_attach import Attachment

if current.globalenv.get('cms'):
	attach = Attachment(db=cms.db)
else: 
	attach = Attachment()

def index():
	a = attach.define_table()
	return dict(f=a.fields)

def explorer():
	content = attach.view()
	response.view = 'plugin_app/content.%s'%request.extension
	return dict(content=content)
	
def delete():
	attach.delete()
	return explorer()
	
def upload_callback():
	attach.upload()
	return response.json({'success':True})
	
def upload1():
	content = attach.view(type='table')
	return dict(content=content)	

def upload_data():
	# inserts file and associated form data.        
	attach.upload_data(request.vars.multi_file)	
	
def download():
	attach.define_table()
	return response.download(request,db)

def upload():
	#from plugin_app import ColorBox
	button1 = ''#SPAN(ColorBox(caption='Scan',source=URL(c='plugin_scan',f='scan',args=request.args,vars=request.vars),url=URL(c='plugin_attach',f='view',args=request.args,vars=request.vars),target='progress',width='100%',height=700),_id='button_scan')
	button2 = SPAN(T('Attachment'),_id="upfile1",style="cursor:pointer")
	button3 = INPUT(_id="data_file_file", _class="", _type="file", _name="file",_style="display:none")
	script = SCRIPT('''$("#upfile1").click(function () {$("#data_file_file").trigger('click');});''')
	form = FORM(button1, ' ', button2, button3, script)
	form.attributes['_id'] = "myform"
	form.attributes['_action'] = URL(f="upload_data",args=request.args,vars=request.vars)    
	return dict(form=form, table=view())	

def view():
	table=TABLE()
	a = attach.define_table()
	rows = attach.db((a.tablename==attach.tablename)&(a.table_id==attach.table_id)).select()
	for row in rows:
		ajax = "ajax('%s', [], 'progress')"%(URL(f='del_file',args=[attach.tablename,attach.table_id,row.id],vars=request.vars))
		delete = A(T('Delete'),_href='#',_onclick=ajax,_id='delete')		
		ajax = "gView('http://%s/%s/static/uploads/%s/%s');"%(request.env.http_host,request.application,attach.tablename,row.file)
		view = A(row.name,_href='#',_onclick=ajax,_id='view')		
		ajax = "ajax('%s', [], 'box_edit_default')"%(URL(f='extract',args=[attach.tablename,row.file]))
		filesize= row.filesize or 0
		if filesize>1024*1024: filesize = str(round(filesize/1024*1024,2))+ 'Gb'
		elif filesize>1024: filesize = str(round(filesize/1024,2))+ 'Mb'
		elif filesize>1: filesize = str(int(filesize))+ 'Kb'
		else: filesize = str(round(filesize,2))+ 'Kb'
		tr = TR(TD(SPAN(row.extension,_class='filetype_'+row.extension)),TD(view),TD(filesize,_style='text-align:right'),TD(delete))
		table.append(tr)
	return table

def del_file():
	attach.delete()
	return view()	
	
def applet():
	script = '''<APPLET CODE="EditOnline.class" WIDTH=1 HEIGHT=0 ARCHIVE="EditOnline.jar" codebase="%s">
	  <param name="filename" value="http://113.191.248.231:84/webdav/%s"> 
	</APPLET>'''%(URL(c='static',f='plugin_attach'),request.vars.file)
	return XML(script)	
		
