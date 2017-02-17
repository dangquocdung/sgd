###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 28/07/2014
###################################################


from plugin_upload import FileUpload
fileupload = FileUpload(db=cms.db)

def index():
	form = fileupload.formupload()
	#form = fileupload.view_publish()
	return dict(form=form)

def preview(): 
	import os 
	path=os.path.join(fileupload.path,request.args(3)) 
	return response.stream(path)
		
def download():
	from gluon.contenttype import contenttype
	import os 
	path=os.path.join(fileupload.path,fileupload.filename) 
	headers = response.headers
	headers['Content-Type'] = contenttype(fileupload.filename)
	headers['Content-Disposition'] = 'attachment; filename="%s"' % fileupload.filename
	return response.stream(path)
	
def upload_file():
	# inserts file and associated form data.        
	fileupload.upload_file(request.vars.multi_file)
	return fileupload.view()

def msdoc():
	import os
	import shutil
	try:
		src = '%s/%s'%(fileupload.path,fileupload.filename)
		dest = '%s/static/uploads'%(request.folder)
		if not os.path.exists(dest):
			os.makedirs(dest)
		dest += '/googledoc'
		if not os.path.exists(dest):
			os.makedirs(dest)
		dest = '%s/%s'%(dest,fileupload.filename)
		shutil.copy(src,dest)
	except Exception, e:
		print e
	#print request.env.wsgi_url_scheme
	return 'http://%s/%s/static/uploads/googledoc/%s'%(request.env.http_host,request.application,fileupload.filename)
	
def view():
	return fileupload.view()
	
def del_file():
	try:
		fileupload.delete()
		return fileupload.view()		
	except Exception, e:
		return e	

def publish():
	try:
		fileupload.publish(is_publish=('checkbox_publish_%s'%fileupload.upload_id in request.vars.keys()))
		return ''		
	except Exception, e:
		return e	
		
def textcontent():
	form = SQLFORM(fileupload.upload,fileupload.upload_id,fields=['textcontent'],showid=False,labels = {'textcontent':''})
	if form.process().accepted:
		return SCRIPT('parent.$.colorbox.close();')
	return dict(content=form)
		
def applet():
	#filepath = msdoc()
	#filepath = 'http://sonoivu.hatinh.gov.vn/vbsnv/static/test.docx'
	filepath = 'http://113.191.248.231/vendor/server.php/Decuong-TT21-2010.doc'
	script = '''<APPLET CODE="EditOnline.class" WIDTH=1 HEIGHT=0 ARCHIVE="EditOnline.jar" codebase="%s">
	  <param name="filename" value="%s"></APPLET>'''%(URL(r=request,c='static',f='plugin_upload'),filepath)
	return XML(script)
		
def extract():
	try:
		a = fileupload.upload
		txt = a(fileupload.upload_id).textcontent or ''
		folder = T(request.vars.folder) if request.vars.folder else ''
		if txt == '':
			import tesseract.utils as utils	
			filename = '%s/%s'%(fileupload.path,fileupload.filename)
			txt, archives = utils.extract(filename,folder)
			fileupload.db(a.id==fileupload.upload_id).update(textcontent=txt)
		else:
			import tesseract.archives as arc
			if len(txt.split('\n'))<20: archives = arc.get_ocr(txt,folder)
			else: archives = arc.ArchivesText(txt,folder).extract()
		script=""
		if archives['name']:
			script += "$('#number').val('%s');$('#name').val('%s');$('#archives_name').val('%s/%s');"%(archives['name'][0],archives['name'][1],archives['name'][0],archives['name'][1])
		if archives['title']: 
			script+= "$('#archives_title').val('%s');"%(archives['title'].replace("'",'"'))
		if archives['publish']:
			script+= "$('#archives_publish_date').val('%s/%s/%s');"%(archives['publish'][0],archives['publish'][1],archives['publish'][2])
		if archives['org']:
			script+= "$('#archives_org').val('%s');"%(archives['org'])
		if archives['signer']:
			tmp = archives['signer'].split('|')
			script+= "$('#archives_competance').val('%s');$('#archives_position').val('%s');$('#archives_signer').val('%s');"%(tmp[0],tmp[1],tmp[2])
		if archives['receive']:
			script+= "$('#archives_receive').val('%s');"%(archives['receive'])
		from plugin_app import ColorBox
		txt = A(T('Metadata'),href='#',_onclick='$.colorbox({href:"%s",width:"800",height:"600"});'%URL(r=request,c='plugin_upload',f='textcontent',args=request.args))
		script+= "$('#extract_%s').html('%s');"%(fileupload.upload_id,txt)
	except Exception, e:
		script = 'alert(%s);'%e
	return SCRIPT(script)
	

