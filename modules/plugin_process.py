# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 22/02/2012
# Version 0.2 Date: 07/03/2014
###################################################
from gluon import current, LOAD, redirect
from html import *
from gluon.dal import Field
from validators import IS_IMAGE, IS_NULL_OR, IS_IN_SET, IS_EMPTY_OR
import os

PROCEDURE = 0
PROCESS = 1
FOLDER = 2
PAGE = 3
TABLENAME = 3
OBJECTSID = 4


		
class ProcessModel:
	def __init__(self,**attr):
		# self.db = attr.get('db',current.globalenv['db'])
		# self.auth = attr.get('auth',current.globalenv['auth'])
		self.init(**attr)
						
	def init(self,**attr):
		self.db = attr.get('db',None)
		if not self.db:
			from gluon import DAL
			self.db = DAL('sqlite://process.db3',pool_size=1,check_reserved=['all'],fake_migrate_all=False,migrate=True,lazy_tables=True,folder=current.request.folder+'/databases/process')
		self.auth = attr.get('auth',None)
		if not self.auth:
			from gluon.tools import Auth
			from plugin_auth import ProcessAuth
			self.auth = ProcessAuth(self.db, hmac_key=Auth.get_or_create_key()) 
			self.auth.init(migrate=True)
						
	def define_procedures(self,migrate=False):
		if 'procedures' not in self.db.tables: 
			self.db.define_table('procedures',
				Field('name',unique=True,required=True),
				Field('label'),
				Field('description'),
				Field('avatar','upload',autodelete=True,requires=IS_NULL_OR(IS_IMAGE()),uploadfolder=os.path.join(current.request.folder,'static/uploads/procedures')),
				Field('user_group','reference auth_group'),
				Field('auth_group','list:reference auth_group'),
				Field('folder','list:integer'),
				Field('ptype',default='on',requires=IS_IN_SET(['in','on','out'])),
				Field('is_create','boolean',default=True),
				Field('display_order','integer',default=100),
				format='%(name)s',
				migrate=migrate)
			self.db.procedures.avatar.represent = lambda value,row: IMG(_src=URL(r=current.request,c='static',f='uploads/procedures',args=[value]))

		return self.db.procedures

	def define_process(self,migrate=False):	
		if 'process' not in self.db.tables: 
			self.define_procedures(migrate)
			self.db.define_table('process',
				Field('procedures','reference procedures'),
				Field('paccess','list:reference process',default=[]),
				Field('pnext','reference process'),
				Field('name',unique=True,required=True),
				Field('label'),
				Field('description',default=''),
				Field('avatar','upload',autodelete=True,requires=IS_NULL_OR(IS_IMAGE()),uploadfolder=os.path.join(current.request.folder,'static/uploads/process')),
				Field('auth_group','list:reference auth_group',label='Groups use this process'),
				Field('view_group','list:reference auth_group',label='Groups view this process'),
				Field('process_group','list:reference auth_group',label='Process to groups'),
				Field('pmode',requires=IS_EMPTY_OR(IS_IN_SET(['radio','checkbox','set','return','org']))),
				Field('ptype',default='on',requires=IS_IN_SET(['in','on','out'])),
				Field('url'),
				Field('is_first','boolean',default=False),
				Field('is_copy','boolean',default=False),
				Field('is_confirm','boolean',default=False),
				Field('is_lock','boolean',default=False),
				Field('tablename'),
				Field('field','list:string'),
				Field('setting','text'),
				Field('display_order','integer',default=100),
				Field('time_feedback','integer',default=0),
				Field('time_type',default='days',requires=IS_IN_SET(['days','hours','minutes','weeks'])),
				format='%(name)s',
				migrate=migrate)
			self.db.process.avatar.represent = lambda value,row: IMG(_src=URL(r=current.request,c='static',f='uploads/process',args=[value]))
		return self.db.process		
			
	def define_objects(self,migrate=False):	
		if 'objects' not in self.db.tables: 
			self.define_process(migrate)
			self.db.define_table('objects',
				Field('folder','integer'),
				Field('foldername'),
				Field('tablename'),
				Field('table_id','integer'),
				Field('objects_id','integer'),
				Field('process','reference process'),
				Field('auth_group','reference auth_group'),
				Field('auth_org','reference auth_group',default=self.auth.auth_org),
				Field('publish_on','datetime',default=current.request.now),
				Field('expired_on','datetime'),
				Field('created_by','integer',default=self.auth.user_id or 1),
				Field('created_on','datetime',default=current.request.now),
				format='%(tablename)s %(table_id)s',
				migrate=migrate)
		return self.db.objects		

	def define_process_lock(self,migrate=False):	
		if 'process_lock' not in self.db.tables: 
			self.define_process(migrate)
			self.db.define_table('process_lock',
				Field('tablename'),
				Field('table_id','integer'),
				Field('objects_id','integer'),
				Field('process','integer'),
				Field('comment_lock','text'),
				Field('comment_unlock','text'),
				Field('lock_by','integer',default=self.auth.user_id or 1),
				Field('lock_on','datetime',default=current.request.now),
				Field('unlock_on','datetime'),
				format='%(tablename)s %(table_id)s',
				migrate=migrate)
		return self.db.process_lock
		
	def define_process_log(self,migrate=False):	
		if 'process_log' not in self.db.tables: 	
			self.define_objects(migrate)
			self.define_process(migrate)
			self.db.define_table('process_log',
				Field('objects','reference objects'),
				Field('process','reference process'),
				Field('auth_group','reference auth_group'),
				Field('created_by','integer',default=self.auth.user_id or 1),
				Field('created_on','datetime',default=current.request.now),
				migrate=migrate)
		return self.db.process_log
		
	def get_id(self,tablename,value,field='name'):
		table = eval('self.define_%s()'%tablename)
		row = self.db(table[field]==value).select().first()
		return row.id if row else 0		

	def widget_folder(self, field, value):
		from plugin_app import select_option
		from plugin_cms import CmsModel
		cms = CmsModel()
		cms.define_folder()
		list_id = []
		try:
			if not value: 
				if current.request.args[FOLDER]: 
					value = cms.get_id('folder',current.request.args[FOLDER])
			if current.request.args[PROCEDURES]:
				procedure = self.define_procedures()
				list_id = procedure(current.request.args[PROCEDURES]).folder 
		except:
			pass
		widget = SELECT(['']+select_option(cms.db,self.auth,'folder',field='label',selected=[value],list_id=list_id,permission=current.request.function),_name=field.name,_id=field._tablename+'_'+field.name,requires=field.requires)
		return widget
		
