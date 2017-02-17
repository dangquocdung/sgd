# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 28/02/2012
# Version 0.2 Date: 28/02/2014
###################################################
from gluon import current
from html import *
from gluon.dal import Field
from validators import IS_LENGTH
import os
exec('import applications.%s.modules.plugin_app as app' % current.request.application)

class Attachment:
	def __init__(self,**attr):
		self.db = attr.get('db',current.globalenv['db'])
		self.auth = attr.get('auth',current.globalenv['auth'])
		self.tablename = attr.get('tablename', current.request.vars.tablename or 'attachment')
		self.table_id = attr.get('table_id', current.request.vars.table_id or current.request.vars.uuid)
		self.attachment_id = attr.get('attachment_id', current.request.vars.attachment_id or current.request.args(2))
		self.table = attr.get('attachments','attachments')
		self.path = '%s/static/uploads/attachments/%s'%(current.request.folder, self.tablename)
		
	def define_table(self,migrate=False):
		db = self.db
		if self.table not in db.tables:
			db.define_table(self.table,
				Field('tablename',writable=False,readable=False),
				Field('table_id',writable=False,readable=False),
				Field('name'),
				Field('filetype'),
				Field('extension'),
				Field('filesize','double'),
				Field('filepath','upload',autodelete=True,uploadfolder=os.path.join(self.path)),
				Field('textcontent','text',default='',requires=IS_LENGTH(16777215),writable=False,readable=False),
				Field('created_by','integer',default=self.auth.user_id or 1,writable=False,readable=False),
				Field('created_on','datetime',default=current.request.now,writable=False,readable=False),
				migrate=migrate)
		db[self.table].tablename.default = self.tablename
		db[self.table].table_id.default = self.table_id
		return db[self.table]

	def files(self):
		db = self.db
		attach = self.define_table()
		attachs = []
		rows = db((attach.tablename==self.tablename)&(attach.table_id==self.table_id)).select()
		for row in rows:
			attachs.append('%s/%s'%(self.path,row.filepath))
		return attachs	
		
	def get_row(self):
		db = self.db
		request = current.request
		T = current.T
		attach = self.define_table()
		rows = db((attach.tablename==self.tablename)&(attach.table_id==self.table_id)).select()
		return rows
			
	def view(self,crud=['delete'],type='table',length=10,edit_online=False):
		db = self.db
		request = current.request
		T = current.T
		content = DIV(_id='attachment',_class=self.tablename) 
		attach = self.define_table()
		rows = db((attach.tablename==self.tablename)&(attach.table_id==self.table_id)).select()
		if len(rows) == 0: return ''
		if type=='ul': ul = UL(_class='attachment')
		elif type=='ligne': ul = SPAN()
		else: 
			tr = TR(TH('STT'),TH('Type'),TH(T('Name')),TH(T('Size')),TH(T('Preview')))
			for f in crud: tr.append(TH(T(f.capitalize())))
			ul = TABLE(tr,_id='table_attach')
						
		i = 1
		for row in rows:
			if str(row.filepath).startswith(self.table):
				href=URL(r=request,c='plugin_attach',f='download',args=['db',row.filepath])
				name = A(row.name, _href=href)
			else: 
				href=URL(r=request,c='static',f='uploads/attachments/%s/%s'%(self.tablename,row.filepath))
				name = A(row.name, _href=href)
			icon = row.extension.lower()
			if length == 0:new_name = row.name+'.'+icon
			else:
				new_name = row.name[:10]+'.'+icon if len(row.name)<10 else row.name[:10]+'...'+icon
			if os.path.isfile(self.path+'/%s.pdf'%row.name):
				url = 'http://%s/%s/static/uploads/attachments/%s/%s.pdf'%(request.env.http_host,request.application,self.tablename,row.name)
			elif (icon in ['png','jpg','jpeg','bmp','gif']):
				url = 'http://%s/%s/static/uploads/attachments/%s/%s'%(request.env.http_host,request.application,self.tablename,row.filepath)
			else:
				url = 'http://%s/%s/static/uploads/attachments/%s/%s'%(request.env.http_host,request.application,self.tablename,row.filepath)
				url = 'http://docs.google.com/viewer?url=%s'%url
			#preview = A(new_name,_href=XML(url),_target='blank',_title=T('Click to preview'))		

			filesize= row.filesize or 0
			if filesize>1024*1024: filesize = str(round(filesize/1024*1024,2))+ 'Gb'
			elif filesize>1024: filesize = str(round(filesize/1024,2))+ 'Mb'
			elif filesize>1: filesize = str(int(filesize))+ 'Kb'
			else: filesize = str(round(filesize,2))+ 'Kb'

			preview = A(new_name,_href='#',_onclick='window.open("'+url+'","Preview","width=800,height=700,toolbar=no,location=no,directories=no,status=no,menubar=no,left=600,top=0")',_title=T('Click to preview'))
			
			edit = ''
			if (icon not in ['zip','pdf'])&edit_online:
				ajax = "ajax('%s', [], 'applet_id')"%(URL(r=request,c='plugin_attach',f='applet',args=request.args,vars=dict(filepath=row.filepath)))	
				edit = SPAN(A(T('Sửa bản thảo'),_href='#',_onclick=ajax,_id='button_edit_online',_title=T('Sửa bản thảo')))
			
			if type=='ul': attach = LI(edit, A(SPAN(_class='file_download'),_title=T('Click to download'),_href=href),preview,SPAN(filesize,_class='filesize'))
			elif type=='ligne': attach = SPAN(edit, A(SPAN(_class='file_download'),_title=T('Click to download'),_href=href),preview,SPAN(filesize,_class='filesize'))
			else:
				attach = TR(TD(i,_style='text-align:center'),TD(SPAN(icon,_class='filetype_'+icon)),TD(name),TD(filesize))
				attach.append(TD(preview))
				i += 1
			for f in crud:
				url = URL(r=request,f=f,args=[self.tablename,self.table_id,row.id],extension='load')
				ajax = "ajax('%s', [], 'attachment')"%(url)
				button = A(T(f.capitalize()),_href='#',_onclick=ajax,_id=f)
				attach.append(button)
			ul.append(attach)	
		content.append(ul)
		content.append(DIV(_id='applet_id',_style='height:0px;'))
		return content	
		
	def upload(self):
		id = None
		request = current.request
		if request.vars.qqfile:
			filename=request.vars.qqfile
			extension = filename.split('.')[-1]
			name = filename[:-(len(extension)+1)]
			import uuid	
			new_name = '%s.%s.%s'%(name.replace(' ','_'),uuid.uuid4(),extension)
			attach = self.define_table()
			id = attach.insert(name=name,filepath=attach.filepath.store(request.body,filename),extension=extension)    
			filesize= os.path.getsize(self.path+'/'+attach(id).filepath)/1024
			new_name = self.rename(attach(id).filepath,new_name)
			self.db(attach.id==id).update(filesize=filesize,filepath=new_name)
		return id
		
	def insert(self,filename):
		extension = filename.split('.')[-1]
		name = filename[:-(len(extension)+1)]
		attach = self.define_table()
		id = attach.insert(name=name,filepath=filename,extension=extension)    
		filesize= os.path.getsize(self.path+'/'+attach(id).filepath)/1024
		import uuid	
		new_name = '%s.%s.%s'%(name.replace(' ','_'),uuid.uuid4(),extension)
		new_name = self.rename(attach(id).filepath,new_name)
		self.db(attach.id==id).update(filesize=filesize,filepath=new_name)
		return id	
		
	def delete(self):
		try:
			db = self.db
			attach = self.define_table()			
			db(attach.id==self.attachment_id).delete()	
		except: pass
		
	def update(self,id,uuid):
		db = self.db
		attach = self.define_table()
		db((attach.tablename==self.tablename)&(attach.table_id==uuid)).update(table_id=id)			

	def rename(self,old_name,new_name):
		try:
			uploadfolder=os.path.join(self.path)
			os.rename(os.path.join(uploadfolder, old_name),os.path.join(uploadfolder, new_name))
			return new_name
		except: return old_name
		
	def upload_data(self,fobject):
		# inserts filepath and associated form data.        
		try:
			filename=fobject.filename
			extension = filename.split('.')[-1].lower()
			name = filename[:-(len(extension)+1)]
			a = self.define_table()
			id = a.insert(name=name,extension=extension,filepath=a.filepath.store(fobject.file,fobject.filename))
			filesize= (0.0+os.path.getsize(self.path+'/'+a(id).filepath))/1024
			name = name.replace(' ','_')
			new_name = '%s.%s'%(name,extension)
			i = 1
			while os.path.isfile(self.path+'/'+new_name):
				new_name = '%s(%s).%s'%(name,i,extension)
				i+=1
			new_name = self.rename(a(id).filepath,new_name)
			self.db(a.id==id).update(name=new_name[:-(len(extension)+1)],filesize=filesize,filepath=new_name)		
			if extension in ['doc','docx','xls','xlsx']: self.word2pdf(self.path+'/'+new_name)
		except Exception, e:
			print 'plugin_attach module upload_data error: %s'%e
		
	def word2pdf(self,word_file):
		try: 
			import subprocess
			subprocess.Popen('C:\\Windows\\System32\\cscript.exe %sstatic\\plugin_attach\\save_pdf.js %s'%(current.request.folder,word_file))
		except: 
			pass		