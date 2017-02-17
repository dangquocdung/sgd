# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 15/03/2014
###################################################


@auth.requires_login()	
def index():
	from plugin_cms import CmsModel
	ul = UL()
	for table in ['folder','dtable','rtable','dfield','tablefield']:
		ul.append(LI(A(T(table),_href=URL(f=table)),_class='table_%s'%table,_id='table_%s'%table))
	ul.append(LI(A(T('dcontent'),_href=URL(f='manage',args=['dcontent'])),_class='table_dcontent',_id='table_dcontent'))
	ul.append(LI(A(T('box'),_href=URL(f='manage',args=['box'])),_class='table_box',_id='table_box'))
	ul.append(LI(A(T('rtable'),_href=URL(f='manage',args=['rtable'])),_class='table_box',_id='table_box'))
	content = DIV(ul,_class='cmsindex',_id='cmsindex')
	cms = CmsModel()
	table = cms.define_dtable()
	rows = cms.db(table).select(orderby=table.display_order)
	ul1 = UL(_class='table_data')
	ul2 = UL(_class='table_publish')
	for row in rows:
		li = LI(A(T(row.name),_href=URL(f='manage',args=[row.name])),_class='table_%s'%row.name,_id='table_%s'%row.name)
		if row.publish: ul2.append(li)
		else: ul1.append(li)
	content.append(ul1)	
	content.append(ul2)	
	response.view = 'plugin_cms/content.html'	
	return dict(content=content)
	
@auth.requires_login()	
def menu():
	from plugin_cms import CmsModel
	ul = UL(_class='sf-menu')
	for table in ['folder','dtable','rtable','dfield','tablefield']:
		ul.append(LI(A(T(table),_href=URL(f=table)),_class='table_%s'%table,_id='table_%s'%table))
	ul.append(LI(A(T('dcontent'),_href=URL(f='manage',args=['dcontent'])),_class='table_dcontent',_id='table_dcontent'))
	ul.append(LI(A(T('box'),_href=URL(f='manage',args=['box'])),_class='table_box',_id='table_box'))
	ul.append(LI(A(T('rtable'),_href=URL(f='manage',args=['rtable'])),_class='table_box',_id='table_box'))
	content = DIV(ul,_class='cmsindex',_id='cmsindex')
	cms = CmsModel()
	table = cms.define_dtable()
	rows = cms.db(table).select(orderby=table.display_order)
	ul1 = UL(_class='table_data sf-menu')
	ul2 = UL(_class='table_publish sf-menu')
	for row in rows:
		li = LI(A(T(row.name),_href=URL(f='manage',args=[row.name])),_class='table_%s'%row.name,_id='table_%s'%row.name)
		if row.publish: ul2.append(li)
		else: ul1.append(li)
	content.append(ul1)	
	content.append(ul2)	
	
	return content

@auth.requires_login()	
def explorer():
	from plugin_cms import CmsTable
	cms = CmsTable()
	content = cms.view()
	response.view = 'plugin_cms/content.%s'%request.extension
	return dict(content=content)	
	
@auth.requires_login()	
def edit():
	from plugin_cms import CmsTable
	cms = CmsTable()
	tablename = cms.get_table()
	vars = {}
	if request.vars.reference:
		if request.vars.reference_id:
			cms.db[tablename][request.vars.reference].writable = False
			cms.db[tablename][request.vars.reference].default = request.vars.reference_id
			vars['reference']=request.vars.reference
			vars['reference_id']=request.vars.reference_id
	table_id = request.args(1)
	if not table_id:
		if tablename in request.vars.keys():
			table_id = request.vars[tablename]
			if isinstance(table_id,list): table_id = table_id[0]
		
	form = SQLFORM(cms.db[tablename],table_id)
	if form.process().accepted:
		if not request.vars.new_id: 
			vars['new_id']=form.vars.id
			redirect(URL(args=[tablename],vars=vars))
		if table_id: 
			redirect(URL(args=[tablename],vars=vars))
	content = form
	if request.vars.new_id:
		vars['new_id'] = request.vars.new_id
		fields = []
		for field in cms.db[tablename].fields:
			if (cms.db[tablename][field].writable==True)&(cms.db[tablename][field].readable==True):
				fields.append(field)
		rows = cms.db(cms.db[tablename].id>=request.vars.new_id).select()
		table = TABLE()
		tr = TR(TD(),TD())
		for field in fields:
			tr.append(TD(T(field.capitalize())))
		table.append(tr)
		for row in rows:
			tr = TR()
			tr.append(TD(A(SPAN(T('Edit'),_css='edit'),_href=URL(args=[tablename,row.id],vars=vars))))
			tr.append(TD(A(SPAN(T('Delete'),_css='delete'),_href=URL(f='delete_create',args=[tablename,row.id],vars=vars))))
			for field in fields:
				tr.append(TD(row[field]))
			table.append(tr)
		content = DIV(form,table)	
	response.view = 'plugin_cms/content.%s'%request.extension
	return dict(content=content)	
	
@auth.requires_login()	
def delete_create():
	from plugin_cms import CmsTable
	cms = CmsTable()
	tablename = cms.get_table()	
	cms.db(cms.db[tablename].id==request.args(1)).delete()
	redirect(URL(f='create',args=[tablename],vars=request.vars))
	
