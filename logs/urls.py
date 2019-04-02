"""logs URL Configuration"""

from django.urls import path
from . import views
from django.views.static import serve
from django.conf.urls import url
from django.conf import settings

urlpatterns = [
    url(r'^new_article/$', views.new_article, name='new_article'),
    url(r'^article_upload/$', views.article_upload, name='article_upload'),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^ajax_add_cate/$', views.ajax_add_cate, name='ajax_add_cate'),
    url(r'^ajax_get_cates/$', views.ajax_get_cates, name='ajax_get_cates'),
    url(r'^user(?P<user_id>\d+)/$', views.userhome, name='userhome'),
    url(r'^userhome_header(?P<user_id>\d+)/$', views.userhome_header, name="userhome_header"),
    url(r'^home_list_cates(?P<user_id>\d+)/$', views.home_list_cates, name='home_list_cates'),
    url(r'^ajax_home_cates_list(?P<user_id>\d+)/$', views.ajax_home_cates_list, name='ajax_home_cates_list'),
    url(r'^cate(?P<cate_id>\d+)/$', views.cate, name="cate"),
    url(r'^home_new_articles(?P<user_id>\d+)/$', views.home_new_articles, name="home_new_articles"),
    url(r'^article(?P<article_id>\d+)/$', views.article, name="article"),
    url(r'^cate_null(?P<user_id>\d+)/$', views.cate_null, name="cate_null"),
    url(r'^edit_cates/$', views.edit_cates, name="edit_cates"),
    url(r'^del_cate(?P<cate_id>\d+)/$', views.del_cate, name="del_cate"),
    url(r'^rename_cate(?P<cate_id>\d+)/$', views.rename_cate, name="rename_cate"),
    url(r'^del_article_cate_null(?P<article_id>\d+)/$', views.del_article_cate_null, name="del_article_cate_null"),
    url(r'^del_article(?P<article_id>\d+)/$', views.del_article, name="del_article"),
    url(r'^recycle_bin/$', views.recycle_bin, name="recycle_bin"),
    url(r'^shift_delete(?P<article_id>\d+)/$', views.shift_delete, name="shift_delete"),
    url(r'^recycle_article(?P<article_id>\d+)/$', views.recycle_article, name="recycle_article"),
    url(r"^update_article(?P<article_id>\d+)/$", views.update_article, name="update_article"),
]
app_name = "logs"  
