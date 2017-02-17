# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 27/02/2014
###################################################

if request.controller=='plugin_auth':
	from plugin_process import ProcessModel
	from plugin_cms import CmsModel
	process = ProcessModel()
	db = process.db
	auth = process.auth
	cms = CmsModel()
	