# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 27/02/2014
###################################################

from plugin_cms import Cms
cms = Cms()

from plugin_ckeditor import CKEditor
CKEditor(cms.db).define_tables()

if request.controller in ['plugin_cms','portal','plugin_app','plugin_box','plugin_sgd','plugin_folder','plugin_manager','plugin_report']:
	from plugin_process import ProcessModel
	db = cms.db
	cms.define_dcontent(False)
	cms.define_box(False)
	cms.define_folder(False)
	cms.define_rtable(False)
	auth = ProcessModel().auth
	folder_id_gian_hang = ''
	if auth.user_id:
		folder = cms.define_folder()
		db_auth = ProcessModel().db
		rows = db_auth(db_auth.auth_membership.user_id==auth.user_id).select()
		list_group = []
		for r in rows:
			list_group.append(r.group_id)
		
		if 3 in list_group:
			# from plugin_cms import CmsFolder
			# folder_id = CmsFolder().get_folder(request.args(0))
			folder_id = db(folder.name==request.args(0)).select().first()
		else:
			folder_id = db(folder.created_by==auth.user_id).select().first()
		if folder_id:
			folder_id_gian_hang = folder_id
		# print folder_id_gian_hang,9999
		
	