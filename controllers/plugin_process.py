###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 7/03/2012
###################################################

@auth.requires_login()
def table():
	tablename = request.args(0)
	eval('processmodel.define_%s(True)'%tablename)
	content = SQLFORM.grid(db[tablename],args=request.args)
	response.view = 'plugin_process/content.html'	
	return dict(content=content)


@auth.requires_login()		
def index():
	redirect(URL(c='plugin_process',f='explorer',args=['website','soanthao','home']))
	response.view = 'plugin_process/content.html'	
	return dict(content=content)
	
def create():
	from plugin_cms import CmsModel
	from plugin_process import Process
	p = Process()
	first = p.get_process_first()
	ul = UL()
	if not first: 
		table = p.define_procedures()
		rows = p.db(table).select(orderby=table.display_order)
		for row in rows:
			ul.append(LI(A(T(row.name.capitalize()),_href=URL(args=[row.name]))))
	else:
		cms = CmsModel()
		dtable = cms.define_dtable()
		rows = cms.db(dtable).select()
		process_name = p.db.process(first).name
		procedure_name = p.db.process(first).procedures.name
		for row in rows:
			ul.append(LI(A(T(row.name.capitalize()),_href=URL(f='edit',args=[procedure_name,process_name,request.args(2),row.name]))))
	response.view = 'plugin_process/content.html'	
	return dict(content=ul)
	
# @auth.requires(auth.has_membership(role='admin') or (auth.has_permission('edit', 'folder')))	
def edit():
	from plugin_cms import CmsModel
	from plugin_app import Dropdown
	from plugin_ckeditor import CKEditor
	from plugin_process import Process
	
	model = CmsModel()
	db = model.db
	process = Process()
	model.define_dtable()
	tablename = process.tablename
	table_id = process.get_table_id()
	dtable = db(db.dtable.name==tablename).select().first()
	if not dtable: return dict(content='Table %s not existe'%tablename)		
	table = model.define_table(tablename)
	if not table: return dict(content='Can not define %s'%tablename)		
	
	#table.description.widget=CKEditor(db).widget
	
	if dtable.link_edit: 
		from plugin_app import get_url
		c,f,e=get_url(dtable.link_edit)
		redirect(URL(c=c,f=f,extension=e,args=request.args,vars=request.vars))
	
	for field in table.fields:
		if table[field].type[:9]=='reference':
			ref = table[field].type[10:]
			if auth.has_permission('create',ref,0,auth.user_id):  
				table[field].comment=Dropdown(table[field], T('Add new'))
		else:
			row = db(db.dfield.name==field).select().first()
			if row:
				if row.ckeditor: table[field].widget=CKEditor(db).widget		
		if field == 'folder':
			table[field].widget = process.widget_folder
		# if field == 'avatar':
			# from plugin_app import widget_avatar
			# table[field].widget = widget_avatar
		if tablename=='documents':
			if field=='name':
				from plugin_app import widget_number_name
				table[field].widget = widget_number_name
			if field=='nguoi_ky':
				from plugin_app import widget_auto_nguoi_ky
				table[field].widget = widget_auto_nguoi_ky
			if field=='chuc_vu':
				from plugin_app import widget_auto_chuc_vu
				table[field].widget = widget_auto_chuc_vu
			if field=='co_quan_ban_hanh':
				from plugin_app import widget_auto_co_quan_ban_hanh
				table[field].widget = widget_auto_co_quan_ban_hanh
				
	form=SQLFORM(table,table_id,buttons=[])
	
	if dtable.attachment: 
		if not table_id: 
			if not request.vars.uuid:
				import uuid
				redirect(URL(args=request.args,vars=dict(uuid=uuid.uuid1().int)))

		from plugin_upload import FileUpload
		fileupload = FileUpload(db=db,tablename=tablename,table_id=table_id or request.vars.uuid,upload_id=None)
		upload = fileupload.formupload(colorbox=False)
	else: 
		upload = ''

	form[0][-1].append(TR(TD(),TD(INPUT(_type='submit',_value=T('Submit'),_style="display: none;",_id='act_submit'))))
	
	if form.process().accepted:
		update_imageURL_in_content(table,form.vars.id)
		if form.vars.htmlcontent: 
			row = table(form.vars.id)
			row.update_record(htmlcontent=change_img(form.vars.htmlcontent))
		if dtable.attachment:
			if request.vars.uuid:
				fileupload.update(form.vars.id,request.vars.uuid)
		if not table_id: process.create_objects(form.vars.folder,tablename,form.vars.id)
		else: 
			process.update_folder(form.vars.folder,tablename,table_id)
			if dtable.publish:
				from plugin_cms import CmsPublish
				cms = CmsPublish(db=db)
				cms.update(tablename,table_id)
		args = request.args[:4]
		args[2] = model.db.folder(form.vars.folder).name
		args[1] = 'moi_tao'
		redirect(URL(f='explorer',args=args))
	div = DIV(form)
	div.append(upload)
	div.append(DIV(INPUT(_type='submit',_value=T('Submit'),_class='btn btn-primary',_id='act_submit_ao'),INPUT(_type='button',_value=T('Cancel'),_onclick='javascript:history.go(-1)',_class='btn btn-primary')))
	script = SCRIPT('''$("#act_submit_ao").click(function () {$("#act_submit").trigger('click');});''')
	div.append(script)
	
	cache.ram.clear()
	return dict(content=div)		
	


