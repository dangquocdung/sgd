# -*- coding: utf-8 -*-
###################################################
# This content was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 26/02/2014
###################################################
from gluon import current, LOAD
from html import *
from gluon.dal import Field
from validators import IS_EMPTY_OR, IS_NOT_EMPTY, IS_IMAGE, IS_NULL_OR, IS_IN_DB, IS_IN_SET, IS_NOT_IN_DB, IS_SLUG
import os

#####################################################################


def get_setting(data,key=None,default=None):
	try:
		tmp = eval(data.replace(chr(13),''))
		if not key: return tmp
		return tmp[key]
	except:
		return default


		
class CmsModel:
	def __init__(self,**attr):
		self.init(**attr)	
	
	def init(self,**attr):
		self.db = attr.get('db',None)
		if not self.db:
			if 'cms' in current.globalenv.keys():
				self.db = current.globalenv['cms'].db
			else:
				from gluon import DAL
				self.db = DAL('sqlite://cms.db3',pool_size=1,check_reserved=['all'],fake_migrate_all=True,migrate=False,lazy_tables=True,folder=current.request.folder+'/databases/cms')
		try:	
			self.auth = attr.get('auth',current.globalenv['auth'])
		except:
			pass
		
	def define_folder(self,migrate=False):	
		if 'folder' not in self.db.tables:
			self.db.define_table('folder',
				Field('parent','reference folder'),
				Field('label',required=True),
				Field('name',unique=True,required=True),
				Field('description','text',default=''),
				Field('setting','text'),
				Field('layout'),
				Field('display_order','integer',default=100),
				Field('created_by','integer',default= 1,writable=False,readable=False),
				Field('created_on','datetime',default=current.request.now,writable=False,readable=False),
				format='%(name)s',
				migrate=migrate)
		return self.db.folder		

	def define_dtable(self,migrate=False):	
		if 'dtable' not in self.db.tables:
			self.db.define_table('dtable',
				Field('name',unique=True,required=True),
				Field('description','text'),
				Field('publish','boolean'),
				Field('attachment','boolean'),
				Field('layout'),
				Field('display_row','text'),
				Field('display_rows','text'),
				Field('display_order','integer',default=100),
				Field('link_edit'),
				format='%(name)s',
				migrate=migrate)
		return self.db.dtable 

	def define_rtable(self,migrate=False):	
		if 'rtable' not in self.db.tables:
			self.db.define_table('rtable',
				Field('name',required=True),
				Field('dtable',required=True),
				Field('tablename',required=True),
				Field('display_order','integer',default=100),
				format='%(name)s',
				migrate=migrate)
			self.define_dtable()
			self.db.rtable.dtable.requires = IS_IN_DB(self.db,'dtable.name','%(name)s')
			self.db.rtable.tablename.requires = IS_IN_DB(self.db,'dtable.name','%(name)s')
		return self.db.rtable
		
	def define_dcontent(self,migrate=False):	
		if 'dcontent' not in self.db.tables:
			self.define_folder(migrate)
			self.define_dtable(migrate)
			self.db.define_table('dcontent',
				Field('folder','reference folder'),
				Field('dtable'),
				Field('table_id','integer'),
				Field('link'),
				Field('name'),
				Field('avatar'),
				Field('description','text'),
				Field('publish_on','datetime'),
				Field('expired_on','datetime'),
				Field('textcontent','text',default=''),
				Field('languague',default='vie'),
				Field('publisher'),
				Field('creator'),
				Field('created_on','datetime',default=current.request.now),
				Field('modified_on','datetime'),
				format='%(name)s',
				migrate=migrate)
		return self.db.dcontent
		
	def define_dfield(self,migrate=False):	
		if 'dfield' not in self.db.tables: 
			self.db.define_table('dfield',
				Field('name',unique=True,required=True),
				Field('ftype'),
				Field('fdefine','text'),
				Field('ckeditor','boolean'),
				format='%(name)s',
				migrate=migrate)
		return self.db.dfield
		
	def define_tablefield(self,migrate=False):	
		if 'tablefield' not in self.db.tables: 
			self.define_dtable(migrate)
			self.define_dfield(migrate)
			self.db.define_table('tablefield',
				Field('dtable','reference dtable'),
				Field('dfield','reference dfield'),
				Field('dlabel'),
				Field('display_order','integer',default=100),
				migrate=migrate)
		return self.db.tablefield

	def define_box(self,migrate=False):	
		if 'box' not in self.db.tables: 
			self.db.define_table('box',
				Field('boxtype',default=''),
				Field('name',unique=True,required=True),
				Field('avatar','upload',autodelete=True),
				Field('link'),
				Field('setting','text',default='{}'),
				Field('textcontent','text',default=''),
				Field('htmlcontent','text',default=''),
				migrate=migrate)
		return self.db.box

	def define_readcontent(self,migrate=False):	
		if 'readcontent' not in self.db.tables: 
			self.db.define_table('readcontent',
				Field('foldername'),
				Field('tablename'),
				Field('link'),
				Field('clientip'),
				Field('user_agent'),
				Field('created_on','datetime',default=current.request.now),
				migrate=migrate)
		return self.db.readcontent
		
	def define_table(self,tablename,migrate=False):	
		T = current.T
		if (migrate==False)&(tablename in self.db.tables): 
			return self.db[tablename]
		if tablename in ['folder','dtable','rtable','dcontent','dfield','tablefield','box','readcontent']: 
			return eval('self.define_%s()'%tablename)
		db = self.db
		self.define_tablefield()
		dtable = db(db.dtable.name==tablename).select().first()
		if dtable:	
			fields = []
			fieldname = []
			path = os.path.join(current.request.folder,'static/uploads/%s'%tablename)	
			if dtable.publish:
				self.define_folder()
				fields.append(Field('link',unique=True,writable=False,readable=False))
				fields.append(Field('folder','reference folder',label=T('folder')))
				fields.append(Field('name','string',requires=IS_NOT_EMPTY(),label=T('%s name'%(tablename))))
				fields.append(Field('description','text',label=T('%s description'%(tablename))))
				fields.append(Field('avatar','upload',uploadfolder=path,label=T('avatar')))
				fieldname = ['link','folder','name','description','avatar']
			rows = db((db.tablefield.dtable==dtable.id)&(db.tablefield.dfield==db.dfield.id)).select(db.tablefield.ALL,orderby=db.tablefield.display_order)
			if len(rows)>0:
				format = None
				for row in rows:
					reftable = False
					if row.dfield.fdefine:
						field = eval(row.dfield.fdefine)
						if field.type.startswith('reference')|field.type.startswith('list:reference'):
							tname = field.type.split(' ')[-1]
							if tablename != tname:
								reftable = self.define_table(tname)
					else:
						if row.dfield.ftype.startswith('reference')|row.dfield.ftype.startswith('list:reference'):
							tname = row.dfield.ftype.split(' ')[-1]
							if tablename != tname:
								reftable = self.define_table(tname)
						if row.dfield.name=='name': format = '%(name)s' 
						if row.dfield.ftype=='upload':
							field = Field(row.dfield.name,row.dfield.ftype,label=current.T(row.dlabel or row.dfield.name),uploadfolder=path)
						else:
							field = Field(row.dfield.name,row.dfield.ftype,label=current.T(row.dlabel or row.dfield.name))
					if field.name not in fieldname:
						if reftable != None: fields.append(field)
				if len(fields)>0: 
					db.define_table(tablename,*fields,format=format,migrate=migrate,redefine=migrate)
					for row in rows:
						if row.dfield.ckeditor:
							db[tablename][row.dfield.name].represent = lambda value,row: XML(value)
					return db[tablename]
		return None
				
	def define_tables(self,migrate=False):
		self.define_folder(migrate)
		table = self.define_dtable(migrate)
		self.define_dcontent(migrate)
		self.define_dfield(migrate)
		self.define_box(migrate)
		self.define_readcontent(migrate)
		self.define_tablefield(migrate)
		self.define_rtable(migrate)
		rows = self.db(table.id).select()
		for row in rows: self.define_table(row.name,migrate)
				
	def get_id(self,tablename,value,field='name'):
		table = self.define_table(tablename)
		row = self.db(table[field]==value).select().first()
		return row.id if row else 0

	def get_avatar(self,tablename,value):
		return 'http://%s/%s/static/uploads/%s/%s'%(current.request.env.http_host,current.request.application,tablename,value) 

	def get_images_content(self,tablename,value, width=70, height=70):
		request = current.request
		if not value: return '' #'image_upload.file.default.png'
		elif value[0:7] == 'http://': return XML('<img src=%s width=%s height=%s />'%(value,width,height)) if width*height>0 else XML('<img src=%s />'%(value))
		import os
		if os.path.exists(request.folder+'/static/uploads/'+tablename+'/'+ value):
			value='http://'+request.env.http_host +'/'+request.application+'/static/uploads/'+tablename+'/'+ value
		elif os.path.exists(request.folder+'/static/uploads/ckeditor/'+ value):
			value='http://'+request.env.http_host+'/'+request.application+'/static/uploads/ckeditor/'+ value
		elif os.path.exists(request.folder+'/static/uploads/images_download/'+ value):
			value='http://'+request.env.http_host+'/'+request.application+'/static/uploads/images_download/'+ value
		else:
			value='http://'+request.env.http_host+'/'+request.application+'/static/images/img_defautl.jpg'
			return  XML('<img src=%s />'%(value))
		return  XML('<img src=%s />'%(value))
		
	def widget_folder(self, field, value):
		from plugin_app import select_option
		auth = current.globalenv.get('auth',None)
		widget = SELECT(['']+select_option(self.db,auth,'folder',selected=[value]),_name=field.name,_id=field._tablename+'_'+field.name,requires=field.requires)
		return widget	
		

		
