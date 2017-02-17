# -*- coding: utf-8 -*-
###################################################
# This file was developed by Anhnt
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 12/01/2015
###################################################

import os

	
def history():
	from plugin_process import ProcessModel
	processmodel = ProcessModel()
	auth = processmodel.auth
	db = processmodel.db
	query =(db.auth_event.id>0)
	rows  = db(query).select()
	content = DIV(_class='panel panel-default',_id='wrapper_history')
	content.append(DIV(A(SPAN(T('Lịch sử truy cập'))),_class='panel-heading'))
	table = TABLE(_class='table',_id='history')
	table.append(TR(TH(T('Stt'),_class='stt'),TH(T('User event'),_class='user_event'),TH(T('Content event'),_class='content_event'),TH(T('Time event'),_class='time_event'),TH(T('ip connect'),_class='ip_connect')))
	i = 1
	for row in rows:
		table.append(TR(TD(i),TD(row.user_id.last_name,' ',row.user_id.first_name),TD(row.description),TD(row.time_stamp.strftime("%d/%m/%Y") ),TD(row.client_ip)))
		i+=1
	input = A(T('Delete all history'),_href=URL(c='plugin_report',f='clear_all_history.load'),_class='btn btn-danger')
	content.append(DIV(input,_class='btn-group'))
	content.append(DIV(table))
	response.view = 'plugin_report/content.%s'%request.extension
	return dict(content=content)
	
def report():
	return dict()
	
	
def clear_all_history():
	from plugin_process import ProcessModel
	processmodel = ProcessModel()
	auth = processmodel.auth
	db = processmodel.db
	db(db.auth_event.id>0).delete()
	redirect(URL(c='plugin_report',f='history.html'))
	
def giao_dich():
	import datetime
	don_hang = cms.define_table('don_hang')
	start_time = request.vars.start_time or datetime.datetime.now().strftime("%Y-%m-%d 00:00:00")
	end_time = request.vars.end_time or datetime.datetime.now().strftime("%Y-%m-%d 23:59:00")
	rows = cms.db((don_hang.tao_luc >= start_time)&(don_hang.tao_luc <= end_time)).select(orderby=~cms.db.don_hang.id)
	div = DIV(_class="panel panel-default giao_dich")
	div.append(DIV(SPAN(T('Quản lý đơn hàng'),_class='pull-left title_name'),SPAN(search_date(),_class='pull-right'),_class="panel-heading"))
	table = TABLE(_class='table',_id='giao_dich')
	table.append(TR(TH('STT',_style="width: 50px; text-align: center;"),TH(T('Người nhận ')),TH(T('Số điện thoại')),TH(T('Địa chỉ')),TH(T('Lời nhắn'))))
	j= 1
	for row in rows:
		i = row.id
		link = A(SPAN(_class='glyphicon glyphicon-collapse-down on_show'),_href="#dh_%s"%(i),**{'_data-toggle':"collapse" ,'_data-parent':"#giao_dich",'_aria-expanded':"false",'_aria-controls':"dh_%s"%(i)})
		table.append(TR(TD(link,SPAN(j),_style="width: 50px; text-align: center;"),TD(row.nguoi_nhan_hang),TD(row.dien_thoai),TD(row.dia_chi),TD(row.loi_nhan)))
		table.append(TR(TD(_colspan=5,_style='border-top:none;padding:0;',_class='collapse' ,_id='dh_%s'%(i))))
		j+=1
	url = URL(c='plugin_report',f='view_xls.xls',vars= request.vars)
	div_body = DIV(_class='panel-body')
	div_body.append(table)
	if len(rows)>0:
		
		div_body.append(H3('Có tổng ' +str(len(rows)) + ' đơn hàng'))
	else:
		div_body.append(H3('Không có đơn hàng nào.'))
		
		
	div_bottom = DIV(_class='input-group ')
	div_bottom.append(A('Xuất excel đơn hàng',_class='btn btn-success',_href=url))
	
	url = URL(c='plugin_report',f='view_xls.xls',args=['chitiet'],vars= request.vars)
	div_bottom.append(A('Xuất excel đơn hàng kèm chi tiết',_class='btn btn-success',_href=url))
	
	div_body.append(div_bottom)
	
	div.append(div_body)
	scr ='''<script type="text/javascript"> 
	
    $(".collapse").on('show.bs.collapse', function(){
		var de_id = $(this).attr('id')
		var id= de_id.replace("dh_", "");
		url = 's'
		ajax('%s/'+id, [''], de_id)
    });
	</script>'''%(URL(f='giao_dich_chi_tiet'))
	div.append(XML(scr))
	response.view = 'plugin_report/content.%s'%request.extension
	return dict(content=div)	
	
