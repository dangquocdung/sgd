###################################################
# This file was developed by Anhnt
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 28/07/2014
###################################################

def add_gian_hang():
	template ='gian_hang.html'
	if request.vars.template:
		if request.vars.template=='t1':
			template ='gian_hang1.html'
		elif request.vars.template=='t2':
			template ='gian_hang.html'
		else:
			template ='gian_hang2.html'
	name = request.vars.ten_url.lower()
	folder = cms.define_folder()
	id = db.folder.insert(parent=241,name=name,label=request.vars.ten_gian_hang,setting="{'TABLES':['tintuc','cong_ty','san_pham']}",layout=template,created_by=auth.user_id)
	from plugin_process import ProcessModel
	processmodel = ProcessModel()
	role = 'gian-hang-'+str(name)
	group_id = processmodel.db.auth_group.insert(role=role,parent=8,atype='org',created_by=1)
	processmodel.db.auth_permission.insert(group_id =group_id,name='quan_tri_gian_hang',table_name='folder',record_id=id)
	processmodel.db.auth_membership.insert(group_id =group_id,user_id=auth.user_id)
	
	auth_name = processmodel.db.auth_user[auth.user_id]
	
	mail = auth.setting_mail()
	mail.send(to=['nguyentuananh.aptech@gmail.com'],subject='Có 1 gian hàng mới: %s'%(request.vars.ten_gian_hang),message='Gian hàng: %s đã được khởi tạo bởi người dùng %s'%(request.vars.ten_gian_hang,(auth_name.first_name +' ' +auth_name.last_name) )) 
	mail.send(to=[auth_name.email],subject='Bạn đã khởi tạo thành công gian hàng: %s'%(request.vars.ten_gian_hang),message='Gian hàng: %s. Bạn vui lòng liên hệ ban quản trị để đăng ký duyệt gian hàng của bạn. Xin cảm ơn'%(request.vars.ten_gian_hang )) 
	
	
	
	redirect(URL(c='portal',f='folder',args=['tao-nha-cung-cap',id,name]))
	
	
def add_cong_ty():
	id_folder = request.args(1)
	name = request.args(2)
	from plugin_ckeditor import CKEditor
	div = DIV(_class='col-md-12')
	div.append(H2(SPAN('Khởi tạo gian hàng',_class='title_name'),_class='title_page'))
	cong_ty = cms.define_table('cong_ty')
	from gluon.tools import Crud
	crud = Crud(cms.db)
	cong_ty.folder.default=id_folder
	cong_ty.folder.writable=False
	cong_ty.folder.readable=False
	
	cong_ty.start_time.writable=False
	cong_ty.start_time.readable=False
	
	cong_ty.danh_gia.writable=False
	cong_ty.danh_gia.readable=False
	
	cong_ty.is_maps.writable=False
	cong_ty.is_maps.readable=False
	form = crud.create(cong_ty)
	if form.process().accepted:
		from plugin_process import ProcessModel
		objects = ProcessModel().define_objects()
		objects_id = objects.insert(folder=id_folder,foldername=name,tablename='cong_ty',table_id=form.vars.id,auth_group=8,process=3)
		link = name.replace('đ','d')
		link = '%s.html'%IS_SLUG.urlify(link)
		dcontent = cms.define_dcontent()
		dcontent.insert(folder=id_folder,dtable='cong_ty',table_id=form.vars.id,link=link,name=form.vars.name,avatar=form.vars.avatar,description=form.vars.description,publish_on=request.now,expired_on=None)	
		cms.db(cong_ty.id==form.vars.id).update(link=link)
		redirect(URL(c='portal',f='folder',args=[name]))
	div.append(form)
	response.view = 'layout/home_dang_ky_nha_cung_cap.html'
	return dict(content=div)
	