class CmsFolder(CmsModel):

	def get_folder(self,folder=None):
		if not folder:
			folder = current.request.args(0)
		if not str(folder).isdigit(): 
			return self.get_id('folder',folder)
		return int(folder)
		
	def get_folders(self,parent=None):
		folder = self.define_folder()
		id_folders = [parent]
		rows = self.db(folder.parent==parent).select(folder.id)
		for row in rows: id_folders += self.get_folders(row.id)
		return id_folders
		
	def get_lasttime(self,folder=None):
		folder = self.get_folder(folder)
		table = self.define_dcontent()
		row = self.db(table).select(orderby=table.modified_on).last()
		return row.modified_on.strftime("%Y%m%d%H%M%S") if row else "0"
		
	def get_page(self):
		try: 
			page = int(current.request.args[-1].split('.')[0])
		except: 
			page = 1
		return page
		
	def get_length(self,folder,length=10):
		return get_setting(self.db.folder(folder).setting,'length',length) if self.db.folder(folder) else length

	def get_query(self,folder=None):	
		dcontent = self.define_dcontent()
		folder = self.get_folder(folder)
		folders = self.get_folders(folder)
		query = dcontent.folder.belongs(folders)
		query &=((dcontent.expired_on>=current.request.now)|(dcontent.expired_on==None))&(dcontent.publish_on<=current.request.now)
		return query
		
	def get_count(self,folder=None,tablename=None):
		query = self.get_query(folder)
		if tablename: 
			dtable = self.define_table(tablename)
			query &= (dtable.link==self.db.dcontent.link)
		return self.db(query).count()
		
	def get_rows(self,folder=None,page=None,length=None,orderby=None,query=None):
		folder = folder or self.get_folder(folder)
		query = self.get_query(folder)&query if query else self.get_query(folder)
		page = page or self.get_page()
		length = length or self.get_length(folder)
		p1 = (page-1)*length
		p2 = page*length
		orderby = orderby or ~self.db.dcontent.publish_on
		rows = self.db(query).select(limitby=(p1,p2),orderby=orderby)
		return rows

	def get_content(self,tablename,orderby=None,folder=None,page=None,length=None,query=None):
		dtable = self.define_table(tablename)
		folder = folder or self.get_folder(folder)
		#query = self.get_query(folder) & (dtable.id==self.db.dcontent.table_id)
		query = self.get_query(folder)&query if query else self.get_query(folder)
		query &= (dtable.link==self.db.dcontent.link)
		
		page = page or self.get_page()
		length = length or self.get_length(folder)
		p1 = (page-1)*length
		p2 = page*length
		orderby = orderby or ~dtable.id
		rows = self.db(query).select(dtable.ALL,limitby=(p1,p2),orderby=orderby)
		return rows
		
	def url_content(self,row):
		return URL(r=current.request,c='portal',f='read',args=[row.folder.name,row.dtable,row.link])

	def url_folder(self,folder_name):
		return URL(r=current.request,c='portal',f='folder',args=[folder_name])

	def layout_folder(self,folder=None):
		table = self.define_folder()
		folder = self.get_folder(folder)
		return table(folder).layout if table(folder) else None
		
	def folder(self,folder=None):
		folder = self.get_folder(folder)
		rows = self.get_rows(folder)
		content = UL()
		i = 1
		for row in rows:
			dcontent = DIV(_class=row.dtable)
			dcontent.append(H2(row.name,_class='name name-%s'%row.dtable))
			url = ''
			if row.avatar[0:5]=='http:':
				url = row.avatar
			else:
				url = self.get_avatar(row.dtable,row.avatar)
			dcontent.append(DIV(IMG(_src=url),_class='avatar avatar-%s'%row.dtable))
			dcontent.append(P(row.description,_class='description description-%s'%row.dtable))
			content.append(LI(A(dcontent,_href=self.url_content(row)),_class='line-%s line-%s'%(row.dtable,i%2))) 
		foldername = self.db.folder(folder).name if self.db.folder(folder) else 'homepage' 
		return DIV(content,_id=foldername,_class=foldername)
		
	def breadcrumb(self,parent=None):
		request = current.request
		T = current.T
		path = ''
		div = DIV(_class="breadcrumb_menu")
		if request.function != 'crud':
			while parent>1:
				folder_id = self.get_folder(parent)
				folder = self.db.folder(folder_id)
				if folder:
					url =''
					if request.controller =='plugin_process':
						url = str(A(B(folder.label),_href=URL(r=request,c='plugin_process',f='explorer',args=[request.args(0),request.args(1),folder.name]),_class = 'folder'+str(parent),cid=request.cid))
					else:
						url = str(A(B(folder.label),_href=URL(r=request,f='folder',args=[folder.name]),_class = 'folder'+str(parent),cid=request.cid))
					path = url + ' > ' + path if path <> '' else url
					parent = folder.parent
			div.append(XML(path))
		return div
		
	def folder_name(self,folder=None):
		folder = self.get_folder(folder)
		foldername = self.db.folder(folder).label if self.db.folder(folder) else 'homepage' 
		return foldername
		
	def folder_name_by_id(self,folder_id=None):
		folder = self.define_folder()
		foldername = self.db.folder[folder_id].label if self.db.folder[folder_id] else 'homepage' 
		return foldername
	
	def folder_layout(self,folder=None):
		folder = self.get_folder(folder)
		folderlayout = self.db.folder(folder).layout if self.db.folder(folder) else 'home_13.html' 
		return folderlayout
		