@auth.requires_login()		
def delete():
	from plugin_process import Process
	from plugin_cms import CmsPublish
	cms = CmsPublish()
	process = Process()
	if request.vars.objects: 
		objects_ids = request.vars.objects
		if not isinstance(objects_ids,list): objects_ids = [objects_ids]
	elif process.objects_id: 
		objects_ids = [process.objects_id]
	try:
		#process_id = int(request.vars.process)
		objects_ids = [int(id) for id in objects_ids]

		objects = process.define_objects()
		for id in objects_ids:
			o = objects(id) 
			cms.delete(o.tablename,o.table_id)
		process.delete_objects(objects_ids)
	except Exception,e: 
		print 'plugin_process/delete: ',e
		pass
	# process.process_group(process_id,objects_ids,[process.auth_group])
	redirect(URL(c='plugin_process',f='explorer',args=request.args[:3]),client_side=True)

	
def rtable():
	return dict(content=content)

@auth.requires_login()			
def explorer():
	from plugin_process import ProcessCms
	from plugin_process import Process
	cms = ProcessCms()
	content = cms.explorer()
	return dict(content=content)	
		
def process():
	from plugin_process import Process
	p = Process()
	if request.vars.objects: 
		objects_ids = request.vars.objects
		if not isinstance(objects_ids,list): objects_ids = [objects_ids]
	elif p.objects_id: 
		objects_ids = [p.objects_id]
	try:
		process_id = int(request.vars.process)
		objects_ids = [int(id) for id in objects_ids]
	except:
		process_id = 0
		objects_ids = []
	content = p.process_run(process_id,objects_ids)
	response.view = 'plugin_process/content.%s'%request.extension
	return dict(content=content)

	
def group():
	from plugin_process import Process
	if request.vars.objects: 
		objects_ids = request.vars.objects
		if not isinstance(objects_ids,list): objects_ids = [objects_ids]
	elif process.objects_id: 
		objects_ids = [process.objects_id]
	try:
		process_id = int(request.vars.process)
		objects_ids = [int(id) for id in objects_ids]
		group_ids = [request.vars.auth_group] if isinstance(request.vars.auth_group,str) else request.vars.auth_group
		group_ids = [int(id) for id in group_ids]
	except Exception, e:
		process_id = 0
		objects_ids = []
		group_ids = []
	try:
		content = Process().process_group(process_id,objects_ids,group_ids)
	except Exception, e: 
		content = e
	redirect(URL(f='explorer.html',args=request.args[:3]))
	response.view = 'plugin_process/content.%s'%request.extension
	return dict(content=content)

def publish():
	form = TABLE(TR(TD(T("Publish on")),TD(INPUT(_name='publish_on',_value=request.now,_class="datetime"))))
	form.append(TR(TD(T("Expired on")),TD(INPUT(_name='expired_on',_class="datetime"))))
	form.append(TR(TD(),TD(INPUT(_type="submit",_value=T("Submit")),INPUT(_type="button",_value=T("Cancel"),_onclick="javascript:history.go(-1)"))))
	form = FORM(form)
	
	if form.process().accepted:
		from plugin_cms import CmsPublish
		from plugin_process import Process
		cms = CmsPublish()
		process = Process()
		if request.vars.objects: 
			objects_ids = request.vars.objects
			if not isinstance(objects_ids,list): objects_ids = [objects_ids]
		elif process.objects_id: 
			objects_ids = [process.objects_id]
		try:
			process_id = int(request.vars.process) 
			objects_ids = [int(id) for id in objects_ids]
			objects = process.define_objects()
			publish_on = request.vars.publish_on
			expired_on = request.vars.expired_on
			for id in objects_ids:
				o = objects(id) 
				cms.publish(o.tablename,o.table_id,publish_on,expired_on)
			process.process_group(process_id,objects_ids,[])
		except Exception,e: 
			pass
		redirect(URL(c='plugin_process',f='explorer',args=request.args[:3]),client_side=True)
	response.view = 'plugin_process/content.html'	
	return dict(content=form)
	