def edit_cong_ty():
	id_folder = request.args(1)
	name = request.args(0)

	from plugin_ckeditor import CKEditor
	div = DIV(_class='col-md-12')
	div.append(H2(SPAN('Khởi tạo gian hàng',_class='title_name'),_class='title_page'))

	cong_ty = cms.define_table('cong_ty')
	cong_ty_id = db(cong_ty.folder==folder_id_gian_hang).select().first()
	from gluon.tools import Crud
	crud = Crud(cms.db)
	cong_ty.folder.default=id_folder
	cong_ty.folder.writable=False
	cong_ty.folder.readable=False

	cong_ty.start_time.writable=False
	cong_ty.start_time.readable=False

	cong_ty.danh_gia.writable=False
	cong_ty.danh_gia.readable=False

	cong_ty.is_maps.writable=False
	cong_ty.is_maps.readable=False
	form = crud.update(cong_ty,cong_ty_id)
	if form.process().accepted:

		from plugin_process import ProcessModel
		objects = ProcessModel().define_objects()
		objects_id = objects.insert(folder=id_folder,foldername=name,tablename='cong_ty',table_id=form.vars.id,auth_group=8,process=3)
		
		link = name.replace('đ','d')
		link = '%s.html'%IS_SLUG.urlify(link)
		dcontent = cms.define_dcontent()
		dcontent.insert(folder=id_folder,dtable='cong_ty',table_id=form.vars.id,link=link,name=form.vars.name,avatar=form.vars.avatar,description=form.vars.description,publish_on=request.now,expired_on=None)	
		cms.db(cong_ty.id==form.vars.id).update(link=link)
		redirect(URL(c='portal',f='folder',args=[name]))
	pass
	div.append(form)
	
def act_add_cart():
	don_hang = cms.define_table('don_hang')
	don_hang_item = cms.define_table('don_hang_item')
	don_hang_item = cms.define_table('san_pham')
	don_hang_gian_hang = cms.define_table('don_hang_gian_hang')
	gian_hang = []
	from plugin_cms import CmsFolder
	folder_id = CmsFolder().get_folder(request.args(0))
	
	don_hang_id = db.don_hang.insert(auth_user = auth.user_id or '',nguoi_nhan_hang=request.vars.ho_ten,email=request.vars.email,dien_thoai=request.vars.dien_thoai,dia_chi=request.vars.dia_chi,loi_nhan=request.vars.loi_nhan,thanh_toan=request.vars.pttt )
	carts = eval(request.cookies['cart_shop'].value)
	
	for cart in carts:
		cart = eval(cart)
		row  = db(db.san_pham.id==cart['id']).select().first()
		if row:
			if row.r_folder not in gian_hang:
				gian_hang.append(row.r_folder)
			db.don_hang_item.insert(r_don_hang=don_hang_id,r_san_pham=cart['id'],so_luong=cart['num'],gia_ban=row.gia_san_pham)
	if len(gian_hang)>0:
		for g in gian_hang:
			db.don_hang_gian_hang.insert(folder_gian_hang=g,r_status=1,r_don_hang=don_hang_id)
	response.cookies['cart_shop'] = 'invalid' 
	response.cookies['cart_shop']['expires'] = -10 
	response.cookies['cart_shop']['path'] = '/' 
	div = DIV(B('Đặt hàng thành công. Chúng tôi sẽ liên hệ với bạn trong thời gian sớm nhất để xác nhận đơn hàng. Xin cảm ơn! '),_class='bg-info text-center' )
	div.append(DIV(BR(),'Chuyển hướng về trang chủ sau 3 giây.',_class='bg-info text-center' ))
	scr ='''
	 <META http-equiv="refresh" content="3;URL=%s">
	'''%(URL(c='portal',f='folder',args=['home']))
	div.append(XML(scr))
	return div
	
def test_email():
	mail = auth.setting_mail()
	response.view = 'plugin_sgd/content.%s'%request.extension
	if mail.send(to=['nguyentuananh.aptech@gmail.com'],subject='Tiêu đề email',message='Tin kiểm tra'):
		abc ='Ok'
	else: abc ='NO'
	return dict(content=abc)
	
