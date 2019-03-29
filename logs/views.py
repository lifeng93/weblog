from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Article, Category
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
import os
import uuid
import json
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import  HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from users.decorators import referer_required
from django.http import Http404

User = get_user_model()


# Create your views here.
@login_required
def new_article(request):
	if request.method == "POST":
		title = request.POST['title']
		content = request.POST['content']
		category = request.POST.get('category')
		if category == "不分类":
			category = None
		article = Article.objects.create(title=title, content=content, author=request.user, cate_id=category )
		is_public = request.POST.get('is_public')
		is_public_index = request.POST.get('is_public_index')
		cannot_comment = request.POST.get('cannot_comment')
		if is_public:
			article.is_public = True
		if is_public_index:
			article.is_public_index = True
		if cannot_comment:
			article.can_comment = False
		article.save()
		return HttpResponseRedirect(reverse('logs:userhome', args=(request.user.id,)))
	return render(request, 'logs/new_article.html')


""" start 富文本编辑器上传图片 """

'''
@csrf_exempt用于取消csrftoken验证
url为:http://127.0.0.1:8000/article_upload/?dir=media post请求
'''
@csrf_exempt
def article_upload(request):
	'''
	kindeditor图片上传返回数据格式说明：
	{"error": 1, "message": "出错信息"}
	{"error": 0, "url": "图片地址"}
	'''
	result = {"error": 1, "message": u"上传失败"}
	files = request.FILES.get("imgFile")  #input type="file" 中name属性对应的值为imgFile
	upload_type = request.GET['dir']  #获取资源类型
	if  files:
		result = process_upload(files, upload_type)
	#结果以json形式返回
	return HttpResponse(json.dumps(result), content_type="application/json")


def is_ext_allowed(upload_type, ext):
	'''
	根据类型判断是否支持对应的扩展名
	'''
	ext_allowed = {}
	ext_allowed['image'] = ['jpg','jpeg', 'bmp', 'gif', 'png', 'PNG']
	ext_allowed['flash'] = ["swf", "flv"]
	ext_allowed['media'] = ["swf", "flv", "mp3", "wav", "wma", "wmv", "mid", "avi", "mpg", "asf", "rm", "rmvb", "mp4"]
	ext_allowed['file'] = ["doc", "docx", "xls", "xlsx", "ppt", "htm", "html", "txt", "zip", "rar", "gz", "bz2", 'pdf']
	return ext in ext_allowed[upload_type]

def get_relative_file_path():
	'''
	获取相对路径
	'''
	dt = datetime.datetime.today()
	relative_path = 'upload/%s/%s/' %(dt.year, dt.month)
	absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
	print(absolute_path)
	if not os.path.exists(absolute_path):
		os.makedirs(absolute_path)
	return relative_path


def process_upload(files, upload_type):
	dir_types = ['image','flash','media','file']
	if upload_type not in dir_types:
		return {"error":1, "message": u"上传类型不支持[必须是image,flash,media,file]"}

	cur_ext = files.name.split('.')[-1]  #当前上传文件的扩展名
	# 判断是否支持对应的扩展名
	if not is_ext_allowed(upload_type, cur_ext):
		return {'error':1, 'message': u'error:扩展名不支持 %s 类型不支持%s 扩展名' %(upload_type, cur_ext)}

	relative_path = get_relative_file_path()
	file_name = str(uuid.uuid1()) + "." + cur_ext
	base_name = os.path.join(settings.MEDIA_ROOT, relative_path)
	file_full_path = os.path.join(base_name, file_name).replace('\\','/') #windows中的路径以\分隔
	file_url = settings.MEDIA_URL + relative_path + file_name

	with open(file_full_path, 'wb') as f:
		if  files.multiple_chunks() == False:  #判断是否大于2.5M
			f.write(files.file.read())
		else:
			for chunk in files.chunks():
				f.write(chunk)

	return {"error": 0, "url": file_url}


""" end 富文本编辑器上传图片 """


@login_required
def ajax_add_cate(request):
	"添加个人分类"
	if request.method == 'POST':
		cate_name = request.POST['cate_name']
		user = request.user
		if Category.objects.filter(owner=user, cate_name=cate_name).exists():
			error_msg = "该分类已存在"
		elif Category.objects.filter(owner=user).count() >= 50:
			error_msg = "您最多可创建50个分类"
		else:
			Category.objects.create(cate_name=cate_name, owner=user)
			error_msg = ""
		return HttpResponse(error_msg)


from django.core.serializers.json import DjangoJSONEncoder

def ajax_get_cates(request):
	"获取个人分类列表"
	cates = Category.objects.filter(owner=request.user).values('id', 'cate_name')
	cates = json.dumps(list(cates), cls=DjangoJSONEncoder)
	return JsonResponse({'cates':cates})


def userhome(request, user_id):
	user = get_object_or_404(User, id=user_id, is_active=True)
	return render(request, 'logs/homepage.html', locals())

def userhome_header(request, user_id):
	home_user = get_object_or_404(User, id=user_id, is_active=True)
	request_path = request.GET.get("next")
	return render(request, 'logs/userhome_header.html', locals())

@referer_required
def home_list_cates(request, user_id):
	user = User.objects.get(id=user_id)
	user_name =user.nickname
	return render(request, 'logs/home_list_cates.html', locals())