def giao_dich_chi_tiet():
	id = request.args(0)
	don_hang_item = cms.define_table('don_hang_item')
	san_pham = cms.define_table('san_pham')
	rows = cms.db(don_hang_item.r_don_hang ==id).select()
	table = TABLE(_class='table')
	table.append(TR(TH(T('Gian hàng')),TH(T('Tên sản phẩm')),TH(T('Số lượng')),TH(T('Giá bán'))))
	for row in rows:
		sp = san_pham[row.r_san_pham]
		table.append(TR(TD(sp.r_folder.label),TD(sp.name),TD(row.so_luong),TD(row.gia_ban)))
		
	return table
	
def san_pham():
	import datetime
	div = DIV(_class="panel panel-default giao_dich")
	div.append(DIV(SPAN(T('Sản phẩm mới'),_class='pull-left title_name'),SPAN(search_date(),_class='pull-right'),_class="panel-heading"))
	san_pham = cms.define_table('san_pham')
	start_time = request.vars.start_time or datetime.datetime.now().strftime("%Y-%m-%d 00:00:00")
	end_time = request.vars.end_time or datetime.datetime.now().strftime("%Y-%m-%d 23:59:00")
	rows = cms.db((san_pham.tao_luc >= start_time)&(san_pham.tao_luc <= end_time)).select(orderby=~cms.db.san_pham.id)
	
	table = TABLE(_class='table',_id='san_pham')
	table.append(TR(TH('STT',_style="width: 50px; text-align: center;"),TH(T('Gian hàng ')),TH(T('Tên sản phẩm')),TH(T('Mã sản phẩm')),TH(T('Giá bán'))))
	i=1
	folder = cms.define_folder()
	for row in rows:
		row_fol = cms.db.folder(row.r_folder)
		table.append(TR(TD(i,_style="width: 50px; text-align: center;"),TD(row_fol.label if row_fol else ''),TD(row.name),TD(row.code_name),TD(row.gia_san_pham) ))
		i+=1
	
	div_body = DIV(_class='panel-body')
	div_body.append(table)
	
	div_bottom = DIV(_class='input-group ')
	div_bottom.append(A('Xuất excel',_class='btn btn-success',_id='ex_button'))
	div_body.append(div_bottom)
	
	div.append(div_body)	
	scr ='''<script type="text/javascript"> 
		$("#ex_button").click(function(){
			$("#san_pham").table2excel({
				exclude: ".noExl",
				name: "San pham ban nhieu"

			});
		});

  
	</script>'''
	div.append(XML(scr))
	
	response.view = 'plugin_report/content.%s'%request.extension
	return dict(content=div)
	
def san_pham_xem_nhieu():
	import datetime
	div = DIV(_class="panel panel-default giao_dich")
	div.append(DIV(SPAN(T('Sản phẩm xem nhiều'),_class='pull-left title_name'),SPAN(search_date(),_class='pull-right'),_class="panel-heading"))
	san_pham = cms.define_table('san_pham')
	start_time = request.vars.start_time or datetime.datetime.now().strftime("%Y-%m-%d 00:00:00")
	end_time = request.vars.end_time or datetime.datetime.now().strftime("%Y-%m-%d 23:59:00")
	
	
	table = cms.define_readcontent()
	count = table.link.count()
	# query = (table.foldername==foldername) if foldername else table.id>0
	query =  table.created_on >= start_time
	query &= table.created_on <= end_time
	rows = cms.db(query).select(table.link, count, groupby=table.link,  orderby=~count)
	
	table = TABLE(_class='table',_id='san_pham')
	table.append(TR(TH('STT',_style="width: 50px; text-align: center;"),TH(T('Gian hàng ')),TH(T('Tên sản phẩm')),TH(T('Mã sản phẩm')),TH(T('Giá bán')),TH(T('Số lượt xem'))))
	i=1
	folder = cms.define_folder()
	for pr in rows:
		try:
			row = cms.get_row('san_pham',pr['readcontent']['link'])
			row_fol = cms.db.folder(row.r_folder)
			table.append(TR(TD(i,_style="width: 50px; text-align: center;"),TD(row_fol.label if row_fol else ''),TD(row.name),TD(row.code_name),TD(row.gia_san_pham),TD(pr['_extra']['COUNT(readcontent.link)'],_style="text-align: center;") ))
			i+=1
		except Exception,e: 
			print e
	div_body = DIV(_class='panel-body')
	div_body.append(table)
	
	div_bottom = DIV(_class='input-group ')
	div_bottom.append(A('Xuất excel',_class='btn btn-success',_id='ex_button'))
	div_body.append(div_bottom)
	
	div.append(div_body)	
	scr ='''<script type="text/javascript"> 
		$("#ex_button").click(function(){
			$("#san_pham").table2excel({
				exclude: ".noExl",
				name: "San pham ban nhieu"

			});
		});

  
	</script>'''
	div.append(XML(scr))
	
	response.view = 'plugin_report/content.%s'%request.extension
	return dict(content=div)	
	
