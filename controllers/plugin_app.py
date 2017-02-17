###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 22/02/2012
###################################################


def up():
	if not request.vars.attach_uuid:
		import uuid
		vars = request.vars
		vars['attach_uuid'] = str(uuid.uuid1())
		redirect(URL(r=request,vars=vars,args=request.args))
	content = ''
	content = LOAD(c='plugin_attach',f='up.load',ajax=False)
	#content = DIV(LOAD(c='plugin_app',f='index.load',ajax=False))
	response.view = 'plugin_app/content.%s'%request.extension
	return dict(content=content)

@auth.requires_login()
def index():
	return dict(content='')
	
@auth.requires_login()
def explorer():
	content = ''
	if plugin_object:
		box_name = plugin_object.settings.get('box_name',None)
		if box_name:
			content = plugin_box.show(box_name,context=plugin_object.settings)
		else:
			content = plugin_object.explorer({})
			if request.extension == 'html': content = DIV(plugin_object.toolbars(),content,_id='box_edit_default')
	response.view = 'plugin_app/content.%s'%request.extension
	return dict(content=content)

@auth.requires_login()
def read():
	content = ''
	if plugin_object:
		content = plugin_object.explorer({})
		if request.extension == 'html': content = DIV(plugin_object.toolbars(),content,_id='box_edit_default')
	response.view = 'plugin_app/content.%s'%request.extension
	return dict(content=content)
	
@auth.requires(auth.has_membership(role='admin') or (auth.has_permission('create', 'folder', int(request.vars.folder_id)) if request.vars.folder_id else auth.has_permission('create', request.args(0))))	
def create():
	form_redirect('link_create')
	content = ''
	o = plugin_object
	if o.settings.get('attachment'): redirect(URL(f='upload',vars=request.vars,args=request.args))
	form,content = o.form()
	if form.process().accepted:
		if o.process: o.process.update_objects(form.vars.id)
		if o.settings.get('attachment'): 
			if request.vars.attach_uuid:
				from plugin_attach import Attachment
				Attachment().update(form.vars.id,request.vars.attach_uuid)
		if request.vars.reference: args = [request.vars.reference,request.vars.reference_id]
		else: args = [request.args(0),form.vars.id]	
		update_onaccept(form.vars.id)
		update_null(o.name,form.vars.id)	
		if o.folder:
			if o.folder.id:
				if request.vars.folder: o.vars['folder_id'] = int(request.vars.folder)	
				redirect(URL(f='read',args=args,vars=o.vars))
	response.view = 'plugin_app/content.%s'%request.extension
	content = DIV(o.toolbars(),DIV(_class="clearfix"),content,_id='box_edit_default')
	return dict(content=content)
	
@auth.requires(auth.has_membership(role='admin') or (auth.has_permission('edit', 'folder', int(request.vars.folder_id)) if request.vars.folder_id else auth.has_permission('edit', request.args(0), request.args(1))))	
def edit():
	form_redirect('link_update')
	content = ''
	o = plugin_object
	form,content = o.form()
	if form.process().accepted:
		if request.vars.reference: args = [request.vars.reference,request.vars.reference_id]
		else: args = request.args
		update_onaccept(form.vars.id)	
		update_null(o.name,form.vars.id)	
		if request.vars.folder:
			if request.vars.folder_id: o.vars['folder_id'] = int(request.vars.folder)
		redirect(URL(f='read',args=args,vars=o.vars))
	response.view = 'plugin_app/content.%s'%request.extension
	if (not request.vars.folder_id)&(request.extension=='html'): content = DIV(o.toolbars(),DIV(_class="clearfix"),content,_id='box_edit_default')
	else: content = DIV(content,_id='box_edit_default')
	return dict(content=content)

@auth.requires(auth.has_membership(role='admin') or (auth.has_permission('delete', 'folder', int(request.vars.folder_id)) if request.vars.folder_id else auth.has_permission('delete', request.args(0), request.args(1))))	
def delete():
	plugin_object.delete()
	redirect(URL(f='explorer',args=[plugin_object.name],vars=plugin_object.vars))	

def form_redirect(key):
	url = plugin_object.settings.get(key,None)
	if url:
		from plugin_app import get_url
		c,f,e = get_url(url)
		redirect(URL(c=c,f=f, extension=e,args=request.args,vars=request.vars))	
	
def update_onaccept(id):
	onaccept = plugin_object.settings.get('onaccept',None)
	if onaccept:
		from plugin_app import get_url
		c,f,e = get_url(onaccept)
		LOAD(c=c,f=f,extension=e,args=[plugin_object.name,id],vars=request.vars)
	