class Cms(CmsFolder):

	def menu(self,folder,deep=1,**attr):
		table = self.define_folder()
		rows = self.db(table.parent==folder).select(orderby=table.display_order)
		if len(rows)==0: return ''
		content = UL(_class=attr.get('ul_class_%s'%deep,attr.get('ul_class')),_id=attr.get('ul_id_%s'%deep,attr.get('ul_id')))
		from plugin_app import get_short_string
		for row in rows:
			try:
				if (row.display_order==0):
					pass
				else:
					cls_li = attr.get('li_class_%s'%deep,attr.get('li_class'))
					cls_a = attr.get('a_class_%s'%deep,attr.get('a_class'))
					p = self.db(self.db.folder.name==current.request.args(0)).select().first()
					folder_name =''
					if p.parent==folder:
						folder_name = current.request.args(0)
					else:
						if p.parent:
							folder_name = p.parent.name
					if row.name == folder_name:
						cls_li = str(attr.get('li_class_%s'%deep,attr.get('li_class'))) +' folder_act'
						cls_a = str(attr.get('a_class_%s'%deep,attr.get('a_class'))) +' a_act'
					link = A(row.label,_href=self.url_folder(row.name),_class=cls_a,_id=attr.get('a_id_%s'%deep,attr.get('a_id')))
					if attr.get('length'):
						link = A(get_short_string(row.label,attr.get('length')),_href=self.url_folder(row.name),_class=cls_a,_id=attr.get('a_id_%s'%deep,attr.get('a_id')))
					content.append(LI(link,self.menu(row.id,deep+1,**attr),_class=cls_li,_id=attr.get('li_id_%s'%deep,attr.get('li_id'))))
			except Exception, e: print e
		if attr.get('div_class_%s'%deep,attr.get('div_id_%s'%deep)):
			content = DIV(content,_class=attr.get('div_class_%s'%deep),_id=attr.get('div_id_%s'%deep))
		elif attr.get('div_class',attr.get('div_id')):
			content = DIV(content,_class=attr.get('div_class'),_id=attr.get('div_id'))		
		return content

	def menu_gian_hang(self,folder,deep=1,**attr):
		table = self.define_folder()
		rows = self.db(table.parent==folder).select(orderby=table.display_order)
		if len(rows)==0: return ''
		content = UL(_class=attr.get('ul_class_%s'%deep,attr.get('ul_class')),_id=attr.get('ul_id_%s'%deep,attr.get('ul_id')))
		from plugin_app import get_short_string
		for row in rows:
			try:
				if (row.display_order==0):
					pass
				else:
					cls_li = attr.get('li_class_%s'%deep,attr.get('li_class'))
					cls_a = attr.get('a_class_%s'%deep,attr.get('a_class'))
					p = self.db(self.db.folder.name==current.request.args(0)).select().first()
					folder_name =''
					if p.parent==folder:
						folder_name = current.request.args(0)
					else:
						if p.parent:
							folder_name = p.parent.name
					if row.name == folder_name:
						cls_li = str(attr.get('li_class_%s'%deep,attr.get('li_class'))) +' folder_act'
						cls_a = str(attr.get('a_class_%s'%deep,attr.get('a_class'))) +' a_act'
					url = URL(r=current.request,c='portal',f='folder',args=[current.request.args(0),row.name],vars=dict(page='san_pham') )
					link = A(row.label,_href=url,_class=cls_a,_id=attr.get('a_id_%s'%deep,attr.get('a_id')))
					if attr.get('length'):
						link = A(get_short_string(row.label,attr.get('length')),_href=url,_class=cls_a,_id=attr.get('a_id_%s'%deep,attr.get('a_id')))
					content.append(LI(link,self.menu(row.id,deep+1,**attr),_class=cls_li,_id=attr.get('li_id_%s'%deep,attr.get('li_id'))))
			except Exception, e: print e
		if attr.get('div_class_%s'%deep,attr.get('div_id_%s'%deep)):
			content = DIV(content,_class=attr.get('div_class_%s'%deep),_id=attr.get('div_id_%s'%deep))
		elif attr.get('div_class',attr.get('div_id')):
			content = DIV(content,_class=attr.get('div_class'),_id=attr.get('div_id'))		
		return content
		
	def menu_table(self,folder,deep=1,**attr):
		table = self.define_folder()
		rows = self.db(table.parent==folder).select(orderby=table.display_order)
		if len(rows)==0: return ''
		content = UL(_class=attr.get('ul_class_%s'%deep,attr.get('ul_class')),_id=attr.get('ul_id_%s'%deep,attr.get('ul_id')))
		from plugin_app import get_short_string
		for row in rows:
			try:
				if (row.display_order==0):
					pass
				else:
					cls_li = attr.get('li_class_%s'%deep,attr.get('li_class'))
					cls_a = attr.get('a_class_%s'%deep,attr.get('a_class'))
					p = self.db(self.db.folder.name==current.request.args(0)).select().first()
					folder_name =''
					if p.parent==folder:
						folder_name = current.request.args(0)
					else:
						if p.parent:
							folder_name = p.parent.name
					if row.name == folder_name:
						cls_li = str(attr.get('li_class_%s'%deep,attr.get('li_class'))) +' folder_act'
						cls_a = str(attr.get('a_class_%s'%deep,attr.get('a_class'))) +' a_act'
					cls_li =str(cls_li) + ' menu-' + str(row.name)
					link = A(row.label,_href=self.url_folder(row.name),_class=cls_a,_id=attr.get('a_id_%s'%deep,attr.get('a_id')))
					if attr.get('length'):
						link = A(get_short_string(row.label,attr.get('length')),_href=self.url_folder(row.name),_class=cls_a,_id=attr.get('a_id_%s'%deep,attr.get('a_id')))
					content.append(LI(I(I(_class='icon'),_class='wr_icon'),link,self.menu(row.id,deep+1,**attr),_class=cls_li,_id=attr.get('li_id_%s'%deep,attr.get('li_id'))))
			except Exception, e: print e
		if attr.get('div_class_%s'%deep,attr.get('div_id_%s'%deep)):
			content = DIV(content,_class=attr.get('div_class_%s'%deep),_id=attr.get('div_id_%s'%deep))
		elif attr.get('div_class',attr.get('div_id')):
			content = DIV(content,_class=attr.get('div_class'),_id=attr.get('div_id'))		
		return content
		
		
	def render(self,boxname=None,id=None,context={}):
		try:
			import cStringIO
			self.define_box()
			box = self.box(id) if id else self.db(self.db.box.name==boxname).select().first()
			content = box.htmlcontent.replace('&quot;', "'").replace('&#39;', '"')	
			content = '%s%s'%(box.textcontent,content)
			if content == '':
				return A(IMG(_src=URL(r=current.request,c='static',f='plugin_box/avatar',args=[box.avatar]),_id=boxname,_class='ivinhcmsbox-img'),_href=box.link)
			try:
				settings = eval(box.setting.replace(chr(13),''))
				for key in settings.keys(): context[key] = settings[key]
			except: 
				pass
			content = current.response.render(cStringIO.StringIO(content), context)
			return XML(content)
		except Exception, e:
			return 'Box %s error: %s'%(boxname or id, e)
	
	def layout(self,tablename=None):
		tablename = tablename or self.get_table()
		dtable = self.define_dtable()
		row = self.db(dtable.name==tablename).select().first()
		return row.layout if row else None
	
	def get_table(self):
		return current.request.args(1)
	
	def get_link(self):
		return current.request.args(2)
		
	def get_row(self,tablename=None,link=None):
		tablename = tablename or self.get_table()
		link = link or self.get_link()
		table = self.define_table(tablename)
		return self.db(self.db[tablename].link==link).select().first()

	def content(self,tablename=None,link=None):
		tablename = tablename or self.get_table()
		row = self.get_row(tablename,link)
		if row:
			dcontent = DIV(_class='content_%s'%tablename)
			dcontent.append(SPAN(row.name,_class='name-%s'%tablename))
			dcontent.append(SPAN(row.description,_class='description-%s'%tablename))
			dcontent.append(SPAN(IMG(_src=self.get_avatar(tablename,row.avatar)),_class='avatar-%s'%tablename))
		else:
			dcontent = DIV('%s %s'(link,current.T('not found!'),_class='content_%s'%tablename))
		return dcontent

	def box_content(self,boxname,tablename=None,link=None,context={}):
		tablename = tablename or self.get_table()
		row = self.get_row(tablename,link)
		if row:
			context['row'] = row
			return self.render(boxname=boxname,context=context)
		else:
			return '%s %s'(link,current.T('not found!'))

	def box_folder(self,boxname,folder=None,context={}):
		row = self.get_rows(folder)
		context['rows'] = rows
		return self.render(boxname=boxname,context=context)
	
	def box(self,boxname,folder=None,page=None,length=None,tablename=None,link=None,context={}):
		if current.request.controller=='plugin_box':
			self.define_box()
			row = self.db(self.db.box.name==boxname).select().first()
			return IMG(_src=URL(r=current.request,c='static',f='plugin_box/avatar',args=[row.avatar]),_id=boxname,_class='ivinhcmsbox-img')
		if folder:
			context['rows'] = self.get_rows(folder,page,length)
		elif tablename:
			context['row'] = self.get_row(tablename,link)
		return DIV(self.render(boxname=boxname,context=context),_id=boxname,_class='ivinhcmsbox')

	def pagination(self,folder=None,page=None,length=None,count=None,tablename=None):
		PAGE = 1
		T = current.T
		request = current.request
		args = request.args
		folder = folder or self.get_folder(folder)
		length = length or self.get_length(folder)
		
		if len(args) < PAGE: return ''
		elif len(args) == PAGE: args.append('1.html')
		
		count = count or self.get_count(folder,tablename)
		if count<=length: return ''
		
		page = page or self.get_page()
		
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
			url = URL(r=request,args=args,vars=request.vars)
			ul.append(LI(A(T('First page'),'  ',_href=url)))
			ul.append(LI(m1))
		for x in xrange(p1,p2):
			args[PAGE]='%s.html'%x
			url = URL(r=request,args=args,vars=request.vars)
			ul.append(LI(A(x,'  ',_href=url),_class='active' if x == page else ''))
		if m2=='...':
			ul.append(LI(m2))
			args[PAGE]='%s.html'%pagecount
			url = URL(r=request,args=args,vars=request.vars)
			ul.append(LI(A(T('End page'),_href=url)))
		content.append(ul)
		return content			

	def metadc(self):
		try:
			request = current.request
			tablename = self.get_table()
			link = self.get_link()
			table = self.define_dcontent()
			row = self.db((table.link==link)&(table.dtable==tablename)).select().first()
			meta = ''' '''
			if not row: 
				if request.args(0)=='home':
					meta = '''
					<title>Sàn giao dịch thương mại điện tử tỉnh Hà Tĩnh</title>
					'''
				else:
					folder = self.define_table('folder')
					row = self.db(folder.name==request.args(0)).select().first()
					meta = '''
					<title> %s - Sàn giao dịch thương mại điện tử tỉnh Hà Tĩnh</title>
					'''%(row.label)
			else:
				indeitifier = 'http://%s/%s'%(request.env.http_host,request.env.path_info)
				source = 'http://%s'%(request.env.http_host)
				meta = '''
				<title> %s - Sàn giao dịch thương mại điện tử tỉnh Hà Tĩnh</title>
				<meta name="DC.Title" content="%s">
				<meta name="DC.Creator" content="%s">
				<meta name="DC.Date.Created" scheme="W3CDTF" content="%s" >
				<meta name="DC.Date.Modified" scheme="W3CDTF" content="%s" >
				<meta name="DC.Date.Valid" scheme="W3CDTF" content="%s" >
				<meta name="DC.Date.Issued" scheme="W3CDTF" content="%s" >
				<meta name= "DC.Publisher" content= "%s"> 
				<meta name="DC.Description" content="%s">
				<meta name="DC.Inditifier" content="%s">
				<meta name="DC.Languague" content="%s">
				<meta name= "DC.Source" content= "%s">
				<meta name="DC.Contributor" content="">
				<meta name="DC.Subject" content="%s">
				<meta name="DC.Coverage" content="Việt Nam">
				<meta name="DC.Type" content="Text">
				<meta name="DC.Format" content="text/html">''' %(row.name,row.name,row.creator,row.created_on,row.modified_on,row.publish_on,row.publish_on,row.publisher,row.description,indeitifier,row.languague,source,row.folder.label)
			return XML(meta)
		except Exception, e: 
			return ''

	def insert_read(self):
		foldername = current.request.args(0)
		tablename = current.request.args(1)
		link = current.request.args(2)
		if link:
			table = self.define_readcontent()
			clientip = current.request.client
			user_agent = str(current.request.user_agent())
			table.insert(foldername=foldername,tablename=tablename,link=link,clientip=clientip,user_agent=user_agent)
	
	def count_read_product(self,link=None):
		link = link or current.request.args(2)
		table = self.define_readcontent()
		return self.db(table.link==link).count()

	def top_read_product(self,top=10,foldername=None,tablename=None):
		db = self.db
		table = self.define_readcontent()
		count = table.link.count()
		limitby = (0,top)
		query = (table.foldername==foldername) if foldername else table.id>0
		if tablename:
			query&= (table.tablename==tablename)
		rows = db(query).select(table.link, count, groupby=table.link, limitby=limitby, orderby=~count)
		return rows
		
