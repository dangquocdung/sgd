# -*- coding: utf-8 -*-
###################################################
# This file was developed by Anhnt
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 12/01/2015
###################################################
from sqlhtml import SQLFORM
FOLDER_PARENT = 246

def index():
	return dict(content='')
	
def linh_vuc():
	from plugin_folder import Folder
	cms.define_folder()
	folder = Folder(cms.db,auth,parent=FOLDER_PARENT)
	content = folder.display_tree()
	return dict(content=content)

def loca_ads():
	vi_tri = cms.define_table('vi_tri')
	form=SQLFORM.grid(vi_tri)
	div = DIV(_class="panel panel-default")
	div.append(DIV(T('Vị trí quảng cáo bằng hình ảnh'),_class="panel-heading"))
	div.append(DIV(form, _class='panel-body'))
	response.view = 'plugin_manager/index.html'
	return dict(content=div)	

def type_ads():
	ads_product_type = cms.define_table('ads_product_type')
	form=SQLFORM.grid(ads_product_type)
	div = DIV(_class="panel panel-default")
	div.append(DIV(T('Kiểu quảng cáo sản phẩm'),_class="panel-heading"))
	div.append(DIV(form, _class='panel-body'))
	response.view = 'plugin_manager/index.html'
	return dict(content=div)	
	
	
def contact():
	id= 90
	from plugin_ckeditor import CKEditor
	box = cms.define_box()
	box.htmlcontent.widget=CKEditor(cms.db).widget	
	
	box.name.writable=False
	
	box.id.writable=False
	box.id.readable=False
	
	box.boxtype.writable=False
	box.boxtype.readable=False
	
	box.avatar.writable=False
	box.avatar.readable=False
	
	box.link.writable=False
	box.link.readable=False
	
	box.setting.writable=False
	box.setting.readable=False
	
	box.textcontent.writable=False
	box.textcontent.readable=False
	
	form=SQLFORM(box,id)
	div = DIV(_class="panel panel-default")
	div.append(DIV(T('Thông tin hỗ trợ trực tuyến'),_class="panel-heading"))
	div.append(DIV(form, _class='panel-body'))
	if form.process().accepted:
		response.flash = T('Cập nhật thành công.')
	response.view = 'plugin_manager/index.html'
	return dict(content=div)

	
def form():
	try:
		from plugin_folder import FolderCrud
		folder = FolderCrud(cms.db,auth,parent=FOLDER_PARENT)	
		id = request.vars.folder
		form = folder.form(id)

		from sqlhtml import SQLFORM
		table = folder.db[folder.tablename]
		table.parent.widget = folder.widget_folder
		
		table.parent.label = 'Danh mục cha'
		table.label.label = 'Tên danh mục'
		table.name.label = 'Mã danh mục'
		table.label.widget = folder.widget_label
		table.description.label = 'Mô tả'
		table.setting.readable = False
		table.setting.writable = False
		
		table.layout.default = 'page_san_pham.html'
		# table.layout.readable = False
		# table.layout.writable = False
		
		table.display_order.readable = False
		table.display_order.writable = False
		
		form = SQLFORM(table,id,showid=False,buttons=[])
		
		ajax = "ajax('%s',['name','label','parent','description','display_order','layout'],'')"%URL(f='update',args=[id] if id else None)
		ajax_d = "ajax('%s',[],'')"%URL(f='delete',args=[id] if id else None)
		div = DIV(_class='wr_act_form')
		div.append(A(SPAN(_class='glyphicon glyphicon-ok'),T('Submit'),_class='btn btn-primary',_onclick=ajax))
		if id:
			div.append(A(SPAN(_class='glyphicon glyphicon-trash'),T('Delete'),_class='btn btn-danger',_onclick=ajax_d))
		form.append(div)
		return form	
	except Exception, e:
		return e
	
def update():
	try:
		from plugin_folder import FolderCrud
		folder = FolderCrud(cms.db,auth,parent=FOLDER_PARENT)
		id = request.args(0)
		folder.update(id,request.vars)
		session.flash = T('Cập nhật thành công')
	except Exception, e:
		print e
	redirect(URL(f='index'),client_side=True)
	
def delete():
	try:
		from plugin_folder import FolderCrud
		folder = FolderCrud(cms.db,auth,parent=FOLDER_PARENT)
		id = request.args(0)
		folder.delete(id)
		session.flash = T('Xóa thành công')
	except Exception, e:
		print e
	redirect(URL(f='index'),client_side=True)	
	
	