# -*- coding: utf-8 -*-

from plugin_cms import Cms
cms = Cms()

# seconds = cms.get_lasttime()
# if seconds != request.vars.key:
	# vars = request.vars
	# vars["key"] = seconds
	# redirect(URL(args=request.args,vars=vars))
	
def index():
	redirect(URL(f='folder',args=request.args))
	
#@cache.action(time_expire=3600, cache_model=cache.disk, quick='SVP')
def folder():
	try:
		response.view = 'layout/%s'%(cms.layout_folder() or 'folder.html')
	except:
		response.view = 'layout/trangchu.html'
	return response.render(dict())
	
#@cache.action(time_expire=3600, cache_model=cache.disk, quick='SVP')
def read():
	try:
		response.view = 'layout/%s'%(cms.layout() or 'content.html')
	except:
		response.view = 'layout/trangchu.html'
	return response.render(dict())	
	
	
def search():
	dcontent = cms.define_table(tablename ='dcontent')
	txt = request.vars.key_search
	search_folder = request.args(0)
	if request.vars.search_select:
		search_folder = request.vars.search_select
	query = dcontent.textcontent.like('%'+str(txt)+'%')
	if search_folder:
		from plugin_cms import CmsFolder
		folder = CmsFolder().get_folder(search_folder)
		query &= (dcontent.folder.belongs(CmsFolder().get_folders(folder)))
	rows= cms.db(query).select()
	
	div = DIV(_id='list_news')
	
	if len(rows)>0:
		div.append(H2(len(rows),T(' Kết quả tìm kiếm cho từ khóa: "'),request.vars.key_search,'"',_id='title_search_'))
		ul=UL(_class='wr_search')
		for row in rows:
			ulr_link =''
			if row.dtable == 'san_pham':
				san_pham = cms.define_table('san_pham')
				sp = cms.db.san_pham[row.table_id]
				if sp:
					ulr_link = URL(c='portal',f='read',args=[sp.r_folder.name if sp.r_folder else '','san_pham',sp.link])
			if row.dtable == 'cong_ty':
				cong_ty = cms.define_table('cong_ty')
				sp = cms.db.cong_ty[row.table_id]
				if sp:
					ulr_link = URL(c='portal',f='folder',args=[sp.folder.name])
			if row.dtable == 'tintuc':
				tintuc = cms.define_table('tintuc')
				sp = cms.db.tintuc[row.table_id]
				if sp:
					ulr_link = URL(c='portal',f='read',args=[sp.folder.name,'tintuc',sp.link])
			
			if row.dtable == 'doanh_nghiep':
				doanh_nghiep = cms.define_table('doanh_nghiep')
				sp = cms.db.doanh_nghiep[row.table_id]
				if sp:
					ulr_link = URL(c='portal',f='read',args=[sp.folder.name,'doanh_nghiep',sp.link])
					
			code = '<span style=" background: yellow;">'+request.vars.key_search+'</span>'
			name =  row.name.replace(request.vars.key_search,code)

			# name =  name.replace(request.vars.key_search.lower(),code)
			# name =  name.replace(request.vars.key_search.upper(),code)
			li = LI(A(XML(str(B(T('title_search_'+str(row.dtable))))+": "+name),_href=ulr_link,_class='name'))
			if row.description:
				description =  row.description.replace(request.vars.key_search,code)
				li.append(P(XML(description)))
			
			ul.append(li)
			
		div.append(ul)
	else:
		div.append(H2(T('Kết quả tìm kiếm từ khóa: "'),request.vars.key_search,'"',_id='title_page'))
		div.append(P(T('Không có kết quả nào cho từ khóa này.')))
		
	return div