def update_null(table,id):
	for field in db[table].fields:
		if (db[table][field].type[0:9]=='reference'): 
			if db[table](id)[field] == 0:
				var = {field:None}
				db(db[table].id==id).update(**var)
				
##########################################################
# WIDGET
##########################################################	
	
def get_signer():
	from database import define_table
	define_table(db,auth,'signer')
	if request.vars.org:
		orgs = request.vars.org
		if isinstance(orgs,str): orgs = [orgs]
		orgs = [int(org) for org in orgs]
		rows = db(db.signer.org.belongs(orgs)).select(orderby=db.signer.position)
		options = [OPTION(row.name + ' ['+row.post.name+']',_value=row.id) for row in rows]
	else: options = []
	select = SELECT(options,_name='signer',_id='archives_signer',_multiple=(len(orgs)>1))
	return select	


	
##########################################################
# TreeView
##########################################################
@auth.requires_login()
def treedepth():
	from plugin_app import get_tree
	attr = {}
	for key in request.vars.keys(): attr[key] = request.vars[key]
	attr['depth']=1
	selected = attr.get('selected',[])
	selected = [int(id) for id in selected]
	attr['selected'] = selected
	tree = get_tree(request.args(0),parent=int(request.args(1)),**attr)
	return tree
	
##########################################################
# DropDown
##########################################################
@auth.requires_login()
def create_dropdown():
	table,field = request.args(0).split('.')
	refereed=db[table][field].type[10:] if db[table][field].type[:9] == 'reference' else db[table][field].type[15:] 
	db[table][field].requires = IS_IN_DB(db,refereed+'.id','%(name)s')
	from gluon.tools import Crud
	crud = Crud(db)
	form=crud.create(db[refereed])
	if form.vars.id: session['_plugin_dropbox:%s' % request.args(0)]=form.vars.id
	options = UL(*[LI(v) for k,v in db[table][field].requires.options() if k==str(form.vars.id)])
	return dict(form=form,options=options)

def select_dropdown():
	if not auth.user_id or not session.get('_plugin_dropbox:%s' % request.args(0),None): raise HTTP(400)
	table,field = request.args(0).split('.')
	refereed=db[table][field].type[10:] if db[table][field].type[:9] == 'reference' else db[table][field].type[15:] 
	db[table][field].requires = IS_IN_DB(db,refereed+'.id','%(name)s')
	return TAG[''](*[OPTION(v,_value=k,_selected=(k==str(session['_plugin_dropbox:%s' % request.args(0)])))\
								for k,v in db[table][field].requires.options()])	
	
	
##########################################################
### New update 12/3/2013
##########################################################
		
@auth.requires(auth.has_membership(role='admin') or (auth.has_permission('create', 'folder', int(request.vars.folder_id)) if request.vars.folder_id else auth.has_permission('create', request.args(0))))	
def upload():

	from plugin_app import ColorBox
	o = plugin_object
	if not request.args(1): 
		import uuid
		redirect(URL(r=request,vars=request.vars,args=[o.name,uuid.uuid1()]))
	button1 = SPAN(ColorBox(caption=T('Scan'),source=URL(c='plugin_scan',f='scan',args=request.args,vars=request.vars),url=URL(c='plugin_attach',f='view',args=request.args,vars=request.vars),target='progress',width='100%',height=700),_id='button_scan')
	button2 = SPAN(T('Attachment'),_id="upfile1",style="cursor:pointer")
	button3 = INPUT(_id="data_file_file", _class="", _type="file", _name="file",_style="display:none")
	script = SCRIPT('''$("#upfile1").click(function () {$("#data_file_file").trigger('click');});''')
	upload = FORM(button1, ' ', button2, button3, script)
	upload.attributes['_id'] = "myform"
	upload.attributes['_action'] = URL(f="upload_data",args=request.args,vars=request.vars)  

	form = o.form(True)
	if form.process().accepted:
		if o.process: o.process.update_objects(form.vars.id)
		if request.vars.reference: args = [request.vars.reference,request.vars.reference_id]
		else: args = [request.args(0),form.vars.id]	
		update_onaccept(form.vars.id)
		update_null(o.name,form.vars.id)
		if not o.id:
			from plugin_attach import Attachment
			Attachment().update(form.vars.id,request.args(1))
		if o.folder:
			if o.folder.id:
				if request.vars.folder: o.vars['folder_id'] = int(request.vars.folder)	
				return dict(upload=SCRIPT('parent.$.colorbox.close();window.parent.location.replace("%s");'%URL(f='read',args=args,vars=o.vars)),form='',table='')
				#redirect(URL(f='read',args=args,vars=o.vars))
	return dict(upload=upload,form=form,table=view())


