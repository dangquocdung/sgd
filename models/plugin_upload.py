# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 28/07/2014
###################################################

if request.controller in ['plugin_upload']:
	from plugin_process import ProcessModel
	from plugin_cms import CmsModel
	auth = ProcessModel().auth
	cms = CmsModel()
	db = cms.db