def gian_hang_search():
	dcontent = cms.define_table(tablename ='dcontent')
	txt = request.vars.key_search
	search_folder = ''
	if request.vars.search_select:
		search_folder = request.vars.search_select
	query = dcontent.textcontent.like('%'+str(txt)+'%')
	if search_folder:
		from plugin_cms import CmsFolder
		folder = CmsFolder().get_folder(search_folder)
		query &= (dcontent.folder.belongs(CmsFolder().get_folders(folder)))
	rows= cms.db(query).select()
	
	div = DIV(_id='list_news')
	i = 0
	if len(rows)>0:
		
		ul=UL(_class='wr_search')
		for row in rows:
			ulr_link =''
			if row.dtable == 'san_pham':
				san_pham = cms.define_table('san_pham')
				sp = cms.db.san_pham[row.table_id]
				
				if sp:
					if sp.r_folder.name == request.args(0):
						ulr_link = URL(c='portal',f='read',args=[sp.r_folder.name,'san_pham',sp.link])
						code = '<i style=" background: yellow;">'+request.vars.key_search+'</i>'
						name =  row.name.replace(request.vars.key_search,code)

						name =  name.replace(request.vars.key_search.lower(),code)
						name =  name.replace(request.vars.key_search.upper(),code)
						li = LI(A(XML(str(B(T('title_search_'+str(row.dtable))))+": "+name),_href=ulr_link,_class='name'))
						description =  row.description.replace(request.vars.key_search,code)
						li.append(P(XML(description)))
						ul.append(li)
						i+=1

			if row.dtable == 'cong_ty':
				print 'cong ty'
				# cong_ty = cms.define_table('cong_ty')
				# sp = cms.db.cong_ty[row.table_id]
				# if sp:
					# if sp.folder.name == request.args(0):
						# ulr_link = URL(c='portal',f='folder',args=[sp.folder.name])
						# code = '<i style=" background: yellow;">'+request.vars.key_search+'</i>'
						# name =  row.name.replace(request.vars.key_search,code)

						# name =  name.replace(request.vars.key_search.lower(),code)
						# name =  name.replace(request.vars.key_search.upper(),code)
						# li = LI(A(XML(str(B(T('title_search_'+str(row.dtable))))+": "+name),_href=ulr_link,_class='name'))
						# description =  row.description.replace(request.vars.key_search,code)
						# li.append(P(XML(description)))
						# ul.append(li)
						# i+=1

			if row.dtable == 'tintuc':
				tintuc = cms.define_table('tintuc')
				sp = cms.db.tintuc[row.table_id]
				if sp:
					if sp.folder.name == request.args(0):
						ulr_link = URL(c='portal',f='read',args=[sp.folder.name,'tintuc',sp.link])
						code = '<i style=" background: yellow;">'+request.vars.key_search+'</i>'
						name =  row.name.replace(request.vars.key_search,code)

						name =  name.replace(request.vars.key_search.lower(),code)
						name =  name.replace(request.vars.key_search.upper(),code)
						li = LI(A(XML(str(B(T('title_search_'+str(row.dtable))))+": "+name),_href=ulr_link,_class='name'))
						description =  row.description.replace(request.vars.key_search,code)
						li.append(P(XML(description)))
						ul.append(li)
						i+=1
		div.append(H2(i,T(' Kết quả tìm kiếm cho từ khóa: "'),request.vars.key_search,'"',_id='title_search_'))
		div.append(ul)
	else:
		div.append(H2(T('Kết quả tìm kiếm từ khóa: "'),request.vars.key_search,'"',_id='title_page'))
		div.append(P(T('Không có kết quả nào cho từ khóa này.')))
		
	return div				
				