def ajax_home_cates_list(request, user_id):
	user = User.objects.get(id=user_id)
	cates = Category.objects.filter(owner=user).values('id', 'cate_name')
	cates = json.dumps(list(cates), cls=DjangoJSONEncoder)
	return JsonResponse({'cates':cates})


def cate(request, cate_id):
	category = get_object_or_404(Category, id=cate_id)
	user = category.owner
	get_object_or_404(User, id=user.id, is_active=True)
	if user == request.user:
		articles = Article.objects.filter(cate=category, is_recycle=False).order_by("-create_time")
	else:
		articles = Article.objects.filter(cate=category, is_recycle=False, is_public=True).order_by("-create_time")
	page_num = request.GET.get('page')
	articles_paginator = Paginator(articles, 2)
	if page_num:
		page_articles = articles_paginator.get_page(page_num)
	else:
		page_articles = articles_paginator.get_page(1)
	return render(request, 'logs/cate.html', locals())	


def home_new_articles(request, user_id):
	user = User.objects.get(id=user_id)
	if user == request.user:
		articles = Article.objects.filter(author=user, is_recycle=False).order_by("-update_time")
	else:
		articles = Article.objects.filter(author=user, is_public=True, is_recycle=False).order_by("-update_time")
	return render(request, 'logs/home_new_articles.html', locals())

def article(request, article_id):
	article = get_object_or_404(Article, id=article_id, is_recycle=False)
	user = article.author
	get_object_or_404(User, id=user.id, is_active=True)
	if user != request.user and article.is_public == False:
		raise Http404
	else:
		article.reads += 1
		article.save()
		return render(request, 'logs/article.html', locals())
	
def cate_null(request, user_id):
	user = get_object_or_404(User, id=user_id, is_active=True)
	if user == request.user:
		articles = Article.objects.filter(author=user, cate=None, is_recycle=False).order_by("-create_time")
	else:
		articles = Article.objects.filter(author=user, cate=None, is_public=True, is_recycle=False).order_by("-create_time")
	page_num = request.GET.get('page')
	articles_paginator = Paginator(articles, 2)
	if page_num:
		page_articles = articles_paginator.get_page(page_num)
	else:
		page_articles = articles_paginator.get_page(1)
	return render(request, 'logs/cate_null.html', locals())	
	
@login_required
def edit_cates(request):
	return render(request, 'logs/edit_cates.html', locals())


@login_required
def del_cate(request, cate_id):
	category = get_object_or_404(Category, id=cate_id, owner=request.user)
	articles = Article.objects.filter(cate=category)
	articles.update(cate=None)
	category.delete()
	return HttpResponse("删除分类成功")


@login_required
def rename_cate(request, cate_id):
	if request.method == 'POST':
		new_cate_name = request.POST['new_cate_name']
		category = get_object_or_404(Category, id=cate_id, owner=request.user)
		if Category.objects.filter(owner=request.user, cate_name=new_cate_name).exists():
			error_msg = "该分类名已存在"
		else:
			category.cate_name = new_cate_name
			category.save()
			error_msg = "分类重命名成功"
		return HttpResponse(error_msg)

@login_required
def del_article(request, article_id):
	article = get_object_or_404(Article, id=article_id, author=request.user)
	cate_id = article.cate.id
	article.is_recycle = True
	article.save()
	return HttpResponseRedirect(reverse('logs:cate', args=(cate_id,)))


@login_required
def del_article_cate_null(request, article_id):  
	article = get_object_or_404(Article, id=article_id, author=request.user, is_recycle=False)
	article.is_recycle = True
	article.save()
	return HttpResponseRedirect(reverse('logs:cate_null', args=(request.user.id,)))



@login_required
def recycle_bin(request):
	articles = Article.objects.filter(author=request.user, is_recycle=True).order_by("-update_time")
	page_num = request.GET.get('page')
	articles_paginator = Paginator(articles, 2)
	if page_num:
		page_articles = articles_paginator.get_page(page_num)
	else:
		page_articles = articles_paginator.get_page(1)
	return render(request, 'logs/recycle_bin.html', locals())


@login_required
def shift_delete(request, article_id):
	article = get_object_or_404(Article, id=article_id, is_recycle=True, author=request.user)
	article.delete()
	return HttpResponseRedirect(reverse('logs:recycle_bin'))


@login_required
def recycle_article(request, article_id):
	article = get_object_or_404(Article, id=article_id, is_recycle=True, author=request.user)
	article.is_recycle = False
	article.save()
	return HttpResponseRedirect(reverse('logs:recycle_bin'))


@login_required
def update_article(request, article_id):
	if request.method == "POST":
		title = request.POST['title']
		content = request.POST['content']
		category = request.POST.get('category')
		if category == "不分类":
			category = None
		article = get_object_or_404(Article, id=article_id, author=request.user)
		article.title = title
		article.content = content
		article.cate_id = category
		is_public = request.POST.get('is_public')
		is_public_index = request.POST.get('is_public_index')
		cannot_comment = request.POST.get('cannot_comment')
		if is_public:
			article.is_public = True
		if is_public_index:
			article.is_public_index = True
		if cannot_comment:
			article.can_comment = False
		article.save()
		return HttpResponseRedirect(reverse('logs:userhome', args=(request.user.id,)))
	article = get_object_or_404(Article, id=article_id, author=request.user)
	return render(request, "logs/update_article.html", locals())