def get_ocr():
	import re	
	def clean(txt,expr):
		for exp in expr:
			tmp = re.findall(exp, txt, re.U)	
			if len(tmp)>0: txt = txt.replace(tmp[0],'')
		return txt
	def clean_text(txt):
		text = txt
		for key in ['\t','\n','\r']: text = text.replace(key,' ')
		while text.find('  ')>=0: text = text.replace('  ',' ')
		return text.lstrip().rstrip()
	
	txt = request.vars.content.decode('utf-8')
	
	expr = [ur"C\w+ H.+NAM",ur"\w{2}c l.+p\w+c"]
	txt = clean(txt,expr)
	name, title, publish, org = '', '', '', ''

	expr = [ur"H.+ng.+th.+n.+\d{4}", ur"[A-Z].+ng.+th.+n.+\d{4}"]
	for exp in expr:
		tmp = re.findall(exp, txt)
		if len(tmp)>0: 
			txt = txt.replace(tmp[0],'')
			tmp = re.findall(r"\d+", tmp[0].encode('utf-8'))
			if len(tmp)==3: publish = tmp
			break
				
	expr = [ur"(?:S|s)ố:.+\S",ur"(?:S|s)\w+.+\S",ur".+:.+/[A-Z|-]+\w+"]
	for exp in expr:
		tmp = re.findall(exp, txt, re.U)	
		if len(tmp)>0: 
			name = tmp[0]
			org = txt[:txt.find(name)]
			txt = txt.replace(tmp[0],'')
			txt = txt.replace(org,'')
			org = clean_text(org).encode('utf-8')
			tmp = re.findall(r"\d+", name)
			number = tmp[0] if len(tmp)>0 else ''
			tmp = re.findall(r"[A-Z|-]+\w+", name)
			symbol = tmp[-1] if len(tmp)>0 else ''
			name = [number.encode('utf-8'),symbol.encode('utf-8')]
			break
	type = u'Quyết định'
	type = u'Công văn'
	type = u'CHỈ THỊ'
	type = type.upper() 		
	if type==u'Công văn'.upper():
		expr = [ur"K\w+ g\w+:",ur"(?:K|k).+:\s",ur".+:\s"]
		for exp in expr:
			tmp = re.findall(exp, txt, re.U)	
			if len(tmp)>0: 
				title = txt[:txt.find(tmp[0])]
				title = clean_text(title).encode('utf-8')
				break
	else:		
		expr = [ur"\w+ \w+\S",ur"\w+ \w+ \w+\S"]
		for exp in expr:
			tmp = re.findall(exp, txt, re.U)
			if len(tmp)>0:
				tmp = txt[txt.find(tmp[0])+len(tmp[0]):].split('\n')
				i = 0
				while i < len(tmp):
					if clean_text(tmp[i]).lstrip().rstrip()=='': pass
					elif title=='': title = tmp[i]
					elif tmp[i].lstrip()[0].isupper(): break
					else: title += ' ' +tmp[i]
					i+=1
				title = clean_text(title).encode('utf-8')
				break
			
	archives = dict(name=name,title=title,publish=publish,org=org)
	content = 'Result:\n' +'\nName:'+ str(name) +'\nTitle:'+ title +'\nPublish:'+ str(publish) +'\nOrg:'+ org +'\n\n'+ txt.encode('utf-8')
	#for txt in tmp: content += txt +'\n'
	content = TEXTAREA(value=content)
	return content
	