def unpublish():
	from plugin_process import Process
	from plugin_cms import CmsPublish
	cms = CmsPublish()
	process = Process()
	if request.vars.objects: 
		objects_ids = request.vars.objects
		if not isinstance(objects_ids,list): objects_ids = [objects_ids]
	elif process.objects_id: 
		objects_ids = [process.objects_id]
	try:
		process_id = int(request.vars.process)
		objects_ids = [int(id) for id in objects_ids]

		objects = process.define_objects()
		for id in objects_ids:
			o = objects(id) 
			cms.unpublish(o.tablename,o.table_id)
	except:
		pass
	#process.process_group(process_id,objects_ids,[process.auth_group])
	process.process_group(process_id,objects_ids,db.process(process_id).process_group or [])
	redirect(URL(c='plugin_process',f='explorer',args=request.args[:3]),client_side=True)

@auth.requires_login()	
def crud():
	from plugin_process import ProcessCrud
	p = ProcessCrud()
	procedures = p.procedures()
	p.process()
	content = SQLFORM.grid(procedures)
	content = SQLFORM.smartgrid(procedures,linked_tables=['process'])
	return dict(content=content)
	
def load_process():
	id,object_id = request.args(0),request.args(1) 
	groups = request.vars.groups or []
	if isinstance(groups,str): groups = [groups]
	users = request.vars.users or []
	if isinstance(users,str): users = [users]
	process_run(id,object_id,groups,users)
	return T('Successfully sent')


def mail():
	content = TABLE()
	from plugin_process import define_process_email
	define_process_email(db,auth,True)
	rows = db(db.process_email.created_by==auth.user_id).select(db.process_email.email,distinct=True)
	list = '['
	for row in rows:
		temp=''
		temp+='"'+row['email']+'",'
		list+=temp
	list=list[0:len(list)-1]
	list+=']'
	table = TABLE()
	input = TEXTAREA( _id="suggest4", _name="emails")
	script = '''<script type="text/javascript">
				$().ready(function() {
					function formatItem(row) {
						return "<strong>" + row[0] + "</strong>";
					}
					function formatResult(row) {
						return row[0].replace(/(<.+?>)/gi, '');
					}
					$("#suggest4").autocomplete(%s, {
						width: 300,
						multiple: true,
						matchContains: true,
						formatItem: formatItem,
						formatResult: formatResult
					});
				});
				</script>'''%(list)
	content.append(TR(TH(T('To emails')),TD(input,XML(script),_class='send_email')))
	content.append(TR(TH(),TD('Ví dụ: user@hatinh.gov.vn,user@chinhphu.vn')))
	content.append(TR(TH(T('Notes')),TD(TEXTAREA(_name='notes',_cols="30"),_class='notes')))
	content.append(TR(TH(T('Attachment')),TD(INPUT(_type='checkbox',_name='attach',_checked=True))))
	ajax = "ajax('%s', ['emails','notes','attach'], 'window_sendmail')"%(URL(c='plugin_process',f='sendmail',args=request.args,vars=request.vars))
	content.append(TR(TH(),TD(INPUT(_type='button',_value=T('Send'),_onclick=ajax),INPUT(_type='button',_value=T('Close'),_onclick='window.parent.close()'))))
	#response.view = 'plugin_app/content.%s'%request.extension
	h2 = H2(T('Gui email'),_class='title')
	content = DIV(h2,content,_id='window_sendmail')
	return dict(content=content)

def sendmail():
	emails = request.vars.emails.replace(' ','')
	emails = emails.replace(';',',')
	emails = emails.split(',')
	mail = auth.setting_mail()
	object = request.args(0)
	object_id = request.args(1)
	row = db[object](object_id)
	name = row.name
	if 'folder' in db[object].fields: name = row.folder.name +' ' + name
	subject = '[%s] %s'%(db.auth_group(auth.user_org).role, name)
	content = ''
	from plugin_app import get_represent
	for field in db[object].fields:
		if (field <>'id') & (db[object][field].readable==True):		
			content += str(T(db[object][field].label))+': '+get_represent(object,field,row[field])
			content += chr(13)
	# content += url 
	content += chr(13)+chr(13) + 'Với lời nhắn:  '+ request.vars.notes
	attachments = []
	if request.vars.attach:
		from gluon.tools import Mail
		from plugin_attach import Attachment
		attachs = Attachment(object,object_id).files()
		attachments = [Mail.Attachment(file) for file in attachs]
	user = db.auth_user(auth.user_id)
	sender = user.username + '@hatinh.gov.vn'
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=emails,subject=subject,reply_to=sender,message=content,attachments=attachments):
		div = DIV(H2(T('Process execute and send mail successfully')),XML(scr),_class='notice')
		from plugin_process import define_process_email
		table = define_process_email(db,auth)
		o = plugin_process
		attach = request.vars.attach or False
		for email in emails:
			table.insert(email=email,description=request.vars.notes,attach=attach,objects=o.objects.id)
	else: 
		div = DIV(H2(T('Send mail error')),XML(scr),_class='notice')
	return div
	
	
	
