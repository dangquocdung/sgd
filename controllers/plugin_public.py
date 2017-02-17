
def box_diem_bao():
	from plugin_public import Crawler
	plugin_public=Crawler()
	div = DIV()
	div.append(plugin_public.crawler_rss('http://khoinguyenlaptop.com/?q=taxonomy/term/9/all/feed',4))
	div.append(plugin_public.crawler_rss('http://nhaccudantoc.vn/taxonomy/term/3/all/feed',4))
	div.append(plugin_public.crawler_rss('http://guitar123.vn/taxonomy/term/3/all/feed',4))
	div.append(plugin_public.crawler_rss('http://icam.vn/?q=taxonomy/term/5/all/feed',4))
	return div

def box_giai_dieu_que_huong():
	obj = '''<object width="100%" height="170">  <param name="movie" value="http://www.nhaccuatui.com/l/X5Ymd0yCjYCl" />  <param name="quality" value="high" />  <param name="wmode" value="transparent" />  <param name="allowscriptaccess" value="always" />  <param name="flashvars" value="&autostart=true" />  <embed src="http://www.nhaccuatui.com/l/X5Ymd0yCjYCl" flashvars="target=blank&autostart=false" allowscriptaccess="always" quality="high" wmode="transparent" type="application/x-shockwave-flash" width="100%" height="170"></embed></object>'''
	return XML(obj)
	
def list_all_folder_news():
	folder = request.vars.folder_id
	if folder:
		rows = db((db.folder.parent==folder)&(db.folder.object==9)).select()
		div = DIV(_class='list_all_folder folder'+folder)
		
		if len(rows)>0:
			abc = 0
			for row in rows:
				div_row = DIV(_class='list_folder folder'+str(folder))
				div_row.append(H2(A(db.folder[row.id].name,_href=URL(c='default',f='index',vars=dict(folder_id=row.id))),_class='title'))
				from plugin_object import Object
				plugin_object = Object(name='news',folder_id=row.id)
				news = db(plugin_object.get_query()).select(db[plugin_object.name].ALL,limitby=(0,10))	
				if news:
					abc=abc+1
					ul_top= UL(_class=str(plugin_object.name)+str(news[0].id))
					for fi in ['image','name','heading']:
						if str(fi)=='image':
							if news[0][fi]:
								ul_top.append(LI(A(IMG(_src=URL(c='static', f='uploads/news/'+str(news[0][fi]))) ,_href=URL(c='default',f='read',args=['news',news[0].id], vars=dict(folder_id=row.id))),_class='news_'+str(fi)))
						else: 
							ul_top.append(LI(A(news[0][fi],_href=URL(c='default',f='read',args=['news',news[0].id], vars=dict(folder_id=row.id))),_class='news_'+str(fi)))
					div_row.append(DIV(ul_top,_class='news_top'))
					ul_reference = UL()
					i = 1
					while (i< len(news)):
						ul_reference.append(LI(A(news[i].name,_href=URL(c='default',f='read',args=['news',news[i].id], vars=dict(folder_id=row.id))),_class=str(plugin_object.name) + str(news[i].id)))
						i = i+1
					div_row.append(DIV(ul_reference,_class='news_reference'))
					div.append(div_row)
			if(abc==0):
				div = DIV(_class='box folder'+str(folder))
				div.append(H2(A(db.folder[folder].name,_href=URL(c='default',f='index',vars=dict(folder_id=folder))),_class='title_box'))
				div.append(DIV('No data',_class='nodata'))
		else:
			div = DIV(_class='box folder'+str(folder))
			div.append(H2(A(db.folder[folder].name,_href=URL(c='default',f='index',vars=dict(folder_id=folder))),_class='title_box'))
			from plugin_object import Object
			plugin_object = Object(name='news',folder_id=folder)
			news = db(plugin_object.get_query()).select(db[plugin_object.name].ALL)	
			if len(news) > 1:
				for new in news:
					div_row = DIV(_class='list_news news_'+str(new.id))
					ul_top= UL(_class=str(plugin_object.name)+str(new.id))
					for fi in ['image','name','heading']:
						if str(fi)=='image':
							if news[0][fi]:
								ul_top.append(LI(A(IMG(_src=URL(c='static', f='uploads/news/'+str(new[fi]))) ,_href=URL(c='default',f='read',args=['news',new.id], vars=dict(folder_id=folder))),_class='news_'+str(fi)))
						else: 
							ul_top.append(LI(A(new[fi],_href=URL(c='default',f='read',args=['news',new.id], vars=dict(folder_id=folder))),_class='news_'+str(fi)))
					div_row.append(DIV(ul_top,_class='news_list'))
					div.append(div_row)
				
			elif len(news) == 1:
				div = DIV(_class='box news folder'+str(folder))
				div.append(DIV(SPAN(T('Thông tin chi tiết')),_class='title_box'))
				context = {'header':None,'attachment':True,'fields_detail':['name','content'],'link_html':'','objects':[],'tabs':False,'table':False,'label':False}
				plugin_object = Object(name='news',folder_id=folder,id=news[0].id)
				div.append(plugin_object.explorer(context))
				#return LOAD(c='default',f='read.load',args=['news',news[0].id], vars=dict(folder_id=folder),ajax=True)	
				#LOAD(c='plugin_public',f='list_all_folder_news',vars=dict(folder_id=request.vars.folder_id),ajax=True)
			else:
				div.append(DIV('No data',_class='nodata'))
		return div
	else:
		return 'Not Folder'