def view_don_hang():
	from plugin_app import number_format
	don_hang_id = request.args(1)
	don_hang = cms.define_table('don_hang')
	don_hang_item = cms.define_table('don_hang_item')
	san_pham = cms.define_table('san_pham')
	rows_don_hang = cms.db.don_hang[don_hang_id]
	query = (don_hang_item.r_don_hang==don_hang_id)
	rows_don_hang_item = cms.db(query).select()
	div = DIV()
	table = TABLE(_class='table')
	table.append(TR(TH('Khách hàng'),TD(rows_don_hang.nguoi_nhan_hang)))
	table.append(TR(TH('Địa chỉ nhận hàng'),TD(rows_don_hang.dia_chi)))
	table.append(TR(TH('Lời nhắn:'),TD(rows_don_hang.loi_nhan)))
	div.append(table)
	div.append(H4('Chi tiết đơn hàng'))
	table = TABLE(_class='table')
	table.append(TR(TH('Stt',_style="width: 30px;"),TH('Tên sản phẩm'),TH('Số lượng'),TH('Đơn giá'),TH('Thành tiền')))
	i = 1
	for row in rows_don_hang_item:
		if row.r_san_pham.r_folder ==int(request.args(0)):
			table.append(TR(TD(i,_class='text-center'),TD(row.r_san_pham.name),TD(row.so_luong),TD(number_format(row.gia_ban),' VNĐ'),TD(number_format(int(row.gia_ban)* int(row.so_luong)),' VNĐ')))
			i +=1
	div.append(table)
	div_bt = DIV(_class="modal-footer")
	
	div_st = DIV(_class="btn-group")
	div_st.append(BUTTON(T('Cập nhật trạng thái'),_type="button" ,_class="btn btn-default dropdown-toggle" ,**{ "_data-toggle":"dropdown" ,"_aria-expanded":"false"}))
	
	don_hang_status = cms.define_table('don_hang_status')
	row_status = cms.db(don_hang_status.id>0).select()
	ul_st = UL(_class="dropdown-menu")
	for s in row_status:
		# ajax = "ajax('%s', [], '')"%(URL(f='update_don_hang',args=request.args,vars=dict('status'=s.id)))
		ul_st.append(LI(A(s.name,_class="btn btn-default")))
	div_st.append((ul_st))
	# div_bt.append((div_st))
	# div_bt.append(A('Xóa đơn hàng',_class="btn btn-default"))
	div_bt.append(A('Gửi phản hồi',_href="mailto:%s?Subject=Xin chào khách hàng %s"%(rows_don_hang.email,rows_don_hang.nguoi_nhan_hang), _class="btn btn-primary" ))
	div_bt.append(A('Thoát',_class="btn btn-default",**{"_data-dismiss":"modal"}))
	div.append(div_bt)
	return div
	
def update_don_hang():
	try:
		don_hang_gian_hang = cms.define_table('don_hang_gian_hang')
		status = request.vars[request.vars.name]
		id = cms.db((don_hang_gian_hang.folder_gian_hang==request.vars.folder)&(don_hang_gian_hang.r_don_hang==request.vars.don_hang)).update(r_status=status)
		if not id:
			cms.db.don_hang_gian_hang.insert(folder_gian_hang==request.vars.folder,r_don_hang==request.vars.don_hang,r_status=status)
		session.flash = T("Cập nhật thành công!")
		return ''
	except Exception,e: 
		print  e
	
def index():
	return dict()

# START QUAN TRI GIAN HANG
	