def upload_data():
	# inserts file and associated form data.        
	from plugin_attach import Attachment
	attach = Attachment()
	attach.upload_data(request.vars.multi_file)

def view():
	from plugin_attach import Attachment
	attach = Attachment()
	table=TABLE()
	a = attach.define()
	rows = db((a.object==attach.object)&(a.object_id==attach.object_id)).select()
	for row in rows:
		ajax = "ajax('%s', [], 'progress')"%(URL(f='del_file',args=[attach.object,attach.object_id,row.id],vars=request.vars))
		delete = A(T('Delete'),_href='#',_onclick=ajax,_id='delete')		
		ajax = "gView('http://%s/%s/static/uploads/%s/%s');"%(request.env.http_host,request.application,attach.object,row.file)
		view = A(row.name,_href='#',_onclick=ajax,_id='view_%s'%row.id)		
		ajax = "ajax('%s', [], 'script')"%(URL(f='extract',args=[attach.object,attach.object_id,row.id],vars=request.vars))
		text = A(T('Extract'),_href='#',_onclick=ajax,_id='extract')		
		filesize= row.size or 0
		if filesize>1024*1024: filesize = str(round(filesize/1024*1024,2))+ 'Gb'
		elif filesize>1024: filesize = str(round(filesize/1024,2))+ 'Mb'
		elif filesize>1: filesize = str(int(filesize))+ 'Kb'
		else: filesize = str(round(filesize,2))+ 'Kb'
		tr = TR(TD(SPAN(row.extension,_class='filetype_'+row.extension)),TD(view),TD(filesize,_style='text-align:right'),TD(text),TD(delete))
		table.append(tr)
	return table

def del_file():
	from plugin_attach import Attachment
	attach = Attachment()
	attach.delete()
	return view()		
	
def extract():
	exec('import applications.%s.modules.tesseract.utils as utils' % request.application) 
	from plugin_attach import Attachment
	attach = Attachment()
	a = attach.define()
	filename = '%s/%s'%(attach.path,a(attach.id).file)
	txt, archives = utils.extract(filename,plugin_object.folder.name)
	db(a.id==attach.id).update(content=txt)
	script="$('#view_%s').trigger('click');"%attach.id
	if archives['name']:
		script += "$('#number').val('%s');$('#name').val('%s');$('#archives_name').val('%s/%s');"%(archives['name'][0],archives['name'][1],archives['name'][0],archives['name'][1])
	if archives['title']:
		script+= "$('#archives_title').val('%s');"%(archives['title'])
	if archives['publish']:
		script+= "$('#archives_publish_date').val('%s/%s/%s');"%(archives['publish'][0],archives['publish'][1],archives['publish'][2])
	if archives['org']:
		script+= "$('#archives_org').val('%s');"%(archives['org'])
	if archives['signer']:
		tmp = archives['signer'].split('|')
		script+= "$('#archives_competance').val('%s');$('#archives_position').val('%s');$('#archives_signer').val('%s');"%(tmp[0],tmp[1],tmp[2])
	if archives['receive']:
		script+= "$('#archives_receive').val('%s');"%(archives['receive'])
	return DIV(SCRIPT(script))
	
def get_items():
	itms = []
	if request.vars.q and request.vars.table and request.vars.field:
		q = request.vars.q
		f = request.vars.field
		t = request.vars.table
		fld = db[t][f]
		rows = db(fld.upper().like(q.upper()+"%")).select(fld,distinct=True) 
		itms = [str(t[f]) for t in rows] 
	return '\n'.join(itms)
	
def get_name():
	itms = []
	from plugin_cms import Cms
	cms = Cms()
	if request.vars.q and request.vars.table and request.vars.field:
		q = request.vars.q
		f = request.vars.field
		t = request.vars.table
		try:
			dtable = 	eval('cms.define_table("%s",True)'%t)
		
			rows = cms.db(dtable[f].upper().like("%"+q.upper()+"%")).select(dtable[f],distinct=True) 
			for r in rows:
				itms.append(r[f])
		except Exception, e:
			print e
	return '\n'.join(itms)
	
def get_chuc_vu():
	from plugin_cms import Cms
	from plugin_cms import CmsFolder
	cms = Cms()
	document = cms.define_table('documents',True)
	row = cms.db(document.nguoi_ky==request.vars.nguoi_ky).select().last()
	if row:
		return INPUT(_class="string ac_input" ,_id="documents_chuc_vu" ,_name="chuc_vu",_type="text",_autocomplete="off",_value=row.chuc_vu)
	else:
		return INPUT(_class="string ac_input" ,_id="documents_chuc_vu" ,_name="chuc_vu",_type="text",_autocomplete="off",_value='')
	