##########################################################
### New update 18/3/2013
##########################################################	

def widget_access():
	from plugin_app import input_option
	id = request.vars.procedures 
	query = (db.process.procedures==request.vars.procedures) 
	widget = input_option('process', type='checkbox', query=query, keyname='paccess')
	return widget
	
##########################################################
### New update 21/3/2013
##########################################################	

def load_group():
	def get_parent(id):	
		parent = id
		row = db.auth_group(parent)
		while row:
			if row.type=='group': break
			parent = row.parent
			row = db.auth_group(parent)
		return parent	
	
	if request.vars.process_address=='': return ''
	from plugin_process import define_process_address
	pa = define_process_address(db,auth)
	row = pa(int(request.vars.process_address))
	list_id = row.auth_group if row else []
	i = 1
	tr = TR()		
	tmp = SPAN()
	rows = db(db.auth_group.id.belongs(list_id)).select(orderby=db.auth_group.parent|db.auth_group.position|db.auth_group.role)
	parent = None
	for row in rows:
		if (row.type in ['group','group_org']): pass
		else:
			input = SPAN(i if i>9 else '0%s'%i,INPUT(_type='checkbox',_name='auth_group',_class='auth_group',_value=row.id,_checked=True if request.vars.check_all else False),row.role,BR())
			if parent != row.parent: 
				input = SPAN(B(db.auth_group(row.parent).role),BR(),input)
			parent = row.parent
			tmp.append(input)
			if i%10==0: 
				tr.append(TD(tmp))
				tmp = SPAN()
			i+=1
	tr.append(TD(tmp))	
	return TABLE(tr)
	
def save_group():
	from plugin_process import define_process_address
	pa = define_process_address(db,auth)
	if request.vars.address_book=='': 
		if request.vars.process_address!='':
			db(pa.id==int(request.vars.process_address)).update(auth_group=request.vars.auth_group,process=request.vars.process)
			script='alert("Đã cập nhật thành công!");'
		else: script='alert("Chưa nhập tên danh bạ!");'
	else:
		pa.update_or_insert(name=request.vars.address_book,auth_group=request.vars.auth_group,process=request.vars.process)
		script='alert("Thêm mới danh bạ thành công!");'
	script = SCRIPT(script)
	return script
	
def tree_group():
	def process_check():
		rows = db(db.procedures.id>0).select()
		tr = TR()
		for row in rows:
			rs = db(db.process.procedures==row.id).select()
			td = TD(B(row.name),BR())
			add = False
			for r in rs: 
				try: settings=eval(r.setting.replace(chr(13),''))
				except: settings={}
				if settings.get('address',False): 
					td.append(SPAN(INPUT(_type='checkbox',_name='process',_value=r.id,_checked=True),r.name,BR()))
					add = True
			if add: tr.append(td)		
		return SPAN(H5('Được dùng trong các chức năng:'),TABLE(tr))
		
	def parents(id):
		ids = []
		parent = db.auth_group(id).parent
		while parent:
			ids.append(parent)
			parent = db.auth_group(parent).parent
		return ids
		
	selected = []
	script, ex = '', ''
	rows = db(db.auth_group.parent==None).select()
	for row in rows:	
		script += '$("#expand_all_%s").click();'%row.id
		ex += '<div id="auth_group%s_control"><a href="?#"></a><a href="?#" id="expand_all_%s"></a></div>'%(row.id,row.id)
	if request.vars.auth_group:
		groups = [request.vars.auth_group] if isinstance(request.vars.auth_group,str) else request.vars.auth_group
		for id in groups: 
			id = int(id)
			selected.append(id)
			list_parent = parents(id)
			list_parent.reverse()
			for parent in list_parent:
				script += '''if($('#checkbox_%s').length == 0) {$('#parent_%s').click();setTimeout(function(){$('#checkbox_%s').prop('checked', true);},500);}'''%(id,parent,id)
			script += '''$('#checkbox_%s').prop('checked', true);'''%id
	script = SCRIPT(script)
	process = db.process(plugin_process.process)
	vars=request.vars
	if vars.process: del vars['process']
	if vars.auth_group: del vars['auth_group']
	ajax = "ajax('%s', ['address_book','auth_group','process','process_address'], 'script')"%(URL(f='save_group',args=request.args,vars=vars))
	address_input = SPAN(process_check(),B('Nhập tên danh bạ '),INPUT(_name='address_book',_id='address_book'),' ',INPUT(_type='button',_value=T('Submit'),_onclick=ajax),_id='address_book')
	tree = plugin_process.get_tree(process,selected,None)
	return SPAN(XML(ex),tree,address_input,script,DIV(_id='script'))

