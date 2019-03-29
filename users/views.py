from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth import login, logout
from .models import User, Msg_send_log, Email_send_log
import os
import gzip
from django.conf import settings
from .captcha import Captcha
import datetime
import random
from .decorators import referer_required, ajax_required
from django.contrib.auth.decorators import login_required
from .tokens import EmailSetTokenGenerator
from django.core.mail import EmailMultiAlternatives
from logs.models import Article


# Create your views here.
def index(request):
    articles = Article.objects.filter(is_public_index=True, is_public=True, is_delete=False, is_recycle=False)
    if request.user.is_authenticated:
        private_articles = Article.objects.filter(author=request.user, is_public_index=True, is_public=False, is_delete=False, is_recycle=False)
        articles = articles | private_articles
    articles = articles.order_by("-create_time")
    request_path = request.path
    return render(request, 'users/index.html', locals())

@ajax_required
def ajax_nickname(request):
    if request.method == 'POST':
        nickname = request.POST['nickname']
        if User.objects.filter(nickname=nickname).exists():
            error_msg = '昵称已存在'
        else:
            error_msg = ''
        return HttpResponse(error_msg)


@ajax_required
def ajax_phone(request):
    phone = request.POST['phone']
    if User.objects.filter(phone=phone).exists():
        error_msg = '手机号已存在'
    else:
        error_msg = ''
    return HttpResponse(error_msg)


def get_captcha(request):
    captcha = Captcha()
    img_data, captcha_string = captcha.get_captcha()
    request.session['captcha_string'] = captcha_string
    return HttpResponse(img_data, 'image/png')


def get_msg_code():
    """生成6位数的短信验证码"""
    msg_code = ''
    for i in range(6):
        num = random.randint(0, 9)
        msg_code += str(num)
    return msg_code


@ajax_required
def ajax_send_msg(request):
    if request.method == "POST":
        today = datetime.date.today()
        phone = request.POST['phone']
        captcha = request.POST['captcha']
        if captcha != request.session.get('captcha_string', ''):
            error_msg = '验证码错误'
        elif User.objects.filter(phone=phone).exists():
            error_msg = '手机号已被注册'
        elif Msg_send_log.objects.filter(phone=phone, send_time__date=today ).count() > 3:
            error_msg = "今日发送次数已达上限"
        else:
            msg_code = get_msg_code()
            # 发送短信 略
            msg_send_log = Msg_send_log.objects.create(phone=phone, msg_code=msg_code)
            msg_send_log.save()
            error_msg = '短信成功发送'
        return HttpResponse(error_msg)


@ajax_required
def ajax_msg_code(request):
    if request.method == 'POST':
        phone = request.POST["phone"]
        msg_code = request.POST["msg_code"]
        if not Msg_send_log.objects.filter(phone=phone).exists():
            error_msg = '请获取短信验证码' #该手机未发送过短信
        elif Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0].verify_times >= 3:
            error_msg = '此短信验证码已失效' 
        elif msg_code != Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0].msg_code:
            error_msg = '短信验证码错误'
            msg_send_log = Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0]
            msg_send_log.verify_times += 1
            msg_send_log.save()
        else:
            error_msg = ''
        return HttpResponse(error_msg)

def get_common_passwords():
    password_list_path = os.path.join(settings.BASE_DIR, 'static/txt/common-passwords.txt.gz')
    try:
        with gzip.open(password_list_path) as f:
            common_passwords_lines = f.read().decode().splitlines()
    except IOError:
        with open(password_list_path) as f:
            common_passwords_lines = f.readlines()

    passwords = {p.strip() for p in common_passwords_lines}
    return passwords

passwords = get_common_passwords()        


@ajax_required
def ajax_password(request):
    if request.method == 'POST':
        password = request.POST["password"].lower().strip()
        if password in passwords:
            error_msg = '密码太常见'
        else:
            error_msg = ''
        return HttpResponse(error_msg)


def register(request):
    request.session.set_test_cookie()
    return HttpResponseRedirect(reverse('users:pre_register'))