def get_co_quan():
	from plugin_cms import Cms
	from plugin_cms import CmsFolder
	cms = Cms()
	document = cms.define_table('documents',True)
	row = cms.db(document.nguoi_ky==request.vars.nguoi_ky).select().last()
	if row:
		return INPUT(_class="string ac_input" ,_id="documents_co_quan_ban_hanh" ,_name="co_quan_ban_hanh",_type="text",_autocomplete="off",_value=row.co_quan_ban_hanh)
	else:
		return INPUT(_class="string ac_input" ,_id="documents_co_quan_ban_hanh" ,_name="co_quan_ban_hanh",_type="text",_autocomplete="off",_value='')
	
### End new 12/3/2013	
	
def add_cart():
	pid = request.vars.pid
	ar_carts =[]
	if request.cookies.has_key ('cart_shop'):
		carts = eval(request.cookies['cart_shop'].value)
		i=0
		for cart in carts:
			cart = eval(cart)
			if cart['id']==pid:
				ar_carts.append(str({'id':str(cart['id']) ,'num':str(int(cart['num'])+1)}))
				i+=1
			else:
				ar_carts.append(str({'id':str(cart['id']) ,'num':str(cart['num'])}))
		if i==0:
			ar_carts.append(str({'id':pid ,'num':str(1)}))
	else:
		ar_carts.append(str({'id':pid ,'num':str(1)}))
		
	response.cookies['cart_shop'] = str(ar_carts) 
	response.cookies['cart_shop']['expires'] = 24 * 3600
	response.cookies['cart_shop']['path'] = '/'
	response.flash = T("Add new cart!")
	
	# load view_carts() nhung ko request duoc cookies moi
	
	div = DIV()
	num_car = 0
	tong_tien = 0
	carts = ar_carts
	from plugin_cms import CmsModel
	from plugin_cms import CmsFolder
	cms = CmsModel()
	db = cms.db
	cms.define_table('san_pham')
	from plugin_app import number_format
	
	for cart in carts:
		cart = eval(cart)
		row  = db((db.san_pham.id==cart['id'])&(db.san_pham.folder== CmsFolder().get_folder(request.args(0)))).select().first()
		if row:
			div1 = DIV(_class='list_cart')
			ul = UL()
			ul.append(LI(row.name))
			ul.append(LI(SPAN('Số lượng: '),cart['num']))
			ul.append(LI(SPAN('Giá: '),number_format(row.gia_san_pham),' VNĐ'))
			div1.append(DIV(IMG(_src=cms.get_avatar('san_pham',row.avatar),_class='thumbnail'),_class='col-md-4 box_ivinh'))
			div1.append(DIV(ul,_class='col-md-8 box_ivinh'))
			div.append(div1)
			div.append(HR())
			tong_tien += int(row.gia_san_pham)* int(cart['num'])
			num_car +=1
	p_tong = DIV(SPAN('Tổng tiền: '))
	p_tong.append(str(number_format(tong_tien))+' VNĐ')
	div.append(B(p_tong,_class='text-right'))
	div.append(A('Thanh toán',_href=URL(c='portal',f='folder',args=request.args(0),vars=dict(page='cart')),_class='btn btn-success'))
	return div

def view_carts():
	div = DIV()
	num_car = 0
	tong_tien = 0
	carts =''
	try:
		if request.cookies.has_key('cart_shop'):
			carts = eval(request.cookies['cart_shop'].value)
			from plugin_cms import CmsModel
			from plugin_cms import CmsFolder
			cms = CmsModel()
			db = cms.db
			cms.define_table('san_pham')
			from plugin_app import number_format
			
			for cart in carts:
				cart = eval(cart)
				row  = db((db.san_pham.id==cart['id'])&(db.san_pham.folder== CmsFolder().get_folder(request.args(0)))).select().first()
				if row:
					div1 = DIV(_class='list_cart')
					ul = UL()
					ul.append(LI(row.name))
					ul.append(LI(SPAN('Số lượng: '),cart['num']))
					ul.append(LI(SPAN('Giá: '),number_format(row.gia_san_pham),' VNĐ'))
					div1.append(DIV(IMG(_src=cms.get_avatar('san_pham',row.avatar),_class='thumbnail'),_class='col-md-4 box_ivinh'))
					div1.append(DIV(ul,_class='col-md-8 box_ivinh'))
					div.append(div1)
					div.append(HR())
					tong_tien += int(row.gia_san_pham)* int(cart['num'])
					num_car +=1
		if num_car>0:			
			p_tong = DIV(SPAN('Tổng tiền: '))
			p_tong.append(str(number_format(tong_tien))+' VNĐ')
			div.append(B(p_tong,_class='text-right'))
			div.append(A('Thanh toán',_href=URL(c='portal',f='folder',args=request.args(0),vars=dict(page='cart')),_class='btn btn-success'))
		else:
			div.append('Giỏ hàng trống')
	except Exception,e: 
		return e
	return div
	