def list_all_folder_news_title():
	folder = request.vars.folder_id
	if folder:
		rows = db((db.folder.parent==folder)&(db.folder.object==9)).select()
		div = DIV(_class='list_all_folder folder'+folder)
		
		if len(rows)>0:
			abc = 0
			for row in rows:
				div_row = DIV(_class='list_folder folder'+str(folder))
				div_row.append(H2(A(db.folder[row.id].name,_href=URL(c='default',f='index',vars=dict(folder_id=row.id))),_class='title'))
				from plugin_object import Object
				plugin_object = Object(name='news',folder_id=row.id)
				news = db(plugin_object.get_query()).select(db[plugin_object.name].ALL,limitby=(0,10))	
				if news:
					abc=abc+1
					i = 0
					ul_reference = UL()
					while (i< len(news)):
						ul_reference.append(LI(A(news[i].name,_href=URL(c='default',f='read',args=['news',news[i].id], vars=dict(folder_id=row.id))),_class=str(plugin_object.name) + str(news[i].id)))
						i = i+1
					div_row.append(DIV(ul_reference,_class='news_reference'))
					div.append(div_row)
			if(abc==0):
				div = DIV(_class='box folder'+str(folder))
				div.append(H2(A(db.folder[folder].name,_href=URL(c='default',f='index',vars=dict(folder_id=folder))),_class='title_box'))
				div.append(DIV('No data',_class='nodata'))
		else:
			div = DIV(_class='box folder'+str(folder))
			div.append(H2(A(db.folder[folder].name,_href=URL(c='default',f='index',vars=dict(folder_id=folder))),_class='title_box'))
			from plugin_object import Object
			plugin_object = Object(name='news',folder_id=folder)
			news = db(plugin_object.get_query()).select(db[plugin_object.name].ALL)	
			if len(news) > 1:
				for new in news:
					div_row = DIV(_class='list_news news_'+str(new.id))
					ul_top= UL(_class=str(plugin_object.name)+str(new.id))
					for fi in ['name']:
						ul_top.append(LI(A(new[fi],_href=URL(c='default',f='read',args=['news',new.id], vars=dict(folder_id=folder))),_class='news_'+str(fi)))
					div_row.append(DIV(ul_top,_class='news_list'))
					div.append(div_row)
				
			elif len(news) == 1:
				div = DIV(_class='box news folder'+str(folder))
				div.append(DIV(SPAN(T('Thông tin chi tiết')),_class='title_box'))
				context = {'header':None,'attachment':True,'fields_detail':['name','content'],'link_html':'','objects':[],'tabs':False,'table':False,'label':False}
				plugin_object = Object(name='news',folder_id=folder,id=news[0].id)
				div.append(plugin_object.explorer(context))
				#return LOAD(c='default',f='read.load',args=['news',news[0].id], vars=dict(folder_id=folder),ajax=True)	
				#LOAD(c='plugin_public',f='list_all_folder_news',vars=dict(folder_id=request.vars.folder_id),ajax=True)
			else:
				div.append(DIV('No data',_class='nodata'))
		return div
	else:
		return 'Not Folder'
		