def hoi_dap():
	forlder_id = cms.get_folder(request.args(0))
	hoi_dap = cms.define_table(tablename ='hoi_dap',migrate=True)

	hoi_dap.folder.writable=False
	hoi_dap.folder.readable=False
	hoi_dap.folder.default=forlder_id 

	hoi_dap.avatar.writable=False
	hoi_dap.avatar.readable=False
	hoi_dap.avatar.default=' ' 

	hoi_dap.htmlcontent.writable=False
	hoi_dap.htmlcontent.readable=False

	from gluon.tools import Recaptcha
	public_key='6LdtT_YSAAAAALCH4vbHKl1yjqvhB80JZh1J21Lv'
	private_key='6LdtT_YSAAAAAI6XnBMNNWwSkJeSYtbP_-kW5HUH' ### provided by recaptcha.net

	from gluon.tools import Crud
	crud = Crud(cms.db)
	crud.settings.captcha =  Recaptcha(request,public_key,private_key,options = "lang:'en', theme:'clean'")
	form=crud.create(hoi_dap) 

	# form[0].insert(-1, TR('', Recaptcha(request,public_key,private_key,options = "lang:'en', theme:'clean'"))) 

	if form.process().accepted:
		
		from plugin_process import ProcessModel
		process = ProcessModel()
		objects = process.define_objects(True)
		log     = process.define_process_log(True)

		objects_id =objects.insert(folder=forlder_id ,tablename='hoi_dap',table_id=form.vars.id ,process=2)
		log.insert(objects=objects_id, process=2)
		response.flash=T('done!')
		# scr ='''<script type="text/javascript"> 
   				# setInterval("location.reload();",1000);
			# </script>'''
		# form.append(XML(scr))
	# if form.errors:
		# response.flash=T('Loi nhap du lieu!')
		# scr ='''<script type="text/javascript"> 
   				# setInterval("location.reload();",1000);
			# </script>'''
		# form.append(XML(scr))
	div = DIV(_id='hoi_dap')
	div.append(DIV(H2('Nhập câu hỏi',_class="title_box"),_class="tinlienquan"))
	div.append(form)
	response.view = 'layout/hoi_dap_13.html'
	return dict(content=div)
	

def form_y_kien_du_thao():
	vb_du_thao=request.vars.vbdt
	div = DIV(_id='hoi_dap')
	div.append(DIV(H2('Gửi ý kiến đóng góp',_class="title_box"),_class="tinlienquan"))
	
	from gluon.tools import Recaptcha
	public_key='6LdtT_YSAAAAALCH4vbHKl1yjqvhB80JZh1J21Lv'
	private_key='6LdtT_YSAAAAAI6XnBMNNWwSkJeSYtbP_-kW5HUH' ### provided by recaptcha.net
	
	gop_y_du_thao = cms.define_table(tablename ='gop_y_du_thao',migrate=True)
	gop_y_du_thao.r_gop_y_du_thao.writable=False
	gop_y_du_thao.r_gop_y_du_thao.readable=False
	gop_y_du_thao.r_gop_y_du_thao.default=vb_du_thao
	from gluon.tools import Crud
	crud = Crud(cms.db)


	form=crud.create(gop_y_du_thao) 
	form[0].insert(-1, TR('', Recaptcha(request,public_key,private_key,options = "lang:'en', theme:'clean'"))) 
	div.append(form)
	return div


def feed():
	from plugin_cms import CmsFolder
	folder_id = CmsFolder().get_folder()
	ar_entries =[]
	entries =  CmsFolder().get_rows(folder=request.args(0))
	link_page='http://'+request.env.http_host
	for entry in entries:
		link = CmsFolder().url_content(entry)
		description = str(entry.description)
		if entry.avatar:
			description = '<a href="'+link_page + str(link)+'"><img>'+str(entry.avatar) +'</img></a>'+ description
		ar_entries.append(dict(title = entry.name.decode('utf-8'),
			link = link_page + str(link),
			description=XML(description.decode('utf-8')),
			created_on = entry.publish_on))
	return ''
	return dict(title='SOYTE FEED',link=link_page,description='SOYTE.HATINH.GOV.VN', created_on = request.now,entries=ar_entries )
	

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
		row  = db((db.san_pham.id==cart['id'])).select().first()
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
	div.append(A('Gửi đơn hàng',_href=URL(c='portal',f='folder',args=['checkout']),_class='btn btn-success'))
	return div
	