def list_order():
	div= DIV()
	num_car = 0
	tong_tien = 0
	carts =''
	table = TABLE(_class='table')
	table.append(TR(TH('Sản phẩm'),TH('Số lượng'),TH(''),TH('Giá'),TH(B('Thành tiền')),TH(B('Chức năng'))))
	if request.cookies.has_key('cart_shop'):
		carts = eval(request.cookies['cart_shop'].value)
		from plugin_cms import CmsModel
		from plugin_cms import CmsFolder
		cms = CmsModel()
		db = cms.db
		cms.define_table('san_pham')
		from plugin_app import number_format
		
        for cart in carts:
			cart = eval(cart)
			row  = db((db.san_pham.id==cart['id'])).select().first()
			if row:
				tong_tien += int(row.gia_san_pham)* int(cart['num'])
				thanh_tien = int(row.gia_san_pham)* int(cart['num'])
				input_num = INPUT(_type='text',_class='integer',_value=cart['num'],_name='number_pr_%s'%(row.id),_style="width: 55px; text-align: center;")
				ajax = "ajax('%s', ['number_pr_%s'], 'wr_list_order')"%(URL(c='plugin_app',f='update_carts',args=[request.args(0),row.id,'delete']),row.id)
				ajax1 = "ajax('%s', ['number_pr_%s'], 'wr_list_order')"%(URL(c='plugin_app',f='update_carts',args=[request.args(0),row.id,'update']),row.id)
				table.append(TR(TD(row.name,': '),TD(input_num),TD(' * '),TD(number_format(row.gia_san_pham),' VNĐ'),TD(B(number_format(thanh_tien),' VNĐ')),TD(DIV(A(SPAN(_class='glyphicon glyphicon-floppy-save'),'Cập nhật',_onclick=ajax1,_class='btn btn-primary'),_class='btn-group'),A(SPAN(_class='glyphicon glyphicon-remove'),'Xóa',_onclick=ajax,_class='btn btn-danger'),_class='setting')))
				num_car +=1
			
	div.append(table)
	p_tong = DIV(SPAN('Tổng tiền: '))
	p_tong.append(str(number_format(tong_tien) if tong_tien!=0 else '0')+' VNĐ')
	div.append(B(p_tong,_class='text-right'))
	return div