@auth.requires(auth.has_membership(role='admin') or auth.has_membership(role='ql_gian_hang'))	
def gian_hang():
	div = DIV(_id='gian_hang')
	wr_toolbar = DIV(_id='toolbar_gian_hang')
	
	toolbar = DIV(_class="btn-group pull-left")
	ajax = "ajax('%s', [], 'wr_view_gian_hang')"%(URL(c='plugin_sgd',f='cread_gian_hang'))
	toolbar.append(A(SPAN(_class='glyphicon glyphicon-plus'),'Thêm gian hàng',_class="btn btn-primary",**{'_data-toggle':'modal','_data-target':'#act_add_gian_hang'}))
	wr_toolbar.append(toolbar)
	
	
	# toolbar = DIV(_class="btn-group pull-right")
	# toolbar.append(A('Tất cả lĩnh vực',_class="btn btn-primary"))
	# toolbar.append(A(SPAN(_class='caret'),SPAN(_class='sr-only'),_class="btn btn btn-primary dropdown-toggle",**{'_data-toggle':"dropdown", '_aria-expanded':"false"}))
	# ul =UL(_class="dropdown-menu")
	# ul.append(LI(A('Điện thoại')))
	# ul.append(LI(A('Máy tính')))
	# toolbar.append(ul)
	# wr_toolbar.append(toolbar)
	
	
	toolbar = DIV(_class="btn-group pull-right ")
	ajax = "ajax('%s', [], 'wr_view_gian_hang')"%(URL(c='plugin_sgd',f='view_gian_hang'))
	toolbar.append(A('Tất cả gian hàng',_class="btn btn-primary",_onclick=ajax))
	toolbar.append(A(SPAN(_class='caret'),SPAN(_class='sr-only'),_class="btn btn btn-primary dropdown-toggle",**{'_data-toggle':"dropdown", '_aria-expanded':"false"}))
	ul =UL(_class="dropdown-menu")
	ajax = "ajax('%s', [], 'wr_view_gian_hang')"%(URL(c='plugin_sgd',f='view_gian_hang',vars=dict(type_gian_hang=240)))
	ul.append(LI(A('Gian hàng đã cấp phép',_onclick=ajax)))
	ajax = "ajax('%s', [], 'wr_view_gian_hang')"%(URL(c='plugin_sgd',f='view_gian_hang',vars=dict(type_gian_hang=241)))
	ul.append(LI(A('Gian hàng chờ cấp phép',_onclick=ajax)))
	toolbar.append(ul)
	wr_toolbar.append(toolbar)
	
	ajax = "ajax('%s', ['serch_key'], 'wr_view_gian_hang')"%(URL(c='plugin_sgd',f='view_gian_hang'))
	toolbar = INPUT(_type='text',_class='form-control serch_by_name  pull-right',_name='serch_key',_onkeydown=ajax,_placeholder='Tìm theo tên gian hàng')
	wr_toolbar.append(toolbar)
	
	div.append(wr_toolbar)
	div.append(DIV(view_gian_hang(),_id='wr_view_gian_hang'))
	return dict(content=div)
	
def cread_gian_hang():
	return dict()
	
def add_gian_hang_admin():
	template ='gian_hang.html'
	if request.vars.template:
		if request.vars.template=='t1':
			template ='gian_hang1.html'
		elif request.vars.template=='t2':
			template ='gian_hang.html'
		else:
			template ='gian_hang2.html'
	name = request.vars.ten_gian_hang
	name = name.replace('đ','d')
	name = '%s'%IS_SLUG.urlify(name)
	folder = cms.define_folder()
	id = db.folder.insert(parent=241,name=name,label=request.vars.ten_gian_hang,setting="{'TABLES':['tintuc','cong_ty','san_pham']}",layout=template,created_by=auth.user_id)
	try:
		from plugin_process import ProcessModel
		processmodel = ProcessModel()
		if id:
			cong_ty = cms.define_table('cong_ty')
			link = (request.vars.ten_gian_hang).replace('đ','d')
			link = '%s.html'%IS_SLUG.urlify(link)
			ct_id = db.cong_ty.insert(name=request.vars.ten_gian_hang,link=link,folder=id)
			if ct_id:
				objects = processmodel.define_objects()
				objects_id = objects.insert(folder=id,foldername=name,tablename='cong_ty',table_id=ct_id,auth_group=8,process=3)
				dcontent = cms.define_dcontent()
				dcontent.insert(folder=id,dtable='cong_ty',table_id=ct_id,link=link,name=request.vars.ten_gian_hang,publish_on=request.now,expired_on=None)	
	except Exception,e: 
		return e
	role = 'gian-hang-'+str(name)
	group_id = processmodel.db.auth_group.insert(role=role,parent=8,atype='org',created_by=1)
	processmodel.db.auth_permission.insert(group_id =group_id,name='quan_tri_gian_hang',table_name='folder',record_id=id)
	processmodel.db.auth_membership.insert(group_id =group_id,user_id=auth.user_id)
	response.flash = T('Thêm thành công.')
	return LOAD(c='plugin_sgd',f='detai_gian_hang.load',args=[id],ajax=False)
	