class CmsPublish(CmsModel):

	def get_link(self,table,link):
		i = 1
		tmp = link
		while self.db(table.link==tmp).count()>0:
			tmp = '%s-%s.html'%(link.split('.')[0],i) 
			i+=1
		return tmp
		
	def get_link_cms(self,table,link):
		i = 1
		tmp = link
		table = self.define_table(table)
		while self.db(table.link==tmp).count()>0:
			tmp = '%s-%s.html'%(link.split('.')[0],i) 
			i+=1
		return tmp
		
	def get_content(self,tablename,table_id):
		from bs4 import BeautifulSoup
		table = self.define_table(tablename)
		row = self.db[tablename](table_id)
		content = ''
		try:
			for field in table.fields:
				if table[field].type == 'string':
					content += '%s\n'%row[field]
				elif table[field].type == 'text':
					soup = BeautifulSoup(row[field])
					content = '%s\n%s'%(content,soup.text.encode('utf-8'))
		except Exception, e:
			pass
		return content
		
	def publish(self,tablename,table_id,publish_on,expired_on):
		table = self.define_table(tablename)
		row = self.db[tablename](table_id)
		link = row.name.replace('đ','d')
		link = '%s.html'%IS_SLUG.urlify(link)
		link = self.get_link(table,link)
		self.db(table.id==table_id).update(link=link)
		dcontent = self.define_dcontent()
		content = self.get_content(tablename,table_id)
		try:
			auth = current.globalenv['auth']
			creator = '%s %s' % (auth.user.last_name, auth.user.first_name)
			publisher = auth.db.auth_group(auth.auth_org).role
		except:
			creator = ''
			publisher = ''
		dcontent.insert(folder=row.folder,dtable=tablename,table_id=table_id,link=link,name=row.name,avatar=row.avatar,description=row.description,publish_on=publish_on,expired_on=expired_on,textcontent=content,publisher=publisher,creator=creator)	
		return ''
	
	def unpublish(self,tablename,table_id):
		table = self.define_table(tablename)
		row = self.db[tablename](table_id)
		dcontent = self.define_dcontent()
		self.db((dcontent.dtable==tablename)&(dcontent.link==row.link)).delete()
		self.db(table.id==table_id).update(link=None)
		return ''
		
	def update(self,tablename,table_id):
		table = self.define_table(tablename)
		row = self.db[tablename](table_id)
		link = row.name.replace('đ','d')
		link = '%s.html'%IS_SLUG.urlify(link)
		link = self.get_link(table,link)
		self.db(table.id==table_id).update(link=link)
		dcontent = self.define_dcontent()
		content = self.get_content(tablename,table_id)
		self.db((dcontent.dtable==tablename)&(dcontent.link==row.link)).update(folder=row.folder,link=link,name=row.name,avatar=row.avatar,description=row.description,textcontent=content,modified_on=current.request.now)	
		return ''
	
	def delete(self,tablename,table_id):
		table = self.define_table(tablename)
		row = self.db[tablename](table_id)
		dcontent = self.define_dcontent()
		self.db((dcontent.dtable==tablename)&(dcontent.link==row.link)).delete()
		self.db(table.id==table_id).delete()
		return ''

		
		