def filter_img():	
	div = DIV()
	if request.vars.htmlcontent:
		from bs4 import BeautifulSoup
		soup = BeautifulSoup(request.vars.htmlcontent)
		ul = UL(_id='img_filter')
		i = 1
		for link in soup.find_all('img'):
			input = INPUT(_type="radio",_checked=False,_name='input_img',_id='radio_img%s'%(i),_value=link.get('src'))
			ul.append(LI(IMG(_src=link.get('src'),_onclick='check(%s)'%(i)),BR(),input,_class='i_li_item',_id='li_item%s'%(i)))
			i+=1
		div.append(ul)
		scr= '''
		<script src="//code.jquery.com/jquery-1.11.2.min.js"></script>
		<script type="text/javascript">
		function check(i) {
		
			
			if ($('#radio_img'+i).is(':checked'))
			{
				document.getElementById("radio_img"+i).checked = false;
				
			}
			else{
				document.getElementById("radio_img"+i).checked = true;
			}
			
		}
		</script>'''
		div.append(XML(scr))
	else:
		div.append('Không tìm được nội dung bài viết')
	return div
	
def update_imageURL_in_content(table,id):	
	if request.vars.htmlcontent:
		row= table(id)
		if request.vars.input_img:
			if request.vars.input_img[0:7] <> 'http://':
				lis = request.vars.input_img.split('/')
				link = lis[len(lis)-1]
				row.update_record(avatar=link)
			else:
				import urllib
				import os
				url = request.vars.input_img
				dir='static/uploads/images_download'
				path = '%s/%s'%(request.folder,dir)
				if not os.path.exists(path): os.makedirs(path)
				filename = url.split('/')[-1]
				while os.path.exists('%s/%s/%s'%(request.folder,dir,filename)): 
					filename = '1_%s'%filename
				urllib.urlretrieve(url, '%s/%s'%(path,filename))	
				row.update_record(avatar=filename)
		else:
			if not row.avatar:
				new_content= row.htmlcontent
				link =''
				content = new_content.replace(' ', '')
				n1 = content.find('<img')
				if n1>-1: 
					n1 = content.find('src=', n1)
					if n1>-1: 
						n1 = content.find('"', n1)
						if n1>-1:
							n1+=1
							n2 = content.find('"', n1)
							link = content[n1:n2]
						else:
							n1 = content.find("'", n1)
							if n1>-1:
								n1+=1
								n2 = content.find("'", n1)
								link = content[n1:n2]	
				if (link <>'') & (link[0:7] <> 'http://'):
					ns = link.split('/')
					link = ns[len(ns)-1]
					# link = "http://%s/%s/static/uploads/ckeditor/%s"%(request.env.http_host,request.application,link)
				row.update_record(avatar=link)
	return 	

# Update image to server
	
def save_img(url,filename=None,dir='static/uploads/images_download'):
	import urllib
	import os
	path = '%s/%s'%(request.folder,dir)
	if not os.path.exists(path): os.makedirs(path)
	filename = filename or url.split('/')[-1]
	while os.path.exists('%s/%s/%s'%(request.folder,dir,filename)): 
		filename = '1_%s'%filename
	urllib.urlretrieve(url, '%s/%s'%(path,filename))
	return "/%s/%s/%s"%(request.application,dir,filename)

def change_img(html):
	from bs4 import BeautifulSoup
	soup = BeautifulSoup(html)
	imgs = []
	dir = 'static/uploads/images_download'
	for link in soup.find_all('img'):
		url = link.get('src')
		
		try:
			path = save_img(url,dir=dir)
			link['src']=path
		except Exception, e:
			print e
			pass
	#for img in imgs: html = html.replace(img[0],img[1])		
	return soup.prettify().replace('<html>','').replace('</html>','')	