#####################################################################
## PROCEDURE CLASS
		
class Procedures(ProcessModel):
	def __init__(self,**attr):
		self.init(**attr)
		self.procedure_name = attr.get('procedure',current.request.args(PROCEDURE))
		

	def menu(self,auth_group):
		if not auth_group: return ''
		request = current.request
		procedures = self.define_procedures()
		content = UL()
		rows = self.db(procedures.auth_group.contains(auth_group)).select(orderby=procedures.display_order)
		for row in rows: 
			if self.auth.has_permission('explorer',procedures,row.id,self.auth.user_id):
				url = URL(r=request,c='plugin_process',f='explorer',args=[row.name]) 
				content.append(LI(A(row.avatar,current.T((row.label or row.name).capitalize()),_href=url,_class='procedure_menu selected' if row.name==self.procedure_name else 'procedure_menu'))) 
		return DIV(content,_id='menu_procedure')


#####################################################################
## PROCESS CLASS
		
class Process(ProcessModel):
	def __init__(self,**attr):
		self.init(**attr)
		request = current.request
	
		self.procedure_name = attr.get('procedure',request.args(PROCEDURE))
		self.process_name = attr.get('process',request.args(PROCESS))
		self.process_id = self.get_id('process',self.process_name)
		if self.process_id==0:
			self.process_id = self.get_process_first()
			process = self.define_process()
			self.process_name = process(self.process_id).name if process(self.process_id) else None
		
		self.folder_name = attr.get('folder',request.args(FOLDER))
		self.tablename = attr.get('tablename',request.args(TABLENAME))
		if self.tablename:
			if self.tablename.split('.')[-1]=='html': self.tablename = None
		self.objects_id = attr.get('objects_id',request.args(OBJECTSID))
				
		self.auth_group = self.db.auth_user(self.auth.user_id).auth_group if self.db.auth_user(self.auth.user_id) else None
		self.auth_groups = self.auth.auth_groups()
		if request.args(OBJECTSID):
			objects = self.define_objects()(request.args(OBJECTSID))
			if not objects:
				redirect(URL(r=request,vars=request.vars,args=request.args[:-1]),client_side=True)
				
	def get_table_id(self):		
		if not self.objects_id: return None
		objects = self.define_objects()
		return objects(self.objects_id).table_id if objects(self.objects_id) else None 

	def get_process_first(self):		
		procedure_id = self.get_id('procedures',self.procedure_name)		
		process = self.define_process()
		row = self.db((process.procedures==procedure_id)&(process.is_first==True)).select().first()
		if not row: row = self.db(process.procedures==procedure_id).select(orderby=process.display_order).first()
		return row.id if row else None
		
	def create_objects(self,folder_id,tablename,table_id):
		process_first = self.get_process_first()
		objects = self.define_objects()
		objects_id = objects.insert(folder=folder_id,foldername=self.folder_name,tablename=tablename,table_id=table_id,auth_group=self.auth_group,process=process_first)
		log = self.define_process_log()
		log.insert(objects=objects_id,auth_group=self.auth_group,process=process_first)

	def update_folder(self,folder_id,tablename,table_id):
		objects = self.define_objects()
		self.db((objects.tablename==tablename)&(objects.table_id==table_id)).update(folder=folder_id,foldername=self.folder_name)
		
	def delete_objects(self,objects_ids=[]):
		db = self.db
		auth = self.auth
		log = self.define_process_log()
		for id in objects_ids:	
			db(db.objects.id==objects_id).delete()
			log.insert(objects=objects_id,auth_group=self.auth_group,process=self.process_id)
			
	def is_lock(self,tablename,table_id):
		pl = self.define_process_lock()
		lock = self.db((pl.tablename==tablename)&(pl.table_id==table_id)&(pl.unlock_on==None)).select().last()
		return (lock!=None)
			
	def toolbars(self):
		if not self.process_name: return ''
		T = current.T
		auth = self.auth
		db = self.db
		request = current.request
		content = DIV(_id='toolbars_process')
		query = db.process.paccess.contains(self.process_id)&db.process.auth_group.contains(self.auth_groups,all=False)	
		rows = db(query).select(orderby=db.process.display_order)
		if self.objects_id:
			objects = self.define_objects()[self.objects_id] 
			pl = self.define_process_lock()
			process_lock = db((pl.tablename==objects.tablename)&(pl.table_id==objects.table_id)&(pl.unlock_on==None)).select().last()
		else:
			process_lock = None
		for row in rows:
			avatar='http://%s/%s/static/uploads/process/%s'%(request.env.http_host,request.application,row.avatar or 'avatar.png') 
			name = SPAN(IMG(_src=avatar),SPAN(T(row.label or row.name),_id='name'))
			process = A(name,_href='#',_class='btn btn-default button_process_%s'%(row.is_confirm or False),_id='process_%s'%row.id)
			if self.objects_id:
				if process_lock:
					if (row.id == process_lock.process)&(process_lock.lock_by==auth.user_id): 
						content.append(process)
						name = SPAN(IMG(_src=avatar),SPAN(T('Unlock'),_id='name'))
						process = A(name,_href='#',_class='btn btn-default button_process_unlock',_id='process_%s'%row.id)
						content.append(process)
				elif row.is_lock:
					name = SPAN(IMG(_src=avatar),SPAN(T('Lock for %s'%row.name),_id='name'))
					process = A(name,_href='#',_class='btn btn-default button_process_lock',_id='process_%s'%row.id)
					content.append(process)
				else:
					content.append(process)
			else:
				settings = eval(row.setting.replace(chr(13),'')) if row.setting else {}
				if settings.get('check_group',False): content.append(process)
		return content

	def filter(self):
		T = current.T
		db = self.db
		request = current.request
		process = self.define_process()
		procedure_id = self.get_id('procedures',request.args(PROCEDURE))		
		rows = db((process.procedures==procedure_id)&process.view_group.contains(self.auth_groups,all=False)).select(orderby=process.display_order)
		if len(rows)==0: return ''
		content = UL(_id='filter_process',_class='nav nav-tabs')
		args = [arg for arg in request.args[:FOLDER+1]]
		while len(args)<=PROCESS: args.append('')
		vars = {}
		for key in request.vars.keys(): 
			if key !='search': vars[key]=request.vars[key]
		for row in rows: 
			avatar='http://%s/%s/static/uploads/process/%s'%(request.env.http_host,request.application,row.avatar or 'avatar.png') 
			name = SPAN(IMG(_src=avatar),T('Filter %s'%(row.label or row.name)))
			args[PROCESS] = row.name 
			url = URL(r=request,c='plugin_process',f='explorer',args=args,vars=vars)
			cls ='nav_item active' if request.args(PROCESS) == row.name else 'nav_item'
			content.append(LI(A(name,_href=url,_id='process_filter',_class='filter_process_selected filter_%s'%row.name if row.name==self.process_name else 'filter_process filter_%s'%row.name),_class=cls))
		return content		

	def process_lock(self,process_id,objects_ids,lock=True,comment=''):
		db = self.db
		auth = self.auth
		pl = self.define_process_lock()
		self.define_objects()
		try:
			if lock:
				for id in objects_ids:
					objects = db.objects(id)
					pl.insert(tablename=objects.tablename,table_id=objects.table_id,objects_id=id,process=process_id,comment_lock=comment)
			else:
				for id in objects_ids:
					objects = db.objects(id)
					db((pl.tablename==objects.tablename)&(pl.table_id==objects.table_id)&(pl.process==process_id)&(pl.lock_by==auth.user_id)&(pl.unlock_on==None)).update(comment_unlock=comment,unlock_on=current.request.now)
			return 'OK'		
		except Exception, e:
			return e
			
	def process_run(self,process_id,objects_ids):
		process = self.define_process()
		process = process(process_id)
		if current.request.vars.comment_lock: 
			return self.process_lock(process_id,objects_ids,True,current.request.vars.comment_lock)
		elif current.request.vars.comment_unlock:
			return self.process_lock(process_id,objects_ids,False,current.request.vars.comment_unlock)
		elif process.url: 
			args = [self.procedure_name,self.process_name,self.folder_name,self.tablename,self.objects_id]
			if current.request.vars.objects:
				if isinstance(current.request.vars.objects,str):
					self.objects_id = int(current.request.vars.objects)
					args[OBJECTSID] = self.objects_id
					objects = self.define_objects()(self.objects_id)
					args[TABLENAME] = objects.tablename
					from plugin_cms import CmsFolder
					folder = CmsFolder().define_folder()
					if folder(objects.folder):
						args[FOLDER] = folder(objects.folder).name
			vars = {}
			for key in current.request.vars: vars[key]=current.request.vars[key]
			if '.cb' in process.url: return self.load(process.url,args,vars)
			url = self.get_url(process.url,args,vars)
			redirect(url,client_side=True)
		elif process.pmode in ['return']: 
			return self.process_group(process_id,objects_ids,[])
		elif process.pmode in ['radio','checkbox']: 
			return self.process_tree(process_id,selected=process.process_group)				
		elif not process.pmode: 
			return self.process_group(process_id,objects_ids,process.process_group)
		else: 
			return self.process_group(process_id,objects_ids,[self.auth_group])
		
	def process_tree(self,process_id,selected,header=''):
		from plugin_app import treeview	
		request = current.request
		T = current.T
		db = self.db
		self.define_process()
		process = db.process(process_id)
		try: settings=eval(process.setting.replace(chr(13),''))
		except: settings={}		
		permission = settings.get('permission',None)
		type=process.pmode if process.pmode in ['checkbox','radio'] else 'checkbox'
		if process.process_group:
			query = db.auth_group.id.belongs(process.process_group)
		else:
			query= (db.auth_group.atype!='auth')
			if process.ptype=='on': 
				query &=(db.auth_group.parent== self.auth.auth_org)
			else: 
				query &= ~db.auth_group.atype.belongs(['sub_org','staff','group_org'])
				query &= (db.auth_group.parent==None)
		rows = db(query).select(orderby=db.auth_group.display_order)
		query = (db.auth_group.id>0)
		tr = TR()
		for row in rows:
			pnode = XML(str(INPUT(_type=type,_name='auth_group',_value=row.id,_checked=(row.id in selected),_class='check_all'))+ ' '+row.role)
			tree = treeview(self.db,self.auth,'auth_group',parent=row.id,permission=permission,field='role',depth=3,query=query,pnode=pnode,checkbox=type,selected=selected,orderby=db.auth_group.display_order|db.auth_group.role,tree='auth_group_'+str(row.id))
			tr.append(TD(tree))
		tree = TABLE(tr)				
		script = '''<script type="text/javascript">
					$(document).ready(function(){
						$('.check_all').click(function(){
							if ($(this).is(':checked')) {
								$(this).parent().find('input:checkbox').attr('checked', true);
							}
							else{
								$(this).parent().find('input:checkbox').attr('checked', false);
							}
						});
					});
					$('#button_submit').click(function () {
						parent.$.colorbox.close();
						location.reload();
					})
			</script>
			'''	
		# ajax = "ajax('%s', ['auth_group'], '')"%(URL(r=request,c='plugin_process',f='group.html',args=request.args,vars=request.vars))
		# button = INPUT(_type='button',_value=T('Submit'),_onclick=ajax,_id='button_submit')
		# form = DIV(XML(script),H4(T(process.name)),header,tree,button,_id='process_tree')
		form = FORM(XML(script),H4(T(process.name)),header,tree,INPUT(_type='submit',_value=T('Submit'),_id='button_submit'),_action=URL(r=request,c='plugin_process',f='group.html',args=request.args,vars=request.vars))
		return form
		
	def process_group(self,process_id,objects_ids,group_ids):
		T = current.T
		db = self.db
		auth = self.auth
		log = self.define_process_log()
		process = db.process(process_id)
		pnext = process.pnext or process_id
		i = 0	
		
		if self.folder_name:
			from plugin_cms import CmsFolder
			folder = CmsFolder()
			folder_id = folder.get_id('folder',self.folder_name)
			db.objects.folder.default = folder_id
			db.objects.foldername.default = self.folder_name
		
		for id in objects_ids:
			objects = db.objects(id)	
			if process.is_copy:
				objects_id = db.objects.insert(tablename=objects.tablename,table_id=objects.table_id,objects_id=objects.id,process=pnext,auth_group=self.auth_group)
			elif (process.pmode=='return'): 
				objects_id = objects.objects_id
				db((db.objects.objects_id==objects.id)&(db.objects.auth_org==auth.auth_org)).delete()
				db(db.objects.id==objects.id).delete()
			else:
				db(db.objects.id==objects.id).update(process=pnext)
				objects_id = objects.id
				
			log.insert(objects=objects_id,process=pnext,auth_group=self.auth_group)
			db((db.objects.objects_id==objects_id)&(db.objects.auth_org==auth.auth_org)).update(process=pnext)
			db((db.objects.id==objects_id)&(db.objects.auth_org==auth.auth_org)).update(process=pnext)
			for id in group_ids: 
				if db((db.objects.objects_id==objects_id)&(db.objects.auth_group==id)).count()==0:
					expired = None
					try:
						if process.time_feedback>0:
							import datetime
							d = {}
							d[process.time_type] = process.time_feedback
							expired = datetime.datetime.now() + datetime.timedelta(**d)
					except: 
						pass
					db.objects.insert(tablename=objects.tablename,table_id=objects.table_id,objects_id=objects_id,auth_group=id,process=pnext,expired_on=expired)
				else:
					db((db.objects.objects_id==objects_id)&(db.objects.auth_group==id)).update(process=pnext)
				log.insert(objects=objects_id,process=pnext,auth_group=id)
				i+=1
			
		script = SCRIPT('''$('#button_submit').click(function () {parent.$.colorbox.close(); location.reload();})''')	
		button = INPUT(_type='button',_value=T('Submit'),_id='button_submit')
		content = DIV(script,H4(T("Cập nhật thành công")),button)
		return content
		
	def load(self,url,args,vars):
		tmp = url.split('/')
		if len(tmp)>1: c, f = tmp[0], tmp[1]
		else: c, f = 'plugin_process', tmp[0]
		return LOAD(r=current.request,c=c,f=f,args=args,vars=vars,ajax_trap=False)

	def get_url(self,url,args,vars):
		tmp = url.split('/')
		if len(tmp)>1: c, f = tmp[0], tmp[1]
		else: c, f = 'plugin_process', tmp[0]
		return URL(r=current.request,c=c,f=f,args=args,vars=vars,extension='html')
		
	def status(self):
		T = current.T
		request = current.request
		db = self.db
		auth = self.auth
		tablename = self.tablename
		table_id = self.table_id
		process = db.process		
		log = self.define_process_log()
				
		content = DIV(_id='process_status')
		#rows = db((db.objects.tablename==tablename)&(db.objects.table_id==table_id)&(db.objects.auth_group==self.auth_group)).select()
		#content.append(rows)
		
		rs = db(db.procedures.folder.contains(self.folder_name)&db.procedures.auth_group.contains(self.auth_group)).select()
		for r in rs:
			rows = db(db.process.procedures==r.id).select(orderby=db.process.display_order)
			procedure = None
			for row in rows:
				objects = db((db.objects.tablename==tablename)&(db.objects.table_id==table_id)&(db.objects.process==row.id)).select()
				if len(objects)>0:
					ul = UL()
					for o in objects: ul.append(LI(o.auth_group.role))		
					tmp = DIV(H5(row.name),ul)
					if not procedure: procedure = DIV()
					procedure.append(tmp)
			if procedure: 
				content.append(H4(T('Procedure'),' ',r.name))
				content.append(procedure)
		return content

		