def crawler_rss(link,records=10):
	import gluon.contrib.feedparser as feedparser
	d = feedparser.parse(link)
	i = 0
	div=DIV()
	for entry in d.entries :
		if i == records :
			break
		else :
			ul = UL(_class='contentul row_'+str(i+1)) 
			if find_imageURL_in_content(entry.description)!='':
				print entry.description
				li= LI(_class='image')
				a = A(_href=entry.link,_target='_blank')
				img = IMG(_src= find_imageURL_in_content(entry.description))
				a.append(img)
				li.append(a)
				ul.append(li)
				li1 = LI(_class='name')
			else:
				li1 = LI(_class='name_no_img')
			a1 = A(_href=entry.link,_target='_blank')
			a1.append(entry.title)
			li1.append(a1)
			ul.append(li1)
			div.append(ul)
			i+=1
	return div

def crawler_rss_more(link):
	import gluon.contrib.feedparser as feedparser
	d = feedparser.parse(link)
	i = 0
	div=DIV()
	for entry in d.entries :
		ul = UL(_class='contentul row_'+str(i+1)) 
		li1 = LI(_class='name field_2')
		a1 = A(_href=entry.link,_target='_blank')
		a1.append(entry.title)
		li1.append(a1)
		ul.append(li1)
		li2 = LI(_class='heading field_3')
		li2.append(XML(entry.description))
		ul.append(li2)
		div.append(ul)
		i+=1
	return div
	
def crawler_rss_from_bao_moi(keyword):
	import gluon.contrib.feedparser as feedparser
	d = feedparser.parse('http://www.baomoi.com/Rss/RssFeed.ashx?ph='+keyword+'&s=')
	i = 0
	div=DIV()
	for entry in d.entries :
		ul = UL(_class='contentul row_'+str(i+1)) 
		li1 = LI(_class='name field_2')
		a1 = A(_href=entry.link,_target='_blank')
		a1.append(entry.title)
		li1.append(a1)
		ul.append(li1)
		li2 = LI(_class='heading field_3')
		li2.append(XML(entry.description))
		ul.append(li2)
		div.append(ul)
		i+=1
	return div 

def update_imageURL_in_content():	
	object = request.args(0)
	objectID = request.args(1)
	news = db[object][objectID]
	if not news.image:
		new_content= news.content
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
		news.update_record(image=link)
	return 	
	
def makethumb():
	ImageID = request.args(1)
	size=(200,150)
	try:    
		thisImage=db(db.gallery.id==ImageID).select()[0]
		import os, uuid
		from PIL import Image
	except Exception, e: 
		print 'Error %s'%e
		return
	im=Image.open(request.folder + 'static/uploads/images/' + thisImage.image)
	im.thumbnail(size,Image.ANTIALIAS)
	thumbName='images.thumb.%s.jpg' % (uuid.uuid4())
	im.save(request.folder + 'static/uploads/images/' + thumbName,'jpeg')
	thisImage.update_record(thumb=thumbName)
	return 		

def get_galary_box():
	folder_id = request.vars.folder_id
	limit = request.vars.limit
	from plugin_object import Object
	plugin_object = Object(name='gallery',folder_id=folder_id)
	rows = db(plugin_object.get_query()).select(db[plugin_object.name].ALL,orderby='<random>',limitby=(0,int(limit)))
	div = DIV(_id='gallery_homepage')
	ul = UL(_id='sliderContent')
	for row in rows:
		ul.append(LI(A(IMG(_src=URL(c='static',f='uploads/images/'+str(row.thumb))),_href=URL(c='default',f='index',vars=dict(folder_id=folder_id))) ,_class='sliderImage'))
	div.append(DIV(ul,_id='slider'))	
	return div
		