class CmsCrud(CmsModel):

	def widget_layout(self, field, value):
		for root, dirs, files in os.walk(current.request.folder+'/views/layout'):
			pass
		op = [OPTION(file,_value=file,_selected=(value==file)) for file in files]
		widget = SELECT(op,_name=field.name,_id=field._tablename+'_'+field.name)
		return widget
		
	def folder(self):	
		from sqlhtml import SQLFORM
		table = self.define_folder()
		table.parent.widget = self.widget_folder
		table.layout.widget = self.widget_layout
		return table
		
	def dtable(self):	
		from sqlhtml import SQLFORM
		class VALIDATOR_DB_KEYWORD(object):
			def __init__(self, db, error_message="SOMETHING WRONG"):
				self.error_message = error_message
				self.db = db
			def __call__(self, value):
				error = None
				try:
					table = self.db.define_table(value,Field('testfield','string'),migrate=True)
				except Exception, e:
					error = e
				return (value, error)
		table = self.define_dtable()
		table.name.requires = [VALIDATOR_DB_KEYWORD(self.db),IS_NOT_IN_DB(self.db,table.name)]
		tablefield = self.tablefield()
		tablefield.dtable.widget = SQLFORM.widgets.options.widget
		table.layout.widget = self.widget_layout
		return table

	def dfield(self):	
		from sqlhtml import SQLFORM
		def widget_type(field, value):
			list_types = ['blob','boolean','date','datetime','double','integer','list:integer','list:reference','list:string','reference','string','text','time','upload']			
			op = [OPTION(name,_value=name,_selected=str(value).startswith(name)) for name in list_types]
			url = URL(r=current.request,c='plugin_cms',f='widget_type',vars=dict(value=value))
			ajax = "ajax('%s',['fieldtype'],'widget_type')"%(url)
			tables = LOAD(url=url) if value else ''
			widget = SPAN(SELECT(op,_name='fieldtype',_id="fieldtype",_onchange=ajax),DIV(tables,_id='widget_type'))
			widget.append(INPUT(_type='hidden',_value=value,_name=field.name,_id=field._tablename+'_'+field.name))
			return widget
			
		class VALIDATOR_DB_KEYWORD(object):
			def __init__(self, db, error_message="SOMETHING WRONG"):
				self.error_message = error_message
				self.db = db
			def __call__(self, value):
				error = None
				try:
					table = self.db.define_table('table_check_keyword',Field(value,'string'),migrate=True)
					#self.db.table_check_keyword.drop()
				except Exception, e:
					error = e
				return (value, error)
		
		table = self.define_dfield()
		table.ftype.widget = widget_type
		table.name.requires = [VALIDATOR_DB_KEYWORD(self.db),IS_NOT_IN_DB(self.db,table.name)]
		return table
		
	def tablefield(self):	
		from sqlhtml import SQLFORM
		def widget_field(field, value):
			ftype = self.db.dfield(value).ftype if self.db.dfield(value) else 'string'
			list_types = ['blob','boolean','date','datetime','double','integer','list:integer','list:reference','list:string','reference','string','text','time','upload']			
			url = URL(r=current.request,c='plugin_cms',f='widget_field',vars=dict(value=value or 0,ftype=ftype))
			ajax = "ajax('%s',['fieldtype'],'widget_field')"%(url)
			if len(ftype.split(' '))==3: ftype = ftype.split(' ')[0] + ' ' + ftype.split(' ')[1]
			rows = self.db(self.db.dfield.ftype.startswith(ftype)).select()
			op = [OPTION(row.name,_value=row.id,_selected=(row.id==value)) for row in rows]
			dfield = SELECT(op,_name='dfield',_id='tablefield_dfield')
			
			op = [OPTION(name,_value=name,_selected=ftype.startswith(name)) for name in list_types]			
			widget = SPAN(SELECT(op,_name='fieldtype',_id="fieldtype",_onchange=ajax),DIV(dfield,_id='widget_field'))
			return widget

		def widget_table(field, value):
			if not value: return SQLFORM.widgets.options.widget(field,value)
			self.db.tablefield.dtable.default = value
			rows = self.db(self.db.tablefield.dtable==value).select(orderby=self.db.tablefield.display_order)
			widget = DIV()
			for row in rows: 
				widget.append(B(row.dfield.name))
				widget.append('(%s) '%(row.dfield.ftype))
			return widget
			
		table = self.define_tablefield()
		table.dfield.widget = widget_field
		table.dtable.widget = widget_table
		return table
				
	

