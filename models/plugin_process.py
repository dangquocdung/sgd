# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 27/02/2014
###################################################

if request.controller in ['plugin_process','plugin_comment']:
	from plugin_process import ProcessModel
	from plugin_cms import CmsModel
	processmodel = ProcessModel()
	processmodel.define_process()
	processmodel.define_procedures()
	processmodel.define_process_log()
	processmodel.define_process_lock()
	auth = processmodel.auth
	db = processmodel.db
	cms = CmsModel()
	
elif request.controller in ['appadmin','plugin_tools']:
	from plugin_process import ProcessModel
	from plugin_cms import CmsModel
	processmodel = ProcessModel()
	processmodel.define_process(False)
	processmodel.define_procedures(False)
	processmodel.define_process_log(False)
	processmodel.define_process_lock(False)
	auth = processmodel.auth
	db = processmodel.db
	cms = CmsModel()
	cmsdb = cms.db
	cms.define_tables(False)
	# cms.define_table('san_pham',True)
	# cms.db.san_pham.truncate()