def update_carts():
	pid = request.args(1)
	number = 'number_pr_%s'%(pid)
	number_pr = request.vars[number]
	ar_carts =[]
	if request.args(2)=='delete':
		if request.cookies.has_key ('cart_shop'):
			carts = eval(request.cookies['cart_shop'].value)
			i=0
			for cart in carts:
				cart = eval(cart)
				if cart['id']==pid:
					i+=1
				else:
					ar_carts.append(str({'id':str(cart['id']) ,'num':str(cart['num'])}))
			if i==0:
				ar_carts.append(str({'id':pid ,'num':str(1)}))
		else:
			ar_carts.append(str({'id':pid ,'num':str(1)}))
			
		
	elif request.args(2)=='update':
		if request.cookies.has_key ('cart_shop'):
			carts = eval(request.cookies['cart_shop'].value)
			i=0
			for cart in carts:
				cart = eval(cart)
				if cart['id']==pid:
					ar_carts.append(str({'id':str(cart['id']) ,'num':str(number_pr)}))
					i+=1
				else:
					ar_carts.append(str({'id':str(cart['id']) ,'num':str(cart['num'])}))
			if i==0:
				ar_carts.append(str({'id':pid ,'num':str(1)}))
		else:
			ar_carts.append(str({'id':pid ,'num':str(1)}))
			
	response.cookies['cart_shop'] = str(ar_carts) 
	response.cookies['cart_shop']['expires'] = 24 * 3600
	response.cookies['cart_shop']['path'] = '/'
	
	div= DIV()
	num_car = 0
	tong_tien = 0
	table = TABLE(_class='table')
	table.append(TR(TH('Sản phẩm'),TH('Số lượng'),TH(''),TH('Giá'),TH(B('Thành tiền')),TH(B('Chức năng'))))

	carts = ar_carts
	from plugin_cms import CmsModel
	from plugin_cms import CmsFolder
	cms = CmsModel()
	db = cms.db
	cms.define_table('san_pham')
	from plugin_app import number_format
	
	for cart in carts:

		cart = eval(cart)
		row  = db((db.san_pham.id==cart['id'])).select().first()
		if row:
			tong_tien += int(row.gia_san_pham)* int(cart['num'])
			thanh_tien = int(row.gia_san_pham)* int(cart['num'])
			input_num = INPUT(_type='text',_value=cart['num'],_name='number_pr_%s'%(row.id),_style="width: 55px; text-align: center;")
			ajax = "ajax('%s', ['number_pr_%s'], 'wr_list_order')"%(URL(c='plugin_app',f='update_carts',args=[request.args(0),row.id,'delete']),row.id)
			ajax1 = "ajax('%s', ['number_pr_%s'], 'wr_list_order')"%(URL(c='plugin_app',f='update_carts',args=[request.args(0),row.id,'update']),row.id)
			table.append(TR(TD(row.name,': '),TD(input_num),TD(' * '),TD(number_format(row.gia_san_pham),' VNĐ'),TD(B(number_format(thanh_tien),' VNĐ')),TD(DIV(A(SPAN(_class='glyphicon glyphicon-floppy-save'),'Cập nhật',_onclick=ajax1,_class='btn btn-primary'),_class='btn-group'),A(SPAN(_class='glyphicon glyphicon-remove'),'Xóa',_onclick=ajax,_class='btn btn-danger'),_class='setting')))
			num_car +=1
			
	div.append(table)
	
	p_tong = DIV(SPAN('Tổng tiền: '))
	p_tong.append(str(number_format(tong_tien))+' VNĐ')
	div.append(B(p_tong,_class='text-right'))
	response.flash = T('Cập nhật thành công.')
	return div
	
def view_order():
	div = DIV(_id="view_order")
	div.append(DIV(list_order(),_id='wr_list_order'))
	from plugin_process import ProcessModel
	auth_login = ProcessModel().db.auth_user[auth.user_id]
	form = FORM()
	div1 = DIV(_class="form-group")
	div1.append(LABEL('Họ và tên',SPAN('(*)',_style="color: #f00;margin-left: 5px;")))
	div1.append(INPUT(_id='ho_ten',_name='ho_ten',_type='text',_class="form-control",_placeholder="Họ và tên",_value=auth_login.last_name + ' ' + auth_login.first_name if auth_login else ''))
	form.append(div1)
	
	div1 = DIV(_class="form-group")
	div1.append(LABEL('Email'))
	div1.append(INPUT(_id='email',_name='email',_type='text',_class="form-control",_placeholder="Email",_value=auth_login.email if auth_login else ''))
	form.append(div1)
	
	div1 = DIV(_class="form-group")
	div1.append(LABEL('Điện thoại',SPAN('(*)',_style="color: #f00;margin-left: 5px;")))
	div1.append(INPUT(_id='dien_thoai',_name='dien_thoai',_type='text',_class="form-control integer",_placeholder="Điện thoại"))
	form.append(div1)
	
	div1 = DIV(_class="form-group")
	div1.append(LABEL('Địa chỉ nhận hàng',SPAN('(*)',_style="color: #f00;margin-left: 5px;")))
	div1.append(INPUT(_id='dia_chi',_name='dia_chi',_type='text',_class="form-control",_placeholder="Địa chỉ nhận hàng"))
	form.append(div1)
	
	div1 = DIV(_class="form-group")
	div1.append(LABEL('Lời nhắn'))
	div1.append(TEXTAREA(_id='loi_nhan',_name='loi_nhan',_class="form-control",_rows="3",_placeholder="Lời nhắn"))
	form.append(div1)
	
	div1 = DIV(_class="form-group")
	ul = UL(_class="pttt")
	ul.append(LI(INPUT(_value=1,_type="radio",_name='pttt',_checked=True),SPAN('Thanh toán khi nhận hàng') ))
	div1.append(ul)
	form.append(div1)
	
	ajax = "ajax('%s', ['ho_ten','email','dien_thoai','dia_chi','loi_nhan','pttt'], 'order_view')"%(URL(c='plugin_sgd',f='act_add_cart',args=request.args))
	script = '''
	<script type="text/javascript">
		function check_form(){
		var result = check_form_cart();
		if (result==true) {
			%s
		}
	}
	function check_form_cart(){
		if (document.getElementById("ho_ten").value=='') {
			alert('Chưa nhập tên');
			document.getElementById("ho_ten").focus();
			return false;
	
		}
		if (document.getElementById("dien_thoai").value=='') {
			alert('Chưa nhập số điện thoại');
			document.getElementById("dien_thoai").focus();
			return false;
	
		}
		if (document.getElementById("dia_chi").value=='') {
			alert('Chưa nhập địa chỉ nhận hàng');
			document.getElementById("dia_chi").focus();
			return false;
	
		}
		
		else{
			return true;
		}
			
	}

	</script>'''%(ajax)
	form.append(A('Gửi đặt hàng',_onclick='check_form();', _class='btn btn-success'))
	div.append(form)
	div.append(XML(script))
	return div