def view_gian_hang():
	ul = UL(_class='wr_view_gian_hang')
	folder = cms.define_folder()
	query = folder.id>0
	type_gian_hang = 292
	if request.vars.type_gian_hang:
		query &= folder.parent == request.vars.type_gian_hang
	else:	
		query &= folder.parent.belongs([240,241])
	if request.vars.serch_key:
		query &= folder.label.contains(request.vars.serch_key)
	rows = cms.db(query).select(orderby=~cms.db.folder.created_on)
	for row in rows:
		
		li = LI(_class='item_gian_hang gian_hang_%s'%(row.parent.name),**{'_data-toggle':'modal','_data-target':'#exampleModal','_data-whatever':row.id})
		li.append(DIV(_class='image'))
		li.append(DIV(SPAN(row.label),_class='name'))
		ul.append(li)
	return ul
	
def detai_gian_hang():
	folder = cms.define_folder()
	folder_id = request.args(0)
	row = folder[folder_id]
	div = DIV(_id='detai_gian_hang')
	div_header = DIV(_class='modal-header')
	div_header.append(A(SPAN(XML('&times;'),**{'_aria-hidden':'true'}),_class="close",**{ '_data-dismiss':'modal', '_aria-label':'Close'}))
	div_header.append(H4(row.parent.label,' : ',row.label,_class="modal-title", _id="exampleModalLabel"))
	div.append(div_header)
	
	
	div_body = DIV(_class='modal-body')
	wr_toolbar = DIV(_class="wr_toolbar text-left")
	
	if (row.parent==241):
		ajax = "ajax('%s', [], 'detai_gian_hang')"%(URL(c='plugin_sgd',f='act_move_folder',args=[folder_id],vars=dict(parent=240,folder=row.id)))
		toolbar = DIV(_class="btn-group ")
		toolbar.append(A('Duyệt gian hàng',_onclick=ajax,_class="btn btn-danger"))
		wr_toolbar.append(toolbar)
	elif (row.parent==240):
		ajax = "ajax('%s', [], 'detai_gian_hang')"%(URL(c='plugin_sgd',f='act_move_folder',args=[folder_id],vars=dict(parent=241,folder=row.id)))
		toolbar = DIV(_class="btn-group ")
		toolbar.append(A('Gỡ gian hàng',_onclick=ajax,_class="btn btn-danger"))
		wr_toolbar.append(toolbar)
		
	toolbar = DIV(_class="btn-group ")
	ajax = "ajax('%s', [], 'detai_gian_hang')"%(URL(c='plugin_sgd',f='act_delete_folder',args=[folder_id]))
	toolbar.append(A('Xóa',_onclick=ajax,_class="btn btn-danger"))
	wr_toolbar.append(toolbar)
	cong_ty = cms.define_table('cong_ty')
	rows = cms.db(cong_ty.folder==row.id).select()
	danh_gia = 0
	if rows:
		if rows[0].danh_gia:
			danh_gia = rows[0].danh_gia
	toolbar = DIV(_class=" pull-right ")
	for i in [0,1,2,3,4,5]:
		ajax = "ajax('%s', ['',''], 'wr_alert')"%(URL(c='plugin_sgd',f='update_xep_hang',args=[rows[0].id,i]))
		if i == danh_gia:
			toolbar.append(A(i,_onclick=ajax,_class='active vote_item vote_item_%s'%(i)))
		else:
			toolbar.append(A(i,_onclick=ajax,_class='vote_item vote_item_%s'%(i)))
	# ajax = "ajax('%s', ['',''], '')"%(URL(c='plugin_sgd',f='update_xep_hang',args=[rows[0].id,0]))
	# toolbar.append(A('1',_onclick=ajax,_class='vote_item vote_item_1'))
	# toolbar.append(A('2',_href='',_class='vote_item vote_item_2'))
	# toolbar.append(A('3',_href='',_class='vote_item vote_item_3'))
	# toolbar.append(A('4',_href='',_class='vote_item vote_item_4'))
	# toolbar.append(A('5',_href='',_class='vote_item vote_item_5'))
	
	toolbar.append(DIV(_id='wr_alert'))
	wr_toolbar.append(toolbar)
	div_body.append(wr_toolbar)
	
	ul_na = UL(_class='nav nav-tabs',**{'_role':'tablist'})
	
	# ul_na.append(LI(A('Thông tin chi tiết',_href="#tab1",**{'_aria-controls':'tab1', '_role':'tab','_data-toggle':'tab'}),_class='active'))
	# ul_na.append(LI(A('Sản phẩm',_href="#tab2",**{'_aria-controls':'tab2', '_role':'tab','_data-toggle':'tab'})))
	
	ul_na.append(LI(A('Xem trước gian hàng',_href="#tab4",**{'_aria-controls':'tab4', '_role':'tab','_data-toggle':'tab'}),_class='active'))
	ul_na.append(LI(A('Quản trị người dùng',_href="#tab3",**{'_aria-controls':'tab3', '_role':'tab','_data-toggle':'tab'})))
	ul_na.append(LI(A('Thống kê đánh giá',_href="#tab5",**{'_aria-controls':'tab5', '_role':'tab','_data-toggle':'tab'})))
	div_body.append(ul_na)
	div_content = DIV(_class="tab-content")
	from plugin_cong_ty import add_cong_ty
	# div_content.append(DIV('Thông tin về công ty',DIV(_class='clearfix'),_class='tab-pane active',_id='tab1'))
	# # div_content.append(DIV(add_cong_ty(folder_id),DIV(_class='clearfix'),_class='tab-pane',_id='tab1'))
	# div_content.append(DIV('List sản phẩm của gian hàng',_class='tab-pane',_id='tab2'))
	# div_content.append(DIV('List bài viết của gian hàng',_class='tab-pane',_id='tab3'))
	div_content.append(DIV(IFRAME(_src=URL(c='portal',f='folder',args=[row.name],vars=dict(page='quan-ly-gian-hang')),_name="mainwindow",_frameborder="no",_style="width: 100%;min-height: 600px;"),_class='tab-pane active',_id='tab4'))
	div_content.append(DIV(wr_user(row.name),_class='tab-pane',_id='tab3'))
	div_content.append(DIV('Báo cáo, thống kê đánh giá',_class='tab-pane',_id='tab5'))
	div_body.append(div_content)
	div.append(div_body)
	response.view = 'plugin_sgd/content.%s'%request.extension
	return dict(content=div)
	
