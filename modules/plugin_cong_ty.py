###################################################
# This file was developed by Anhnt
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 28/07/2014
###################################################
from gluon import current, LOAD
from html import *
from gluon.dal import Field
from validators import IS_EMPTY_OR, IS_NOT_EMPTY, IS_IMAGE, IS_NULL_OR, IS_IN_DB, IS_IN_SET, IS_NOT_IN_DB, IS_SLUG
import os

def add_cong_ty(folder):
	from sqlhtml import SQLFORM
   	from plugin_ckeditor import CKEditor
   	from plugin_cms import CmsModel
	T = current.T
	cms = CmsModel()
	db = cms.db
	div = DIV(_class='col-md-12')
	div.append(H2(SPAN(T('Thông tin chi tiết')),_class='title_name',_id='title_page'))
	cong_ty_edit = cms.define_table('cong_ty')
	cong_ty_id = db(cong_ty_edit.folder==folder).select().first()
	cong_ty_edit.folder.writable=False
	cong_ty_edit.folder.readable=False

	cong_ty_edit.start_time.writable=False
	cong_ty_edit.start_time.readable=False

	cong_ty_edit.danh_gia.writable=False
	cong_ty_edit.danh_gia.readable=False

	cong_ty_edit.is_maps.writable=False
	cong_ty_edit.is_maps.readable=False

	from plugin_app import widget_danh_muc
	cong_ty_edit.linh_vuc.widget=widget_danh_muc
	form=SQLFORM(cong_ty_edit,cong_ty_id)
	if form.process().accepted:
		current.response.flash = T("Cập nhật thành công!")
	div.append(form)
	return form