class ProcessCms(Process):
	def get_query(self,process=None):
		db = self.db
		auth = self.auth
		request = current.request
		objects = self.define_objects()
		if self.folder_name:
			from plugin_cms import CmsFolder
			cms = CmsFolder()
			parent = cms.get_id('folder',self.folder_name)
			folders = cms.get_folders(parent)
			query = objects.folder.belongs(folders)	
			if self.tablename:	
				query &=(objects.tablename==self.tablename)
				tables = [self.tablename]
			else:
				tables = self.get_tables(cms.db.folder(parent).setting)
			if request.vars.search:
				qtable = None
				for table in tables:
					t = cms.define_table(table)
					q = None
					for f in t.fields:
						if t[f].type in ['string','text','list:string']: 
							q = q|t[f].contains(request.vars.search) if q else t[f].contains(request.vars.search)
						rows = cms.db(q).select(t.id,distinct=True)
					table_ids = [row.id for row in rows]
					if q: 
						q = (objects.tablename==table)&objects.table_id.belongs(table_ids)
						qtable = qtable|q if qtable else q
				query &=qtable
		else:
			query = (objects.id>0)

		query &= objects.auth_group.belongs(auth.auth_groups())		
		query &=((objects.table_id!=None)|(objects.created_by==auth.user_id))

		if not process: 
			process = self.get_id('process',self.process_name)
			if process == 0: process = None
		if process:
			if not isinstance(process,list): process=[process]
			tmp = None
			for p in process: 
				if (p == '0')|(p=='None'): p = None
				tmp = tmp|(objects.process==p) if tmp else (objects.process==p)
			query&=(tmp)
		
		return query
	
	def get_search(self):
		search = FORM(INPUT(_name='search',_value=current.request.vars.search ,_class='form-control string' or ''),INPUT(_type='submit',_class='btn btn-success',_value='Tìm kiếm'),_class="navbar-form navbar-right",_id='process_search')
		return search	
	
	def get_page(self):	
		try: 
			page = int(current.request.args(PAGE).split('.')[0])
		except: 
			page = 1
		return page
		
	def get_length(self):
		if self.folder_name:
			from plugin_cms import CmsFolder
			cms = CmsFolder()
			table = cms.define_folder()
			row = cms.db(table.name==self.folder_name).select().first()
			try:
				setting = eval(row.setting.replace(chr(13),''))
			except: setting = {}
			return setting.get('length',10)	
		return 10
		
	def get_rows(self,process=None,page=None,length=None,orderby=None):
		db = self.db
		query = self.get_query(process)	
		if not page: page = self.get_page()
		if not length: length = self.get_length()
		if not orderby: orderby = ~db.objects.id		
		limit = None
		count = db(query).count(db.objects.id)
		if length>0: 
			if count<(page-1)*length: limit = (0,length)
			else: limit = ((page-1)*length,page*length)
		rows = db(query).select(db.objects.ALL,orderby=orderby,limitby=limit,distinct=True)	
		return rows,count
	
	def search(self):
		request = current.request
		div = DIV(_class="navbar-form navbar-right",_id='process_search')
		div.append(INPUT(_type='text',_class='form-control string',name='search',_placeholder="Từ khóa...",_value=request.vars.search))
		vars = request.vars
		# vars['search']= 227
		url = URL(r=current.request,c='plugin_process',f='explorer',args=request.args[:3],vars=vars)
		div.append(A('Tìm kiếm',_class='btn btn-success',_href=url))
		return div
		
	def explorer(self):	
		div = DIV(_class='panel panel-success',_id='content')
		# div.append(DIV(self.filter(),self.get_search(),_class='panel-heading'))
		div.append(DIV(self.filter(),_class='panel-heading'))
		div.append(DIV(self.toolbars(),DIV(self.read() if self.objects_id else self.view()),_class='panel-body'))
		return div
		
	def view(self):
		from plugin_cms import CmsModel
		cmsmodel = CmsModel()
		request = current.request
		T = current.T
		rows, count = self.get_rows()
		if os.path.isfile('%s/views/plugin_process/view/%s.html'%(current.request.folder,self.tablename)):
			context = dict(request=request,T=T,cmsmodel=cmsmodel,rows=rows,count=count)
			return XML(current.response.render('plugin_process/view/%s.html'%self.tablename, context))		
		i = 0
		content = TABLE(_id='process_id',_class='table table-striped defview')
		thead = THEAD()
		tr = TR()
		tr.append(TH('#',_style="width: 30px;text-align: center;"))
		tr.append(TH(T('Title')))
		tr.append(TH(T('Description')))
		# tr.append(TH('Avatar'))
		thead.append(tr)
		content.append(thead)
		for row in rows:
			tr = TR(_class='line_%s'%(i%2))
			dtable = cmsmodel.define_table(row.tablename)
			dcontent = dtable(row.table_id)
			if dcontent:
				div = DIV(_class=row.tablename)
				title = A(dcontent.name,_href=URL(r=request,f='explorer',args=request.args[:3]+[row.tablename,row.id]))
				# avatar=''
				# if dcontent.avatar[0:5]!='http:':
					# avatar='http://%s/%s/static/uploads/%s/%s'%(request.env.http_host,request.application,row.tablename,dcontent.avatar or 'avatar.png') 
				# else:
					# avatar=dcontent.avatar
				tr.append(TD(INPUT(_type='checkbox',_name='objects',_value=row.id),_class='stt'))
				tr.append(TD(title,_class='title'))
				tr.append(TD(A(dcontent.description,_href=URL(r=request,f='explorer',args=request.args[:3]+[row.tablename,row.id])),_class='description')) 
				# tr.append(TD(DIV(IMG(_src=avatar),_class='avatar'))) 
				content.append(tr)
				i += 1	
		nb = len(rows)
		if nb>0:
			if nb<count: 
				content = DIV(content,DIV(self.pagination(count,self.get_length()),_class='clearfix'))
		return content		
		
	def read(self):
		T = current.T
		if not self.objects_id: 
			return ''
		
		from plugin_cms import CmsModel
		cmsmodel = CmsModel()
		objects = self.define_objects()
		objects = objects(self.objects_id)
		dtable = cmsmodel.define_table(objects.tablename)
		dcontent = dtable(objects.table_id)
		
		if os.path.isfile('%s/views/plugin_process/read/%s.html'%(current.request.folder,self.tablename)):
			context = dict(request=current.request,dtable=dtable,dcontent=dcontent,objects=objects,T=T)
			return XML(current.response.render('plugin_process/read/%s.html'%self.tablename, context))
				
		content = TABLE(_id=objects.tablename,_class='table')
			
		for field in dtable.fields:
			if dtable[field].readable:
				if dtable[field].type=='upload':
					data = cmsmodel.get_images_content(objects.tablename,dcontent[field])
					content.append(TR(TD(B(current.T(field.capitalize())),_class='lablel'),TD(data),_class=str(field.capitalize())))
				elif field=='folder':
					data = current.T(cmsmodel.db.folder(dcontent[field]).label)
					content.append(TR(TD(B(current.T(field.capitalize())),_class='lablel'),TD(data),_class=str(field.capitalize())))
				# elif dtable[field].type.startswith('reference'):
					# data = cmsmodel.db[field](dcontent[field]).name
					# content.append(TR(TD(B(current.T(field.capitalize())),_class='lablel'),TD(data),_class=str(field.capitalize())))
				else:
					data = XML(dcontent[field])
					content.append(TR(TD(B(current.T(field.capitalize())),_class='lablel'),TD(data),_class=str(field.capitalize())))
						
		from plugin_upload import FileUpload
		attach = FileUpload(db=cmsmodel.db,tablename=objects.tablename,table_id=objects.table_id,upload_id=0)
		content.append(TR(TD(B(current.T('Đính kèm')),_class='lablel'),TD(attach.view_publish()),_class='upload_file'))
		
		# from plugin_comment import Comment
		# comment = Comment(db=self.db,auth=self.auth,tablename=objects.tablename,table_id=objects.table_id,objects_id=objects.id,process=self.process_id)
		# content.append(TR(TD(B(current.T('Đánh giá')),_class='lablel'),TD(comment.view())))
		
		content = DIV(DIV(INPUT(_type='checkbox',_name='objects',_value=self.objects_id,_checked=True,_style="display:none"),_id='process_id'),content)
		return content
		
	def view_lock(self,tablename,table_id):
		T = current.T
		pl = self.define_process_lock()
		locks = self.db((pl.tablename==tablename)&(pl.table_id==table_id)).select()
		table = TABLE(_class="table",_id='view_lock')
		table.append(TR(TH(T('Sự kiện')),TH(T('Lý do')),TH(T('Người thực hiện')),TH(T('Thời gian thực hiện'))))
		for lk in locks:
			user = self.db.auth_user(lk.lock_by)
			lock_by =  str(user.first_name) + ' ' + str(user.last_name)
			tr = TR(TD(T('Check Out')),TD(lk.comment_lock),TD( lock_by,_rowspan="2",_class='lock_by'),TD(lk.lock_on))
			table.append(tr)
			tr = TR(TD(T('Check In')),TD(lk.comment_unlock),TD(lk.unlock_on))
			table.append(tr)
		return table
		
	def pagination(self,count,length):
		T = current.T
		request = current.request
		args = request.args
		if len(args) < PAGE: return ''
		elif len(args) == PAGE: args.append('1.html')
		page = self.get_page()
		if length>0:
			tmp = int(count/length)
			if count > tmp*length: pagecount = tmp+1
			else: pagecount = tmp
		content = DIV(_id='page')
		ul = UL(_class='page-ul pagination')
		(p1, m1) = (page - 5,'...') if page > 5 else (1, '')
		(p2, m2) = (page + 5,'...') if page + 5 < pagecount else (pagecount+1, '')
		if (p2 < 11) & (pagecount >10): p2 = 11
		if m1=='...':
			args[PAGE]='1.html'
			url = URL(r=request,args=args)
			ul.append(LI(A(T('First'),'  ',_href=url)))
			ul.append(LI(m1))
		for x in xrange(p1,p2):
			args[PAGE]='%s.html'%x
			url = URL(r=request,args=args)
			ul.append(LI(A(x,'  ',_href=url),_class='active' if x == page else ''))
		if m2=='...':
			ul.append(LI(m2))
			args[PAGE]='%s.html'%pagecount
			url = URL(r=request,args=args)
			ul.append(LI(A(T('End'),_href=url)))
		content.append(ul)
		return content			
		
	def menu(self,folder,deep=1,**attr):
		from plugin_cms import CmsModel
		cmsmodel = CmsModel()
		table = cmsmodel.define_folder()
		rows = cmsmodel.db(table.parent==folder).select(orderby=table.display_order)
		if len(rows)==0: return ''
		args = [arg for arg in current.request.args[:FOLDER+1]]
		while len(args)<=FOLDER: args.append(self.process_name)
		content = UL(_class=attr.get('ul_class_%s'%deep,attr.get('ul_class')),_id=attr.get('ul_id_%s'%deep,attr.get('ul_id')))
		folders = attr.get('folders',[])
		add = None
		for row in rows:
			if (len(folders)>0)&(row.id not in folders):
				pass
			else:
				add = True
				args[FOLDER] = row.name
				url = URL(r=current.request,f='explorer',args=args,vars=current.request.vars)
				link = A(current.T(row.label or row.name),_href=url,_class=attr.get('a_class_%s'%deep,attr.get('a_class')),_id=attr.get('a_id_%s'%deep,attr.get('a_id')))
				content.append(LI(link,self.menu(row.id,deep+1,**attr),_class=attr.get('li_class_%s'%deep,attr.get('li_class')),_id=attr.get('li_id_%s'%deep,attr.get('li_id'))))
		if not add: return ''
		if attr.get('div_class_%s'%deep,attr.get('div_id_%s'%deep)):
			content = DIV(content,_class=attr.get('div_class_%s'%deep),_id=attr.get('div_id_%s'%deep))
		elif attr.get('div_class',attr.get('div_id')):
			content = DIV(content,_class=attr.get('div_class'),_id=attr.get('div_id'))		
		return content

	def menu_process(self,folder,deep=1,**attr):
		from plugin_cms import CmsModel
		cmsmodel = CmsModel()
		table = cmsmodel.define_folder()
		rows = cmsmodel.db(table.parent==folder).select(orderby=table.display_order)
		if len(rows)==0: return ''
		args = [arg for arg in current.request.args[:FOLDER+1]]
		while len(args)<=FOLDER: args.append(self.process_name)
		content = UL(_class=attr.get('ul_class_%s'%deep,attr.get('ul_class')),_id=attr.get('ul_id_%s'%deep,attr.get('ul_id')))
		folders = attr.get('folders',[])
		if folders==[]:
			p = self.get_id('procedures',self.procedure_name)
			if p: folders = self.db.procedures[p].folder or []
		vars = {}
		for key in current.request.vars.keys(): 
			if key !='search': vars[key]=current.request.vars[key]		
		add = None
		for row in rows:
			if (len(folders)>0)&(row.id not in folders):
				pass
			else:
				
				add = True
				args[FOLDER] = row.name
				url =''
				if args:
					url = URL(r=current.request,f='explorer',args=args,vars=vars)
				else:
					url = URL(r=current.request,c='plugin_process',f='explorer',args=['document','soanthao'],vars=vars)
				link = A(current.T(row.label or row.name),_href=url,_class=attr.get('a_class_%s'%deep,attr.get('a_class')),_id=attr.get('a_id_%s'%deep,attr.get('a_id')))
				content.append(LI(link,self.menu(row.id,deep+1,**attr),_class=attr.get('li_class_%s'%deep,attr.get('li_class')),_id=attr.get('li_id_%s'%deep,attr.get('li_id'))))
		if not add: return ''
		if attr.get('div_class_%s'%deep,attr.get('div_id_%s'%deep)):
			content = DIV(content,_class=attr.get('div_class_%s'%deep),_id=attr.get('div_id_%s'%deep))
		elif attr.get('div_class',attr.get('div_id')):
			content = DIV(content,_class=attr.get('div_class'),_id=attr.get('div_id'))		
		return content
		
	def menu_acc(self):
		content = UL(_class='sortable list',_id="sortable-with-handles")
		folder = DIV(_class='accordion_subject', _id="head_folder")
		folder.append(self.menu_process(folder=128,deep=1,ul_class='sf-menu'))
		folder.append(DIV(_class='clearfix'))
		content.append(LI(folder))

		return content
		
	def menu_news(self):
		if self.procedure_name:
			div = DIV(_class="btn-group")
			from plugin_cms import CmsFolder, get_setting
			cms = CmsFolder()
			folder_id = cms.get_folder(self.folder_name)
			role = 'create_'+self.procedure_name
			# if self.auth.has_permission(role, 'folder', folder_id):
			try:
				tables = self.get_tables(cms.db.folder(folder_id).setting)
				for table in tables:
					div.append(A(current.T('New '+table) ,_class="btn btn-danger "+table,_href=URL(r=current.request,c='plugin_process',f='edit',args=[self.procedure_name,self.process_name,self.folder_name,table])))
			except: print 'not create new'
			return div
		else:return ''
		
	def get_tables(self,setting):
		from plugin_cms import get_setting
		tables = get_setting(setting,key='TABLES')
		if not tables:
			from plugin_app import get_setting
			tables = get_setting(key='TABLES')
		if not tables: tables = []
		elif isinstance(tables,str): tables = [tables]
		return tables
		
		
