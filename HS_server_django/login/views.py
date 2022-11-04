from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, JsonResponse
from django.shortcuts import redirect
import uuid
from login.models import Contact

def get_userinfo_context(request):
    context_dict = {"user_name": "无名", "user_sign": "请让我独享经验", "login_button":"登录", "login_link": "/login" }
    session = request.session.get("user_account")
    if session:
        user = Contact.objects.filter(account=session).get()
        context_dict["login_button"] = f"退出"
        context_dict["login_link"] = "/login/logout"
        context_dict["user_name"] = user.name
        context_dict["user_sign"] = user.sign
    return context_dict

def login_check(fun):
    # print("登录检查+++++++++++++++++")
    def real_login_check(request, *args, **kwargs):
        # print("登录检查2+++++++++++++++++")
        session = request.session.get("user_account")
        if session:
            return fun(request, *args, **kwargs)
        else:
            return redirect("/login")
    return real_login_check


def login(request):
    '''
    1. 检查cookie
    2. 如果有cookie，返回带账号密码的界面
    '''
    cookie = request.COOKIES.get("user_name")
    session = request.session.get("user_account")
    context_dict = {"account": "", "password":""}
    if cookie:
        context_dict["account"] = cookie
    if session:
        try:
            user = Contact.objects.filter(account=session).get()
            context_dict = {"account": user.account, "password":user.password}
        except:
            pass
    response = render(request, "login/login.html", context=context_dict)
    return response


def click_login(request):
    '''
    1. 获取账号密码
    2. 检查用户名密码是否正确，并返回结果
    3. 如果密码正确，查看是否有cookie, 没有cookie或者cookie不等于账户，则设置cookie
    4. 前端收到结果，如果正确，跳转到主界面
    5. 主界面根据cookie判断该用户是否已经登陆
    '''
    account = request.POST.get("account")
    password = request.POST.get("password")
    cookie = request.COOKIES.get("user_name")
    session = request.session.get("user_account")
    try:
        user = Contact.objects.filter(account=account).get()
        if user.password == password:
            response = JsonResponse({"result": "correct"})
            if not cookie or cookie!=account:
                # cookie = uuid.uuid4()
                response.set_cookie("user_name", account)
            if not session or session!=account:
                request.session["user_account"] = account
                request.session.set_expiry(None)
        else:
            response = JsonResponse({"result": "password not correct!"})
    except:
        response = JsonResponse({"result": "account isn't exist!"})
    return response


def logout(request):
    if request.session.has_key("user_account"):
        del request.session["user_account"]
    return redirect("/HS_server")


def register(request):
    register_code = request.POST.get("register_code")
    print("注册码是", register_code ,"----")
    if register_code!="8537":
        return JsonResponse({"result": "register code not correct"})

    account = request.POST.get("account")
    password = request.POST.get("password")
    name = request.POST.get("name")
    sign = request.POST.get("sign")
    print(sign)
    try:
        user = Contact.objects.filter(account=account).get()
        response = JsonResponse({"result": "account already exist"})
    except:
        new_user = Contact()
        new_user.name, new_user.account, new_user.password, new_user.sign = name, account, password, sign
        new_user.save()
        response = JsonResponse({"result": "register succesffully"})
    return response


def setting(request):
    session = request.session.get("user_account")
    context_dict = {"account": "", "password":""}
    if session:
    # if cookie:
        try:
            # user = Contact.objects.filter(cookie=cookie).get()
            user = Contact.objects.filter(account=session).get()
            context_dict = {"account": user.account, "password":user.password, "name":user.name, "sign": user.sign}
        except:
            pass
        response = render(request, "login/setting.html", context=context_dict)
        return response
    else:
        return redirect("/login")

def setting_submit(request):
    session = request.session.get("user_account")
    account = session
    password = request.POST.get("password")
    name = request.POST.get("name")
    sign = request.POST.get("sign")
    try:
        user = Contact.objects.filter(account=account).get()
        user.password, user.name, user.sign = password, name, sign
        user.save()
        print("*"*100, "修改信息成功", password, name, sign)
        response = JsonResponse({"result": "modify_success"})
    except:
        response = JsonResponse({"result": "can't find this account"})
    return response


def help(request):
    return HttpResponse("自救者，人恒救之")