def update_xep_hang():
	id = request.args(0)
	cong_ty = cms.define_table('cong_ty')
	# cong_ty[id].update(danh_gia=request.args(1))
	cms.db(cong_ty.id==id).update(danh_gia=request.args(1))
	return 'Cập nhật thành công'
	

def wr_user(folder_name):
	div = DIV(_class='row')
	div.append(DIV(A(T('Thêm người dùng'),_class='btn btn-danger',_href=URL(c='plugin_auth',f='users.html')),_class='col-md-12'))
	
	
	from plugin_process import ProcessModel
	db_auth = ProcessModel().db
	# rows = db_auth((db_auth.auth_user.auth_group==8)).select()
	# if len(rows)>0:
		# div2 = DIV(H2(T('Danh sách khách hàng')))
		# table = TABLE(_class='table-bordered')
		# table.append(TR(TH('Stt',_style='with:30px;'),TH(T('Họ tên')),TH(T('Email')),TH(T('Ngày tham gia'))))
		# i = 1
		# for row in rows:
			# tr = TR()
			# tr.append(TD(i))
			# name = row.last_name +' '+row.first_name
			# tr.append(TD(A(name)))
			# tr.append(TD(row.email))
			# tr.append(TD(row.created_on))
			# i+=1
			# table.append(tr)
		# div2.append(table)
	# div.append(DIV(div2,_class='col-md-5'))
	# div.append(DIV(A(T('Thêm vào'),SPAN(_class='glyphicon glyphicon-chevron-right'),_class='btn btn-default',_href=URL(c='plugin_auth',f='users.html')),_class='col-md-2'))
	div.append(DIV(list_user(folder_name),_class='col-md-12'))
	return div
	