def add_cart_r_number():
	pid = request.vars.pid
	ar_carts =[]
	num_carts = 0
	if request.cookies.has_key ('cart_shop'):
		carts = eval(request.cookies['cart_shop'].value)
		i=0
		
		for cart in carts:
			num_carts +=1
			cart = eval(cart)
			if cart['id']==pid:
				ar_carts.append(str({'id':str(cart['id']) ,'num':str(int(cart['num'])+1)}))
				i+=1
			else:
				ar_carts.append(str({'id':str(cart['id']) ,'num':str(cart['num'])}))
		if i==0:
			num_carts +=1
			ar_carts.append(str({'id':pid ,'num':str(1)}))
	else:
		ar_carts.append(str({'id':pid ,'num':str(1)}))
		num_carts +=1
		
	response.cookies['cart_shop'] = str(ar_carts) 
	response.cookies['cart_shop']['expires'] = 24 * 3600
	response.cookies['cart_shop']['path'] = '/'
	response.flash = T("Add new cart!")
	
	# load view_carts() nhung ko request duoc cookies moi
	
	cache.ram.clear(None)
	div = SPAN(num_carts,_class="badge")
	if num_carts !=0:
		return div
	else: return ''
	
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
				# row  = db((db.san_pham.id==cart['id'])&(db.san_pham.r_folder== CmsFolder().get_folder(request.args(0)))).select().first()
				row  = db((db.san_pham.id==cart['id'])).select().first()
				if row:
					div1 = DIV(_class='list_cart')
					ul = UL()
					ul.append(LI(row.name))
					ul.append(LI(SPAN('Số lượng: '),cart['num']))
					ul.append(LI(SPAN('Giá: '),number_format(row.gia_san_pham),' VNĐ'))
					div1.append(DIV(cms.get_images_content('san_pham',row.avatar),_class='col-md-4 box_ivinh'))
					div1.append(DIV(ul,_class='col-md-8 box_ivinh'))
					
					div.append(div1)
					div.append(HR())
					tong_tien += int(row.gia_san_pham)* int(cart['num'])
					num_car +=1
		if num_car>0:			
			p_tong = DIV(SPAN('Tổng tiền: '))
			p_tong.append(str(number_format(tong_tien))+' VNĐ')
			div.append(B(p_tong,_class='text-right'))
			div.append(A('Gửi đơn hàng',_href=URL(c='portal',f='folder',args=['checkout']),_class='btn btn-success'))
		else:
			div.append('Giỏ hàng trống')
	except Exception,e: 
		return e
	return div
	
def view_order():
	div = DIV(_id="view_order")
	num_car = 0
	tong_tien = 0
	carts =''
	if request.cookies.has_key('cart_shop'):
		carts = eval(request.cookies['cart_shop'].value)
		from plugin_cms import CmsModel
		from plugin_cms import CmsFolder
		cms = CmsModel()
		db = cms.db
		cms.define_table('san_pham')
		from plugin_app import number_format
		table = TABLE(_class='table')
		
		table.append(TR(TH('Sản phẩm'),TH('Số lượng'),TH(''),TH('Giá'),TH(B('Thành tiền'))))
        for cart in carts:
			cart = eval(cart)
			row  = db((db.san_pham.id==cart['id'])&(db.san_pham.folder== CmsFolder().get_folder(request.args(0)))).select().first()
			if row:
				tong_tien += int(row.gia_san_pham)* int(cart['num'])
				input_num = INPUT(_type='text',_value=cart['num'])
				table.append(TR(TD(row.name,': '),TD(input_num),TD(' * '),TD(number_format(row.gia_san_pham),' VNĐ'),TD(B(number_format(tong_tien),' VNĐ'))))
				div.append(table)
				num_car +=1
	p_tong = DIV(SPAN('Tổng tiền: '))
	p_tong.append(str(number_format(tong_tien))+' VNĐ')
	div.append(B(p_tong,_class='text-right'))
	
	form = FORM()
	div1 = DIV(_class="form-group")
	div1.append(LABEL('Họ và tên'))
	div1.append(INPUT(_type='text',_class="form-control",_placeholder="Họ và tên" ))
	form.append(div1)
	
	div1 = DIV(_class="form-group")
	div1.append(LABEL('Email'))
	div1.append(INPUT(_type='text',_class="form-control",_placeholder="Email"))
	form.append(div1)
	
	div1 = DIV(_class="form-group")
	div1.append(LABEL('Điện thoại'))
	div1.append(INPUT(_type='text',_class="form-control",_placeholder="Điện thoại"))
	form.append(div1)
	
	div1 = DIV(_class="form-group")
	div1.append(LABEL('Địa chỉ nhận hàng'))
	div1.append(INPUT(_type='text',_class="form-control",_placeholder="Địa chỉ nhận hàng"))
	form.append(div1)
	
	div1 = DIV(_class="form-group")
	div1.append(LABEL('Lời nhắn'))
	div1.append(TEXTAREA(_class="form-control",_rows="3",_placeholder="Lời nhắn"))
	form.append(div1)
	
	div1 = DIV(_class="form-group")
	div1.append(LABEL('Lời nhắn'))
	div1.append(TEXTAREA(_class="form-control",_rows="3",_placeholder="Lời nhắn"))
	form.append(div1)
	
	ajax = "ajax('%s', [], 'order_view')"%(URL(f='act_add_cart',args=request.args))
	form.append(A('Gửi đặt hàng',_onclick=ajax, _class='btn btn-success'))
	div.append(form)
	return div


	