class ProcessCrud(Process):

	def procedures(self):
		from plugin_app import widget_tree, treeview
		
		def widget_folders(field, value):
			from plugin_app import treeview
			from plugin_cms import CmsModel
			cms = CmsModel()
			cms.define_folder()
			db = cms.db
			auth = self.auth
			if not value: value = []
			rows = db(db.folder.parent==None).select(orderby=db.folder.display_order|db.folder.name)
			tr = TR()
			for row in rows:
				pnode = XML(str(INPUT(_type='checkbox',_name=field.name,_value=row.id,_checked=(row.id in value),_class='check_all'))+' '+row.name)
				tree = treeview(db,auth,'folder',parent=row.id,checkbox='checkbox',pnode=pnode,key=field.name,selected=value,orderby=db.folder.display_order|db.folder.name,tree=field.name+str(row.id))
				tr.append(TD(tree))
			script = '''<script type="text/javascript">
						$(document).ready(function(){
							$('.check_all').click(function(){
								if ($(this).is(':checked')) {
									$(this).parent().find('input:checkbox').attr('checked', true);
								}
								else{
									$(this).parent().find('input:checkbox').attr('checked', false);
								}
							});
						});
				</script>'''	
			return DIV(XML(script),TABLE(tr))		
		
		def widget_auth(field, value):
			db = self.db
			options = ['']
			rows = db(db.auth_group.atype=='auth').select(orderby=db.auth_group.role)
			for row in rows:
				options.append(OPTION(row.role,_value=row.id,_selected=(row.id==value)))
			return SELECT(options,_name=field.name,requires=field.requires)
		
		table = self.define_procedures(True)
		table.user_group.widget = widget_auth
		table.auth_group.widget = widget_tree
		table.folder.widget = widget_folders
		return table
			
	def process(self):	
		from plugin_app import widget_tree, treeview
		db = self.db
		auth = self.auth
		
		def widget_auth(field, value):
			widget = treeview(db,auth,'auth_group',parent=None,tree=field.name,field='role',key=field.name,checkbox='checkbox',selected=value,orderby=db.auth_group.display_order)
			return widget
			
		def widget_procedures(field, value):
			rows = db(db.procedures.id>0).select()
			if not value:
				if (current.request.args(1)=='process.procedures')&current.request.args(2).isdigit():
					value = int(current.request.args(2))
			else:
				value=int(value)
			op = [OPTION(row.name,_value=row.id,_selected=(row.id == value)) for row in rows]
			ajax = "ajax('%s',['%s'],'widget_access')"%(URL(r=current.request,c='plugin_process',f='widget_access',args=current.request.args,vars=current.request.vars),field.name)
			widget = SELECT(op,_name=field.name,_id=field._tablename+'_'+field.name,_onchange=ajax)
			return widget
			
		def widget_access(field, value):
			from plugin_app import input_option
			query = None
			if value:
				if len(value)>0:
					row = db(db.process.id==value[0]).select().first()
					if row: query = (db.process.procedures==row.procedures)
			elif current.request.args(1)=='process.procedures':
				query = (db.process.procedures==current.request.args(2))
			else:
				row = db(db.procedures.id>0).select().first()
				if row: query = (db.process.procedures==row.id)
			tmp = input_option('process', type='checkbox', selected=value or [], query=query, keyname=field.name)
			widget = DIV(tmp, _id='widget_access')
			return widget
			
		def widget_next(field, value):
			rows = db(db.procedures.id>0).select()
			op = [OPTION('')]
			for row in rows:
				rs = db(db.process.procedures==row.id).select()
				for r in rs: op.append(OPTION(row.name+' -> '+r.name,_value=r.id,_selected=(r.id == value)))
			widget = SELECT(op,_name=field.name,_id=field._tablename+'_'+field.name)
			return widget
			
		def widget_setting(field, value):
			v = dict()
			if value: v = eval(value)
			widget = DIV()
			for key in v.keys():
				widget.append(DIV(INPUT(_type='text',_value=key,_style='width:80px;'),INPUT(_type='text',_value=v[key]),_id='setting_key_'+key))
			return widget
			
		table = self.define_process(True)
		table.procedures.widget = widget_procedures
		table.paccess.widget = widget_access
		table.pnext.widget = widget_next
		table.auth_group.widget = widget_auth
		table.view_group.widget = widget_auth
		table.process_group.widget = widget_tree
		return table
	
		