def search_product():
	div = DIV(_id='gian_hang')
	wr_toolbar = DIV(_id='toolbar_gian_hang')
	
	toolbar = INPUT(_type='text',_class='form-control serch_by_name  pull-left',_name='serch_key_gian_hang',_placeholder='Tìm theo gian hàng')
	wr_toolbar.append(toolbar)
	toolbar = INPUT(_type='text',_class='form-control serch_by_name  pull-left',_name='serch_key_san_pham',_placeholder='Tìm theo sản phẩm')
	wr_toolbar.append(toolbar)
	ajax = "ajax('%s', ['serch_key_gian_hang','serch_key_san_pham'], 'wr_view_product')"%(URL(c='plugin_app',f='act_search_produc'))
	toolbar = A('Tìm sản phẩm',_class='btn btn-success',_onclick=ajax)
	wr_toolbar.append(toolbar)
	div.append(wr_toolbar)
	div.append(DIV(_id='wr_view_product'))
	return div
	
def act_search_produc():
	from plugin_cms import Cms
	cms = Cms()
	db = cms.db
	san_pham = cms.define_table('san_pham',True)
	folder = cms.define_folder()
	query = db.san_pham.id>0
	if request.vars.serch_key_san_pham:
		query &= san_pham.name.contains(request.vars.serch_key_san_pham)
	if request.vars.serch_key_gian_hang:
		query &= folder.label.contains(request.vars.serch_key_gian_hang)
		query &= (san_pham.r_folder == folder.id)
	rows = db(query).select()
	div = DIV(_class='act_search_produc')
	for row in rows:
		ul = UL()
		ul.append(LI(cms.get_images_content('san_pham',row.san_pham.avatar),_class='ads_product_image'))
		ul.append(LI(A(row.san_pham.name,_href=URL(c='portal',f='read',args=[row.folder.name,'san_pham',row.san_pham.link]),_class='product_name',_target="_blank")))
		ajax = "$.colorbox.close();ajax('%s', [], 'widget_san_pham');"%(URL(c='plugin_app',f='w_san_pham',args=[row.san_pham.id]))
		ul.append(LI( A('Chọn',_class='btn btn-success',_onclick=ajax)))
		div.append(ul)
	return div


def w_san_pham():
	v = request.args(0)
	widget= DIV(INPUT(_class='string',_id='ads_product_r_san_pham',_name="r_san_pham" ,_type="hidden" ,_value=v))
	value = ''
	if v:
		from plugin_cms import Cms
		cms = Cms()
		san_pham = cms.define_table('san_pham',True)
		row = cms.db.san_pham[v]
		product = DIV()
		product.append(DIV(cms.get_images_content('san_pham',row.avatar),_class='ads_product_image'))
		product.append(A(row.name,_href=URL(c='portal',f='read',args=[row.r_folder.name,'san_pham',row.link]),_class='product_name',_target="_blank"))
		from plugin_app import ColorBox
		button = SPAN(ColorBox(T('Produc khac'),source=URL(r=request,c='plugin_app',f='search_product'),width='95%',height='95%',iframe='false'),_class='btn btn-primary')
		product.append(button)
	widget.append(product)
	return widget	
	