def san_pham_mua_nhieu():
	import datetime
	div = DIV(_class="panel panel-default giao_dich")
	div.append(DIV(SPAN(T('Sản phẩm mua nhiều'),_class='pull-left title_name'),SPAN(search_date(),_class='pull-right'),_class="panel-heading"))
	san_pham = cms.define_table('san_pham')
	start_time = request.vars.start_time or datetime.datetime.now().strftime("%Y-%m-%d 00:00:00")
	end_time = request.vars.end_time or datetime.datetime.now().strftime("%Y-%m-%d 23:59:00")
	
	
	table =  cms.define_table('don_hang_item')
	count = table.r_san_pham.count()
	# query = (table.foldername==foldername) if foldername else table.id>0
	query =  table.tao_luc >= start_time
	query &= table.tao_luc <= end_time
	rows = cms.db(query).select(table.r_san_pham, count, groupby=table.r_san_pham,  orderby=~count)
	
	table = TABLE(_class='table',_id='san_pham')
	table.append(TR(TH('STT',_style="width: 50px; text-align: center;"),TH(T('Gian hàng ')),TH(T('Tên sản phẩm')),TH(T('Mã sản phẩm')),TH(T('Giá bán')),TH(T('Số lượt mua'))))
	i=1
	folder = cms.define_folder()
	for pr in rows:
		row = cms.db(san_pham.id==pr['don_hang_item']['r_san_pham']).select().first()
		row_fol = cms.db.folder(row.r_folder)
		table.append(TR(TD(i,_style="width: 50px; text-align: center;"),TD(row_fol.label if row_fol else ''),TD(row.name),TD(row.code_name),TD(row.gia_san_pham),TD(pr['_extra']['COUNT(don_hang_item.r_san_pham)'],_style="text-align: center;") ))
		i+=1
	
	div_body = DIV(_class='panel-body')
	div_body.append(table)
	
	div_bottom = DIV(_class='input-group ')
	div_bottom.append(A('Xuất excel',_class='btn btn-success',_id='ex_button'))
	div_body.append(div_bottom)
	
	div.append(div_body)	
	scr ='''<script type="text/javascript"> 
		$("#ex_button").click(function(){
			$("#san_pham").table2excel({
				exclude: ".noExl",
				name: "San pham ban nhieu"

			});
		});

  
	</script>'''
	div.append(XML(scr))
	
	response.view = 'plugin_report/content.%s'%request.extension
	return dict(content=div)	
	
def thanh_vien_moi():
	import datetime
	div = DIV(_class="panel panel-default giao_dich")
	div.append(DIV(SPAN(T('Thành viên mới đăng ký'),_class='pull-left title_name'),SPAN(search_date(),_class='pull-right'),_class="panel-heading"))

	start_time = request.vars.start_time or datetime.datetime.now().strftime("%Y-%m-%d 00:00:00")
	end_time = request.vars.end_time or datetime.datetime.now().strftime("%Y-%m-%d 23:59:00")
	
	from plugin_process import ProcessModel
	processmodel = ProcessModel()
	auth = processmodel.auth
	db = processmodel.db
	
	query =  db.auth_user.created_on >= start_time
	query &= db.auth_user.created_on <= end_time
	rows = db(query).select( orderby=~db.auth_user.id)
	
	table = TABLE(_class='table',_id='san_pham')
	table.append(TR(TH('STT',_style="width: 50px; text-align: center;"),TH(T('Tên thành viên ')),TH(T('Tài khoản')),TH(T('Email'))))
	i=1
	for row in rows:
		table.append(TR(TD(i),TD(row.first_name +' ' +row.last_name),TD(row.username),TD(row.email)))
		i+=1
	
	div_body = DIV(_class='panel-body')
	div_body.append(table)
	
	div_bottom = DIV(_class='input-group ')
	div_bottom.append(A('Xuất excel',_class='btn btn-success',_id='ex_button'))
	div_body.append(div_bottom)
	
	div.append(div_body)	
	scr ='''<script type="text/javascript"> 
		$("#ex_button").click(function(){
			$("#san_pham").table2excel({
				exclude: ".noExl",
				name: "San pham ban nhieu"

			});
		});

  
	</script>'''
	div.append(XML(scr))
	
	response.view = 'plugin_report/content.%s'%request.extension
	return dict(content=div)

	
def search_date():
	import datetime
	div= FORM(_class='input-group')
	div.append(LABEL("Từ ngày  "))
	start_time = request.vars.start_time or datetime.datetime.now().strftime("%Y-%m-%d 00:00:00")
	end_time = request.vars.end_time or datetime.datetime.now().strftime("%Y-%m-%d 23:59:00")
	div.append(INPUT(_type="text",_class='datetime',_name='start_time',_value=start_time))
	div.append(LABEL(" đến ngày "))
	div.append(INPUT(_type="text",_class='datetime',_name='end_time',_value=end_time))
	div.append(INPUT(_type='submit',_value=T('Lọc dữ liệu'),_class='btn btn-success'))
	
	return div
	
def view_xls():
	return dict()
	