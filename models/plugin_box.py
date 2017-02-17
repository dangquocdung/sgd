# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 27/02/2014
###################################################

if request.controller =='plugin_box':
	from plugin_cms import CmsModel
	cms = CmsModel()
	db = cms.db
	cms.define_box()
