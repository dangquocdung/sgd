# -*- coding: utf-8 -*-
###################################################
# This content was developed by Anhnt
# Version 0.1 Date: 24/03/2015
###################################################
from gluon import current, LOAD
from html import *
from gluon.dal import Field
from validators import IS_EMPTY_OR, IS_NOT_EMPTY, IS_IMAGE, IS_NULL_OR, IS_IN_DB, IS_IN_SET, IS_NOT_IN_DB, IS_SLUG
import os

#####################################################################
from sqlhtml import SQLFORM

def edit_tin_tuc(id,cms,folder_id_ivinh):
	request =  current.request
	T =  current.T
	from plugin_ckeditor import CKEditor
	tin_tuc = cms.define_table('tintuc')
	tin_tuc.folder.default=folder_id_ivinh
	tin_tuc.folder.writable=False
	tin_tuc.folder.readable=False
	tin_tuc.htmlcontent.widget=CKEditor(cms.db).widget	
	form=SQLFORM(tin_tuc,id)
	ajax = "ajax('%s', [''], 'news_detail')"%(URL(r=current.request,c='plugin_app',f='act_delete',args=[request.args(0)],vars=dict(table_name='tintuc',table_id=id )))
	form[0][-1] = TR(TD(INPUT(_type='submit',_value=T('Submit')),INPUT(_type='button',_value=T('Xóa bài viết'),_onclick=ajax,_class='btn btn-danger'),_colspan="3"),_class='act_ivinh')
	if form.process().accepted:
		current.response.flash = T('Cập nhật thành công.')
	return form
	
def view_san_pham(id,cms,folder_id_ivinh):
	request =  current.request
	T =  current.T
	div = DIV(_class='col-md-12',_id='news_detail')
	name = request.args(0)
	from plugin_ckeditor import CKEditor
	san_pham = cms.define_table('san_pham')
	# san_pham.folder.default=folder_id_ivinh
	# san_pham.folder.writable=False
	# san_pham.folder.readable=False
	from plugin_app import widget_danh_muc_san_pham
	san_pham.folder.widget=widget_danh_muc_san_pham
	san_pham.r_folder.writable=False
	san_pham.r_folder.readable=False
	san_pham.htmlcontent.widget=CKEditor(cms.db).widget	
	
	form=SQLFORM(san_pham,id)
	ajax = "ajax('%s', [''], 'news_detail')"%(URL(r=current.request,c='plugin_app',f='act_delete',args=[request.args(0)],vars=dict(table_name='san_pham',table_id=id )))
	form[0][-1] = TR(TD(INPUT(_type='submit',_value=T('Submit')),INPUT(_type='button',_value=T('Xóa sản phẩm'),_onclick=ajax,_class='btn btn-danger'),_colspan="3"),_class='act_ivinh')
	if form.process().accepted:
		dcontent = cms.define_dcontent()
		link = cms.db.san_pham[request.vars.id].link
		id_d = cms.db((dcontent.dtable=='san_pham')&(dcontent.link==link)).update(name=request.vars.name,folder=request.vars.folder,avatar=request.vars.avatar,description=request.vars.description)
		current.response.flash = T('Cập nhật thành công.')
	div.append(form)
	return div
	