def add_on():
	scr = '''
		<script type="text/javascript">
		var min=8;
		var max=38;
		function zoominLetter() {
				var s = parseInt($("#object_table_content").css("font-size").replace("px",""));
				if (s!=max){
				s+=1
					
				}
				$("#object_table_content").css({'font-size':s+"px"});
			
		  
		}
		function zoomoutLetter() {
		  var s = parseInt($("#object_table_content").css("font-size").replace("px",""));
				if (s!=min){
				s-=1
					
				}
				$("#object_table_content").css({'font-size':s+"px"});
		}
		
		$(document).ready(function() {
           $("#simplePrint").click(function(){
				$('#object_table_content').printElement();
		   });
        });
		</script>
	'''
	div = DIV(_id='add_on')
	div.append(XML(scr))
	compose = 'window.open("%s","%s","width=600,height=400,toolbar=no,location=no,directories=no,status=no,menubar=no,left=400,top=200")'%(URL(c='plugin_public',f='mail.html',args=request.args,vars=request.vars),T('Send email'))
	div.append(A(T('Email'),_onclick=compose ,_title='Chia sẻ qua email',_id="email"))
	div.append(A(T('Print') ,_title='In bài viết',_id="simplePrint"))
	div.append(A(T('A'),_href="javascript:zoominLetter();" ,_title='Tăng phông chữ',_id='zoominLetter'))
	div.append(A(T('a'),_href="javascript:zoomoutLetter();" ,_title='Giảm phông chữ',_id='zoomoutLetter'))
	
	return div

def service_load_box():
	try:
		# from xmlrpclib import ServerProxy	
		# server = ServerProxy('http://dhtn.hatinh.gov.vn/dhtn/plugin_admin/call/xmlrpc')
		# news = server.service_load_box('news_tindieuhanh_home')
		from BeautifulSoup import BeautifulSoup
		import urllib2 
		url = urllib2.urlopen("http://dhtn.hatinh.gov.vn/dhtn/plugin_admin/call/run/service_load_box/news_tindieuhanh_home_5")
		news = url.read()
		content = news.replace('<a data-w2p_disable_with="default" href="', '<a TARGET="_blank" href="http://dhtn.hatinh.gov.vn')
		return content	
	except Exception, e:
		return e	
		
	
	
def mail():
	content = TABLE()
	table = TABLE()
	content.append(TR(TH(T('Thư của bạn')),TD(INPUT(_type='text',_name='you_email',_id='you_email'))))
	content.append(TR(TH(T('Tên của bạn')),TD(INPUT(_type='text',_name='you_name',_id='you_name'))))
	content.append(TR(TH(T('Người nhận')),TD(INPUT(_type='text',_name='send_to',_id='send_to'))))
	content.append(TR(TH(T('Lời nhắn')),TD(TEXTAREA(_name='message',_cols="40"),_class='message')))
	ajax = "ajax('%s', ['you_email','you_name','send_to','message'], 'window_sendmail')"%(URL(f='sendmail',args=request.args,vars=request.vars))
	content.append(TR(TH(),TD(INPUT(_type='button',_value=T(' Gửi '),_onclick=ajax),INPUT(_type='button',_value=T(' Đóng '),_onclick='window.parent.close()'))))
	h2 = H2(T('Chia sẻ qua email'),_style=" background: #158BD5; height: 40px; line-height: 40px; color: #fff; text-align: center; text-transform: uppercase; ",_class='title')
	content = DIV(h2,content,_id='window_sendmail')
	return dict(content=content)

def sendmail():
	you_email = request.vars.you_email.replace(' ','')
	you_name  = request.vars.you_name
	send_to   = request.vars.send_to.replace(' ','')
	send_to   = send_to.replace(';',',')
	send_to   = send_to.split(',')
	message   = request.vars.message
	subject   = you_name +' đã chia sẻ với bạn:'
	url = 'http://'+request.env.http_host
	mailto = "mailto:"+ you_email
	content   = you_name+'<'+str(A(you_email,_href=mailto))+'>' +' đã chia sẻ với bạn 1 bài viết tại' + str(A('đây',_href=url)) + '.<br/> Với lời nhắn: <br/>' + message
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H2(T('Process execute and send mail successfully')),XML(scr),_class='notice')
	else: 
		div = DIV(H2(T('Send mail error')),XML(scr),_class='notice')
	return div


	