@auth.requires_login()	
def delete():
	from plugin_cms import CmsTable
	cms = CmsTable()
	tablename = cms.get_table()
	if tablename in request.vars.keys():
		list_id = request.vars[tablename]
		if isinstance(list_id,str):
			list_id = [list_id]
		list_id = [int(id) for id in list_id]	
		cms.db(cms.db[tablename].id.belongs(list_id)).delete()
	return cms.view(tablename)
	
@auth.requires_login()
def manage():
	table = request.args(0)
	from plugin_cms import CmsModel
	cms = CmsModel()
	cms.define_table(table,True)
	if table not in cms.db.tables: redirect(URL(f='index'))
	content = SQLFORM.grid(cms.db[table],args=request.args[:1])
	response.view = 'plugin_cms/content.html'	
	return dict(content=content)
	
def page():
	from plugin_cms import CmsFolder
	content = CmsFolder().html()
	return dict(content=content)
		
def read():
	from plugin_cms import CmsContent
	content = CmsContent().html(request.args(1),request.args(2))
	return dict(content=content)	

@auth.requires_login()	
def folder():
	from plugin_cms import CmsCrud
	cms = CmsCrud()
	table = cms.folder()
	form = SQLFORM.grid(table)
	response.view = 'plugin_cms/content.html'	
	return dict(content=form)

@auth.requires_login()
def dtable():
	from plugin_cms import CmsCrud
	cms = CmsCrud()

	def ondelete(table,id):
		ftable = cms.define_tablefield()
		cms.db(ftable.dtable==id).delete()
		
	table = cms.dtable()
	form = SQLFORM.smartgrid(table,linked_tables=['tablefield'],ondelete=ondelete)
	response.view = 'plugin_cms/content.html'	
	return dict(content=form)
	
@auth.requires_login()
def dfield():
	from plugin_cms import CmsCrud
	cms = CmsCrud()
	
	def onupdate(form):
		cms.define_table(form.vars.name,True)
		table = cms.define_tablefield()
		rows = cms.db(table.dfield==form.vars.id).select(table.dtable,distinct=True)
		for row in rows:
			cms.define_table(row.dtable.name,True)
			
	def ondelete(table,id):
		table = cms.define_tablefield()
		rows = cms.db(table.dfield==id).select(table.dtable,distinct=True)
		for row in rows:
			cms.define_table(row.dtable.name,True)
		cms.db(table.dfield==id).delete()
		
	table = cms.dfield()
	form = SQLFORM.grid(table,onupdate=onupdate,ondelete=ondelete)
	response.view = 'plugin_cms/content.html'	
	return dict(content=form)
	
@auth.requires_login()
def tablefield():
	from plugin_cms import CmsCrud
	cms = CmsCrud()
	table = cms.tablefield()
	form = SQLFORM.grid(table)
	response.view = 'plugin_cms/content.html'	
	return dict(content=form)

@auth.requires_login()	
def widget_type():
	if ((not request.vars.fieldtype)&('reference' in request.vars.value))|('reference' in str(request.vars.fieldtype)): 
		from plugin_cms import CmsModel
		cms = CmsModel()
		table = cms.define_dtable()
		rows = cms.db(table).select(orderby=table.name)
		tables = cms.db.tables
		if 'folder' not in cms.db.tables: tables.append('folder')
		for row in rows:
			if row.name not in cms.db.tables: tables.append(row.name)
		tables.sort()	
		op = [OPTION(T(table),_value=table,_selected=(request.vars.value.endswith(table))) for table in tables]
		widget = SELECT(op,_name='tablename',_id="tablename")
		script = SCRIPT('''$('#tablename').change(function() {document.getElementById("dfield_ftype").value = document.getElementById("fieldtype").value+' '+$(this).val(); });''')	
		return SPAN(widget,script)
	else:
		script = SCRIPT('''document.getElementById("dfield_ftype").value = document.getElementById("fieldtype").value;''')	
		return script

@auth.requires_login()		
def widget_field():
	from plugin_cms import CmsModel
	cms = CmsModel()
	table = cms.define_dfield()
	ftype = request.vars.fieldtype or request.vars.ftype
	if len(ftype.split(' '))==3: ftype = ftype.split(' ')[0] + ' ' + ftype.split(' ')[1]
	rows = cms.db(table.ftype.startswith(ftype)).select(orderby=table.name)
	op = [OPTION(row.name,_value=row.id,_selected=(row.id==int(request.vars.value))) for row in rows]
	widget = SELECT(op,_name='dfield',_id='tablefield_dfield')
	return widget
		
		
##################################

from gluon.tools import Service
service = Service()
def call():
	session.forget()
	return service()
	
@service.xmlrpc
def giay_moi_event():
	try:
		content = UL(_id='nt-title')
		from plugin_cms import CmsModel
		from plugin_cms import CmsFolder
		cms = CmsModel()
		cf = CmsFolder()
		cms.define_table('documents')
		date_now=request.now.date()
		rows = cf.get_content(tablename='documents',folder='giay-moi',orderby=cms.db.documents.ngay_ky,query=((cms.db.documents.ngay_ky<=date_now)&(cms.db.documents.ngay_het_han>date_now)) )
		for row in rows:
			content.append(LI(A('GM '+ str(row.name)+': ' + str(row.description),_href=URL(a='vbvq',c='portal',f='read',args=[row.folder.name,'documents',row.link] ) ) ))
		content = str(content)
		return content
	except Exception, e:
			return e