class CmsTable(CmsModel):

	def get_table(self):
		tablename = current.request.args(0)
		return tablename if self.define_table(tablename) else None

	def get_reference(self):
		return current.request.vars.reference

	def get_reference_id(self):
		return current.request.vars.reference_id
		
	def get_vars(self):	
		vars = {}
		reference = self.get_reference()
		if reference:
			vars['reference'] = reference
			reference_id = self.get_reference_id()
			if reference_id:
				var['reference']==reference_id
		return vars
		
	def get_page(self):
		try: 
			page = int(current.request.args[-1].split('.')[0])
		except: 
			page = 1
		return page
		
	def get_length(self,tablename,length=10):
		return length

	def get_order(self,tablename,field=None,asc=True):
		field = field or current.request.vars.orderby
		asc = asc or current.request.vars.asc
		if (asc=='False'): asc = False
		if field:
			return self.db[tablename][field] if asc else ~self.db[tablename][field]
		return None
		
	def get_query(self,tablename):	
		query = (self.db[tablename].id>0)
		reference = self.get_reference()
		if reference:
			reference_id = self.get_reference_id()
			if reference_id:
				query &= (self.db[tablename][reference]==reference_id)
		return query
		
	def get_count(self,tablename):
		query = self.get_query(tablename)
		return self.db(query).count()
		
	def get_rows(self,tablename,page=None,length=None,orderby=None,query=None):
		query = self.get_query(tablename)&query if query else self.get_query(tablename)
		page = page or self.get_page()
		length = length or self.get_length(tablename)
		p1 = (page-1)*length
		p2 = page*length
		orderby = orderby or self.get_order(tablename)
		rows = self.db(query).select(limitby=(p1,p2),orderby=orderby)
		return rows

	def toolbars(self,tablename,reference=None,reference_id=None):
		from plugin_app import ColorBox
		vars = None
		reference = reference or self.get_reference()
		if reference:
			reference_id = reference_id or self.get_reference_id()
			if reference_id:
				vars = dict(reference=reference,reference_id=reference_id)
		content = DIV(_id='toolbar-%s'%tablename,_css='toolbar toolbar-%s'%tablename)
		f = 'edit'
		url = URL(r=current.request,c='plugin_cms',f=f,args=[tablename],vars=vars,extension='htm')
		ajax = "ajax('%s', ['%s'], '%s')"%(url,tablename,tablename)
		update = URL(r=current.request,c='plugin_cms',f='explorer.load',args=[tablename],vars=vars,extension='htm')
		button = SPAN(ColorBox(caption=f.capitalize(),source=url,width='80%',height='80%',input_name=tablename,url=update,target='%s_table'%tablename),_css='button_table')	
		content.append(button)
		f = 'delete'
		url = URL(r=current.request,c='plugin_cms',f=f,args=[tablename],vars=vars,extension='load')
		ajax = "ajax('%s', ['%s'], '%s_table')"%(url,tablename,tablename)
		button = SPAN(f.capitalize(),_onclick=ajax,_css='delete button_table',_id='delete_id')	
		button = SPAN(f.capitalize(),_css='delete button_table',_id='%s_id'%f)	
		content.append(button)
		script = SCRIPT('''
			$(document).ready(function() {
				$('#%s_id').click(function () {
					if ($("#%s_table input:checked").length == 0) {
						return 0;
					}
					var r=confirm("Chấp nhận %s?");
					if (r==false) {
						//$('input:checkbox').attr('checked',false);
						return 0;
					}
					var data = $.map($("#%s_table input:checked"), function(elem, idx) {return "&"+$(elem).attr("name")+"="+ $(elem).val();}).join('');	
					$.ajax({
						url: "%s",
						type: "GET",
						data: data,
						cache: false,
						success: function (html) {
							if (html!='') $('#%s_table').html(html);
						}
					});				
				});
			});'''%(f,tablename,current.T(f),tablename,URL(r=current.request,c='plugin_cms',f='delete.load',args=[tablename],vars=vars),tablename))
		content.append(script)	
		return content
		
	def pagination(self,tablename,page=None,length=None,vars=None):
		T = current.T
		request = current.request
		page = page or self.get_page()
		pagecount = self.get_count(tablename)
		length = length or self.get_length(tablename)
		if page == 0: return ''
		if pagecount <= length: return ''
		if length>0:
			tmp = int(pagecount/length)
			if pagecount > tmp*length: pagecount = tmp+1
			else: pagecount = tmp
		content = DIV(_id='page',_class='pagination')
		ul = UL()
		(p1, m1) = (page - 5,'...') if page > 5 else (1, '')
		(p2, m2) = (page + 5,'...') if page + 5 < pagecount else (pagecount+1, '')
		if (p2 < 11) & (pagecount >10): p2 = 11
		vars == vars or self.get_vars()
		div = '%s_pagination'%tablename
		if m1=='...':
			args = [tablename,1]
			url = URL(r=request,c='plugin_cms',f='explorer',vars=vars,args=args,extension='load')
			ajax="ajax('%s', [], '%s')"%(url,div)
			ul.append(LI(A(T('First'),'  ',_href='#',_onclick=ajax)))
			ul.append(LI(m1))
		for x in xrange(p1,p2):
			args = [tablename,x]
			url = URL(r=request,c='plugin_cms',f='explorer',vars=vars,args=args,extension='load')
			ajax="ajax('%s', [], '%s')"%(url,div)
			ul.append(LI(A(x,'  ',_href='#',_onclick=ajax,_class='selected' if x == page else '')))
		if m2=='...':
			args = [tablename,pagecount]
			ul.append(LI(m2))
			url = URL(r=request,c='plugin_cms',f='explorer',vars=vars,args=args,extension='load')
			ajax="ajax('%s', [], '%s')"%(url,div)
			ul.append(LI(A(T('End'),_href='#',_onclick=ajax)))
		content.append(ul)
		return content	

	def view(self,tablename=None,page=None,reference=None,reference_id=None):
		try:
			import cStringIO
			tablename = tablename or self.get_table()
			table = self.define_dtable()
			r = self.db(table.name==tablename).select().first()
			if not self.define_table(tablename): return ''
			query = None
			vars = None
			reference = reference or self.get_reference()
			if reference:
				reference_id = reference_id or self.get_reference_id()
				if reference_id:
					query = (self.db[tablename][reference]==reference_id)
					vars = dict(reference=reference,reference_id=reference_id)
			rows = self.get_rows(tablename,query=query,page=page)
			pagecount = len(rows)			
			
			# if pagecount>1:
				# context = dict(rows=rows)
				# content = r.display_rows or ''
			# elif pagecount==1:
				# context = dict(row=rows[0])
				# content = r.display_row or ''
			# else:
				# return ''
			# content = current.response.render(cStringIO.StringIO(content), context)

			fields = []
			for field in self.db[tablename].fields:
				if (field!='id')&(field!=reference):
					if (self.db[tablename][field].writable==True)&(self.db[tablename][field].readable==True):
						fields.append(field)
			
			table = TABLE(_id='object_ul',_class='table table-striped defview')
			tr = TR(TH('#',_style="width: 30px;text-align: center;"),TH('STT',_style="width: 30px;text-align: center;"))
			for field in fields:
				tr.append(TH(current.T(field.capitalize())))
			table.append(tr)
			i = 1
			for row in rows:
				tr = TR(TD(INPUT(_type='checkbox',_name=tablename,_value=row.id)),TD(i))
				for field in fields:
					tr.append(TD(row[field]))
				table.append(tr)
				i+=1
			if current.request.extension=='load': return table
			
			content = DIV(table,_id='%s_table'%tablename)
			content = DIV(content,self.pagination(tablename,page=page,vars=vars),_id='%s_pagination'%tablename)
			content = DIV(self.toolbars(tablename,reference,reference_id),content,_id=tablename)
			return content
		except Exception, e:
			return e				