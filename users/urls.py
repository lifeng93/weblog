"""users URL Configuration"""

from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('pre_register/', views.pre_register, name='pre_register'),
    path('actual_register/', views.actual_register, name='actual_register'),
    path('register_success/', views.register_success, name='register_success'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('ajax_nickname/', views.ajax_nickname, name='ajax_nickname'),
    path('ajax_phone/', views.ajax_phone, name='ajax_phone'),
    path('get_captcha/', views.get_captcha, name='get_captcha'),
    path('ajax_send_msg/', views.ajax_send_msg, name='ajax_send_msg'),
    path('ajax_msg_code/', views.ajax_msg_code, name='ajax_msg_code'),
    path('ajax_password/', views.ajax_password, name='ajax_password'),
    path('set_password/', views.set_password, name='set_password'),
    path('ajax_send_msg_setpwd/', views.ajax_send_msg_setpwd, name='ajax_send_msg_setpwd'),
    path('setpwd_success/', views.setpwd_success, name='setpwd_success'),
    path('set_email/', views.set_email, name="set_email"),
    url(r'set_email/token=(?P<token>[0-9a-z-]{24})/', views.email_token, name="email_token"),
    path('set_center/', views.set_center, name="set_center"),
    path("reset_phone/", views.reset_phone, name="reset_phone"),
    path("reset_password/", views.reset_password, name="reset_password"),
    path("reset_nickname/", views.reset_nickname, name="reset_nickname"),
    path("set_center_options/", views.set_center_options, name="set_center_options"),
    path("set_center_header/", views.set_center_header, name="set_center_header"),
    path("blank/", views.blank, name="blank"),

]
app_name = "users"  