@referer_required
def pre_register(request):
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        return HttpResponseRedirect(reverse('users:actual_register'))
    else:
        return render(request, 'users/pre_register.html')

@referer_required
def actual_register(request):
    if request.method == 'POST':
        nickname = request.POST["nickname"].strip()
        phone = request.POST["phone"].strip()
        msg_code = request.POST["msg_code"].strip()
        password = request.POST['password'].lower().strip()
        if User.objects.filter(nickname=nickname):
            nickname_error = '昵称已存在'
        elif User.objects.filter(phone=phone).exists():
            phone_error = '手机号已被注册'
        elif password in passwords:
            password_error = '密码太常见'
        elif not Msg_send_log.objects.filter(phone=phone).exists():
            msg_error = '请获取短信验证码' #该手机未发送过短信
        elif Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0].verify_times >= 3:
            msg_error = '此短信验证码已失效' 
        elif msg_code != Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0].msg_code:
            msg_error = '短信验证码错误'
            msg_send_log = Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0]
            msg_send_log.verify_times += 1
            msg_send_log.save()
        else:
            user = User()
            user.phone = phone
            user.nickname = nickname
            user.set_password(password)
            user.save()
            msg_send_log = Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0]
            msg_send_log.verify_times = 3
            msg_send_log.save()
            return HttpResponseRedirect(reverse('users:register_success'))
    return render(request, 'users/register.html', locals())

@referer_required
def register_success(request):
    return render(request, 'users/register_success.html')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('users:index'))
   


def login_view(request):
    if request.method == 'POST':
        phone = request.POST['phone'].strip()
        password = request.POST['password'].lower().strip()
        captcha = request.POST['captcha'].strip()
        auto_login = request.POST.getlist('auto_login')
        next = request.POST["next"]
        if captcha != request.session.get('captcha_string', ''):
            captcha_error = '验证码错误'
        elif User.objects.filter(phone=phone).exists():
            user = User.objects.get(phone=phone)
            if user.check_password(password):
                login(request, user)
                if auto_login:
                    request.session.set_expiry(10*24*60*60)
                else:
                    request.session.set_expiry(0)
                return HttpResponseRedirect(next)
            else:
                password_error = '密码不正确'
        else:
            phone_error = '账号不存在'
    elif request.method == "GET":
        next = request.GET.get("next")
    return render(request, 'users/login.html', locals())


@ajax_required
def ajax_send_msg_setpwd(request):
    if request.method == "POST":
        today = datetime.date.today()
        phone = request.POST['phone']
        captcha = request.POST['captcha']
        if captcha != request.session.get('captcha_string', ''):
            error_msg = '验证码错误'
        elif  not User.objects.filter(phone=phone).exists():
            error_msg = '该手机未注册'
        elif Msg_send_log.objects.filter(phone=phone, send_time__date=today ).count() > 5:
            error_msg = "今日发送次数已达上限"
        else:
            msg_code = get_msg_code()
            # 发送短信 略
            msg_send_log = Msg_send_log.objects.create(phone=phone, msg_code=msg_code)
            msg_send_log.save()
            error_msg = '短信成功发送'
        return HttpResponse(error_msg)


def set_password(request):
    """登录时忘记密码"""
    if request.method == "POST":
        phone = request.POST['phone'].strip()
        msg_code = request.POST['msg_code'].strip()
        password = request.POST['password'].strip()
        if not User.objects.filter(phone=phone).exists():
            phone_error = '该手机号未注册'
        elif not Msg_send_log.objects.filter(phone=phone).exists():
            msg_error = '请获取短信验证码' #该手机未发送过短信
        elif password in passwords:
            password_error = '密码太常见'
        elif Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0].verify_times >= 3:
            msg_error = '此短信验证码已失效' 
        elif msg_code != Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0].msg_code:
            msg_error = '短信验证码错误'
            msg_send_log = Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0]
            msg_send_log.verify_times += 1
            msg_send_log.save()
        else:
            user = User.objects.get(phone=phone)
            user.set_password(password)
            user.save()
            msg_send_log = Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0]
            msg_send_log.verify_times = 3
            msg_send_log.save()
            return HttpResponseRedirect(reverse('users:setpwd_success'))
    return render(request, 'users/set_password.html', locals())