def list_user(folder_name):
	from plugin_process import ProcessModel
	db_auth = ProcessModel().db
	rows = db_auth((db_auth.auth_membership.group_id==db_auth.auth_group.id)&(db_auth.auth_group.role=='gian-hang-%s'%(folder_name))).select()
	if len(rows)>0:
		div = DIV(H2(T('Danh sách quản trị gian hàng')))
		table = TABLE(_class='table-bordered')
		table.append(TR(TH('Stt',_style='with:30px;'),TH(T('Họ tên')),TH(T('Email')),TH(T('Ngày tham gia'))))
		i = 1
		for row in rows:
			tr = TR()
			tr.append(TD(i))
			name = row.auth_membership.user_id.last_name +' '+row.auth_membership.user_id.first_name
			tr.append(TD(A(name, _href=URL(c='plugin_auth',f='users.html',args=[row.auth_membership.user_id]))))
			tr.append(TD(row.auth_membership.user_id.email))
			tr.append(TD(row.auth_membership.user_id.created_on))
			i+=1
			table.append(tr)
		div.append(table)
		return div
	else:
		return T('Chưa có người dùng.')
	
def act_move_folder():
	id = request.vars.folder
	parent = request.vars.parent
	div = DIV()
	if id:
		folder = cms.define_folder()
		cms.db(folder.id==id).update(parent=parent)
		response.flash = T('Cập nhật thành công')
	else:
		response.flash = T('Cập nhật lỗi.')
	return detai_gian_hang()
	
def act_delete_folder():
	if request.args(0):
		folder = cms.define_folder()
		folder_d = cms.db.folder[request.args(0)]
		name = folder_d.name
		id = cms.db(cms.db.folder.id== request.args(0)).delete()
		if id:
			from plugin_process import ProcessModel
			processmodel = ProcessModel()
			role = 'gian-hang-'+str(name)
			processmodel.db((processmodel.db.auth_permission.record_id==request.args(0))&(processmodel.db.auth_permission.name=='quan_tri_gian_hang')&(processmodel.db.auth_permission.table_name=='folder')).delete()
			processmodel.db(processmodel.db.auth_group.role==role).delete()
		response.flash = T('Xóa thành công.')
	scr ='''<script type="text/javascript">
			$('#exampleModal').modal('hide')
		</script>
		'''
	return XML(scr)
# END GIAN HANG
# START ADS


def ads():
	return dict(content='')
	
def ads_img():
	div = DIV(_id='gian_hang',_class='panel panel-default')
	div.append(DIV(T('Quảng cáo banner'),_class='panel-heading'))
	table = 'ads_img'
	cms.define_table(table,True)
	content = SQLFORM.grid(cms.db[table])
	div.append(DIV(content,_class='panel-body'))
	response.view = 'plugin_sgd/ads.%s'%request.extension
	return dict(content=div)
	
def ads_product():
	div = DIV(_id='ads_product',_class='panel panel-default')
	div.append(DIV(T('Quảng cáo sản phẩm'),_class='panel-heading'))
	# content = TABLE(_class='table table-hover table-bordered',_id="view_ads")
	# content.append(TR(TH('Sản phẩm'),TH('Loại quảng cáo'),TH('Thời gian bắt đầu'),TH('Thời gian kết thúc'),TH('Người đại diện')))
	# ads_product = cms.define_table('ads_product',True)
	# rows = cms.db(ads_product.id>0).select()
	# for row in rows:
		# ul =UL()
		# for type in row.r_ads_product_type:
			# ul.append(LI(type.name))
		# product = DIV()
		# product.append(DIV(cms.get_images_content('san_pham',row.r_product.avatar),_class='ads_product_image'))
		# product.append(row.r_product.name)
		# product.append('Gian hàng: ',A(row.r_product.name,_href=URL(c='',f='')))
		# content.append(TR(TD(product),TD(ul),TD(row.time_start),TD(row.time_end),TD(row.htmlcontent)))
	table = 'ads_product'
	cms.define_table(table,True)
	ads_product = cms.db[table]
	from plugin_app import widget_san_pham
	ads_product.r_san_pham.widget = widget_san_pham
	content = SQLFORM.grid(ads_product)
	div.append(DIV(content,_class='panel-body'))
	response.view = 'plugin_sgd/ads.%s'%request.extension
	return dict(content=div)
	