def act_add_cart():
	response.cookies['cart_shop'] = 'invalid' 
	response.cookies['cart_shop']['expires'] = -10 
	response.cookies['cart_shop']['path'] = '/' 
	div = DIV(B('Đặt hàng thành công. Chúng tôi sẽ liên hệ với bạn trong thời gian sớm nhất để xác nhận đơn hàng. Xin cảm ơn! '),_class='bg-info text-center' )
	div.append(DIV(BR(),'Chuyển hướng về trang chủ sau 3 giây.',_class='bg-info text-center' ))
	scr ='''
	 <META http-equiv="refresh" content="3;URL=%s">
	'''%(URL(c='portal',f='folder',args=request.args(0)))
	div.append(XML(scr))
	
	return div
	
def style_list():
	response.cookies['style_id_sgd'] =  request.args(0)
	response.cookies['style_id_sgd']['expires'] = 24 * 3600
	response.cookies['style_id_sgd']['path'] = '/'
	response.flash = T("Đổi giao diện thành công!")
	return ''
	
def style_layout():
	style_layout =  request.args(0)
	if request.args(0)=='layout-boxed':
		style_layout +=' container' 
	response.cookies['style_layout'] =  style_layout
	response.cookies['style_layout']['expires'] = 24 * 3600
	response.cookies['style_layout']['path'] = '/'
	response.flash = T("Đổi bố cục thành công!")
	return ''
	

def add_gian_hang():
	print request.vars.ten_gian_hang
	print request.vars.template
	return 'Thêm thành công'
	
def tao_tin_tim_mua():
	from plugin_ckeditor import CKEditor
	table = cms.define_table('tintuc')
	for field in table.fields:
		if field == 'htmlcontent':
			table[field].label = 'Nội dung tìm mua'
		if field == 'folder':
			table[field].default = 248
			table[field].readable=False
			table[field].writable=False
		row = db(db.dfield.name==field).select().first()
		if row:
			if row.ckeditor: table[field].widget=CKEditor(db).widget		
	form=SQLFORM(table)
	if form.process().accepted:
		from plugin_process import ProcessModel
		objects = ProcessModel().define_objects()
		objects_id = objects.insert(folder=248,foldername='san-pham-tim-mua',tablename='tintuc',table_id=form.vars.id,auth_group=7,process=1)

		# link = form.vars.name.replace('đ','d')
		# link = '%s.html'%IS_SLUG.urlify(link)
		# dcontent = cms.define_dcontent()
		# dcontent.insert(folder=248,dtable='tintuc',table_id=form.vars.id,link=link,name=form.vars.name,avatar=form.vars.avatar,description=form.vars.description,publish_on=request.now,expired_on=None)	
		# cms.db(tin_tuc_edit.id==form.vars.id).update(link=link)
		session.flash = T('Gửi thông tin tìm mua thành công')
		redirect(URL(c='portal',f='folder',args=['san-pham-tim-mua']))
	response.view = 'layout/home_dang_tin-tim-mua.html'	
	return dict(content=form)		
	