def view_new():
	tin_tuc_id = request.vars.tin_tuc_id
	div = DIV(_class='col-md-12')
	folder_id_ivinh = folder_id_gian_hang.id
	if auth.has_permission('quan_tri_gian_hang', 'folder', folder_id_ivinh):
		name = request.args(0)
		from plugin_ckeditor import CKEditor
		
		if not tin_tuc_id:
		   div.append(H2(SPAN('Thêm mới tin tức',_class='title_name'),_id='title_page'))
		
		tin_tuc_edit = cms.define_table('tintuc')
		tin_tuc_edit.folder.default=folder_id_ivinh
		tin_tuc_edit.folder.writable=False
		tin_tuc_edit.folder.readable=False
		tin_tuc_edit.htmlcontent.widget=CKEditor(cms.db).widget	
		
		form=SQLFORM(tin_tuc_edit,tin_tuc_id)
		if tin_tuc_id:
			ajax = "ajax('%s', [''], 'news_detail')"%(URL(c='plugin_app',f='act_delete',args=[request.args(0)],vars=dict(table_name='tintuc',table_id=tin_tuc_id )))
			form[0][-1] = TR(TD(INPUT(_type='submit',_value=T('Submit')),INPUT(_type='button',_value=T('Xóa bài viết'),_onclick=ajax,_class='btn btn-danger'),_colspan="3"),_class='act_ivinh')
		if form.process().accepted:
			dcontent = cms.define_dcontent()
			if not tin_tuc_id:
				from plugin_process import ProcessModel
				objects = ProcessModel().define_objects()
				objects_id = objects.insert(folder=folder_id_ivinh,foldername=name,tablename='tintuc',table_id=form.vars.id,auth_group=7,process=3)

				link = form.vars.name.replace('đ','d')
				link = '%s.html'%IS_SLUG.urlify(link)
				
				from plugin_cms import CmsPublish
				link = CmsPublish().get_link('tintuc',link)
				
				
				dcontent.insert(folder=folder_id_ivinh,dtable='tintuc',table_id=form.vars.id,link=link,name=form.vars.name,avatar=form.vars.avatar,description=form.vars.description,publish_on=request.now,expired_on=None)	
				cms.db(tin_tuc_edit.id==form.vars.id).update(link=link)
				
		div.append(form)
	return dict(content = div)
	
def view_san_pham():
	san_pham_id = request.vars.san_pham_id
	div = DIV(_class='col-md-12')
	folder_id_ivinh = folder_id_gian_hang.id
	if auth.has_permission('quan_tri_gian_hang', 'folder', folder_id_ivinh):
		name = request.args(0)
		from plugin_ckeditor import CKEditor
		
		
		san_pham = cms.define_table('san_pham')
		san_pham.folder.default=folder_id_ivinh
		san_pham.folder.writable=False
		san_pham.folder.readable=False
		san_pham.r_folder.writable=False
		san_pham.r_folder.readable=False
		san_pham.htmlcontent.widget=CKEditor(cms.db).widget	
		
		form=SQLFORM(san_pham,san_pham_id)
		if san_pham_id:
			ajax = "ajax('%s', [''], 'news_detail')"%(URL(c='plugin_app',f='act_delete',args=[request.args(0)],vars=dict(table_name='san_pham',table_id=san_pham_id )))
			form[0][-1] = TR(TD(INPUT(_type='submit',_value=T('Submit')),INPUT(_type='button',_value=T('Xóa sản phẩm'),_onclick=ajax,_class='btn btn-danger'),_colspan="3"),_class='act_ivinh')
		if form.process().accepted:
			print 123
		div.append(form)
	response.view = 'plugin_app/view_new.%s'%request.extension
	return dict(content = div)
	
def act_delete():
	try:
		table_name = request.vars.table_name
		table_id = request.vars.table_id
		print table_id, table_name
		table = cms.define_table(table_name)
		cms.db(table.id==table_id).delete()
		dcontent = cms.define_dcontent()
		from plugin_cms import CmsFolder
		cms.db((dcontent.folder==CmsFolder().get_folder(request.args(0)))&(dcontent.table_id==table_id)&(dcontent.dtable==table_name) ).delete()
		response.flash = T('Xoa thanh cong')
		return XML('<META http-equiv="refresh" content="2;URL=%s">'%(URL(c='portal',f='folder.html',args=request.args(0))))
		
	except Exception, e:
		print e
	
def update_cong_ty():
	page = request.args(0)
	cong_ty = cms.define_table('cong_ty')
	dv_id = request.args(1)
	var = {}
	var[page]=request.vars[page]
	cms.db(cong_ty.id==dv_id).update(**var)
	return 'Cập nhật thành công'
	
# def update_dcontent():
	# from plugin_cms import Cms
	# from plugin_cms import CmsFolder
	# cms = Cms()
	# dcontent = cms.define_dcontent()
	# rows = cms.db(dcontent.id>0).select()
	# ul = UL()
	# i=1
	# for row in rows:
		# from plugin_cms import CmsPublish
		# content = CmsPublish().get_content(tablename=row.dtable,table_id=row.table_id)
		# ul.append(LI(i,'---',content))
		# i+=1
		# if cms.db(dcontent.id==row.id).update(textcontent=content):
			# print 999
	# return ul
	
	