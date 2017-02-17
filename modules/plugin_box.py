###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 22/02/2012
# Version 0.2 Date: 20/01/2014
###################################################

class Box:
	def __init__(self,**attr):
		print attr
		self.db = attr.get('db',None)
		self.migrate = attr.get('migrate',False)
		self.box = self.define_box()

	def define_box(self):	
		if 'box' in self.db.tables: return self.db.box
		from gluon.dal import Field
		return self.db.define_table('box',
			Field('name',unique=True,required=True),
			Field('setting','text',default='{}'),
			Field('textcontent','text',default=''),
			Field('htmlcontent','text',default=''),
			Field('avatar','upload',autodelete=True),
			migrate=self.migrate)		
				
	def render(self,boxname=None,id=None,context={}):
		from html import XML
		from gluon import current
		try:
			import cStringIO
			box = self.box(id) if id else self.db(self.db.box.name==boxname).select().first()
			content = box.htmlcontent.replace('&quot;', "'").replace('&#39;', '"')	
			content = '%s%s'%(box.textcontent,content)
			try:
				settings = eval(box.setting.replace(chr(13),''))
				for key in settings.keys(): context[key] = settings[key]
			except: 
				pass
			content = current.response.render(cStringIO.StringIO(content), context)
			return XML(content)
		except Exception, e:
			return 'Box %s error: %s'%(boxname or id, e)