def edit_box():
	div = DIV(_id='ads_product',_class='panel panel-default')
	div.append(DIV(T('Quảng cáo'),_class='panel-heading'))
	box = cms.define_box()
	from plugin_ckeditor import CKEditor
	box.htmlcontent.widget=CKEditor(cms.db).widget	
	box.boxtype.writable=False
	box.boxtype.readable=False
	
	box.name.writable=False
	
	box.avatar.writable=False
	box.avatar.readable=False
	
	box.link.writable=False
	box.link.readable=False
	
	box.setting.writable=False
	box.setting.readable=False
	
	box.textcontent.writable=False
	box.textcontent.readable=False
	
	form = SQLFORM(box,request.args(0))
	if form.process().accepted:
		response.flash = T('Cập nhật thành công')
	div.append(DIV(form,_class='panel-body'))
	response.view = 'plugin_sgd/ads.%s'%request.extension
	return dict(content=div)
	
def ads_page():
	div = DIV(_id='gian_hang',_class='panel panel-default')
	div.append(DIV(T('Quảng cáo gian hàng'),_class='panel-heading'))
	table = 'ads_img'
	cms.define_table(table,True)
	content = ''
	div.append(DIV(content,_class='panel-body'))
	response.view = 'plugin_sgd/ads.%s'%request.extension
	return dict(content=div)
	
	
# END ADS
def check_url():
	ten_url = request.vars.ten_url.lower()
	ten_gian_hang = request.vars.ten_gian_hang
	div = DIV()
	if ten_gian_hang != '':
		if ten_url != '':
			folder = cms.define_folder()
			rows = cms.db(folder.name==ten_url).count()
			if rows>0:
				div.append(DIV('Địa chỉ không hợp lệ',_class='alert alert-danger'))
				div.append(DIV(INPUT(_type='submit',_class='btn btn-primary',_value=T('Tạo gian hàng'),_disabled=True)))
			else:
				div.append(DIV('Địa chỉ hợp lệ',_class='alert alert-success'))
				ajax = "ajax('%s', ['ten_gian_hang','template'], 'wr_add_gian_hang')"%(URL(c='plugin_sgd',f='add_gian_hang_admin'))
				div.append(DIV(INPUT(_type='submit',_class='btn btn-primary',_value=T('Tạo gian hàng'),_onclick=ajax)))
		else:
			div.append(DIV('Địa chỉ không được trống',_class='alert alert-danger'))
			div.append(DIV(INPUT(_type='submit',_class='btn btn-primary',_value=T('Tạo gian hàng'),_disabled=True)))
	else:
		div.append(DIV('Chưa nhập tên gian hàng',_class='alert alert-danger'))
		div.append(DIV(INPUT(_type='submit',_class='btn btn-primary',_value=T('Tạo gian hàng'),_disabled=True)))	
	return  div
	
def check_url1():
	ten_url = request.vars.ten_url.lower()
	ten_gian_hang = request.vars.ten_gian_hang
	div = DIV()
	if ten_gian_hang != '':
		if ten_url != '':
			folder = cms.define_folder()
			rows = cms.db(folder.name==ten_url).count()
			if rows>0:
				div.append(DIV('Địa chỉ không hợp lệ',_class='alert alert-danger'))
				div.append(DIV(INPUT(_type='submit',_class='btn btn-primary',_id='btn_submit',_value=T('Tạo gian hàng'),_disabled=True)))
			else:
				div.append(DIV('Địa chỉ hợp lệ',_class='alert alert-success'))
				div.append(DIV(INPUT(_type='submit',_class='btn btn-primary',_id='btn_submit',_value=T('Tạo gian hàng'))))
		else:
			div.append(DIV('Địa chỉ không được trống',_class='alert alert-danger'))
			div.append(DIV(INPUT(_type='submit',_class='btn btn-primary',_id='btn_submit',_value=T('Tạo gian hàng'),_disabled=True)))
	else:
		div.append(DIV('Chưa nhập tên gian hàng',_class='alert alert-danger'))
		div.append(DIV(INPUT(_type='submit',_class='btn btn-primary',_id='btn_submit',_value=T('Tạo gian hàng'),_disabled=True)))	
	return  div


	
	