@referer_required
def setpwd_success(request):
    return render(request, 'users/setpwd_success.html')

@login_required
def set_email(request):
    if request.method == "POST":
        email = request.POST["email"].strip()
        phone = request.user.phone 
        today = datetime.date.today()
        if Email_send_log.objects.filter(phone=phone, send_time__date=today).count() > 10:
            email_error = "今日已发邮件数超过上限"
        else:
            # 生成token
            user = User.objects.get(phone=phone)
            email_token_generator = EmailSetTokenGenerator()
            token = email_token_generator.make_token(user)
            server_host = "http://127.0.0.1:8000/"
            token_url = server_host + "/set_email/token=" + token
            # 发送邮件 链接
            from_email = settings.DEFAULT_FROM_EMAIL
            email_subject = '星博客邮箱验证'
            text_content = "点击链接，完成邮箱的绑定："
            html_content = '<p>点击链接，完成邮箱的绑定</p><a href="%s">%s</a>'%(token_url, token_url)
            msg = EmailMultiAlternatives(email_subject, text_content, from_email, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            # 保存发送记录 
            email_send_log = Email_send_log.objects.create(phone=phone, email=email, token=token)
            email_send_log.save()
            return render(request, 'users/sure_email.html', locals())
    return render(request, 'users/set_email.html', locals())


def email_token(request, token):
    if not Email_send_log.objects.filter(token=token).exists():
        error_msg = "此链接无效"
    else:
        email_send_log = Email_send_log.objects.filter(token=token).order_by("-send_time")[0]
        if email_send_log.is_valid == False:
            error_msg = "此链接已失效"
        else:
            phone = email_send_log.phone
            email = email_send_log.email
            user = User.objects.get(phone=phone)
            user.email = email
            user.save()
            email_send_log.is_valid = False
            email_send_log.save()
            error_msg = "恭喜您，邮箱绑定成功！"
    return render(request, 'users/setemail_result.html', locals())


@login_required
def set_center(request):
    return render(request, 'users/set_center.html')


@login_required
def reset_phone(request):
    if request.method == 'POST':
        phone = request.POST["phone"].strip()
        msg_code = request.POST["msg_code"].strip()
        if User.objects.filter(phone=phone).exists():
            phone_error = '手机号已被注册'
        elif not Msg_send_log.objects.filter(phone=phone).exists():
            msg_error = '请获取短信验证码' #该手机未发送过短信
        elif Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0].verify_times >= 3:
            msg_error = '此短信验证码已失效' 
        elif msg_code != Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0].msg_code:
            msg_error = '短信验证码错误'
            msg_send_log = Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0]
            msg_send_log.verify_times += 1
            msg_send_log.save()
        else:
            user = request.user
            user.phone = phone
            user.save()
            msg_send_log = Msg_send_log.objects.filter(phone=phone).order_by("-send_time")[0]
            msg_send_log.verify_times = 3
            msg_send_log.save()
            return render(request, 'users/reset_phone_success.html')
    return render(request, 'users/reset_phone.html', locals())


@login_required
def  reset_password(request):
    """修改密码"""
    if request.method == 'POST':
        password = request.POST['password'].lower().strip()
        if password in passwords:
            error_msg = '密码太常见'
        else:
            user = request.user
            user.set_password(password)
            user.save()
            return render(request, 'users/reset_password_success.html')
    return render(request, 'users/reset_password.html', locals())


@login_required
def reset_nickname(request):
    if request.method == 'POST':
        nickname = request.POST['nickname'].strip()
        if User.objects.filter(nickname=nickname).exists():
            error_msg = '昵称已存在'
        else:
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            user.nickname = nickname
            user.save()
            return render(request, 'users/reset_nickname_success.html')
    return render(request, 'users/reset_nickname.html', locals())


def blank(request):
    return render(request, 'users/blank.html')

def set_center_options(request):
    return render(request, 'users/set_center_options.html')

def base_header(request):
    request_path = request.GET.get("next")
    return render(request, 'users/base.html', locals())
