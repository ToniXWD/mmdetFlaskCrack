import glob
import os
import json
import random
from flask_mail import Mail
from flask import Blueprint, render_template, send_file, request, redirect, jsonify, url_for, session, g
from .form import RegisterForm, LoginForm
from flask_mail import Message
import string
from werkzeug.security import generate_password_hash, check_password_hash
from .inf import temp_codes, user_dict
from functools import wraps

def login_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if hasattr(g,'user'):
            if g.user is not None:
                return func(*args,**kwargs)
        else:
            return render_template("login.html", result=4)
    return wrapper

bp = Blueprint("user",__name__,url_prefix="/user")

letters = string.ascii_letters+string.digits

mail = Mail()

@bp.route("/login",methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template("login.html",result=0)
    else:
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            print("输入密码为:"+password)
            print("输入邮箱为:"+email)
            if email not in user_dict.keys():
                print("登录时邮箱未注册")
                return render_template("register.html", result=2)
            if check_password_hash(user_dict[email]["password"],password):
                session["email"] = email
                return redirect("/")
            else:
                print("密码错误")
                return render_template("login.html",result=1)
                # return redirect(url_for("user.login"))
        else:
            return render_template("login.html",result=1)



@bp.route("/validCodes",methods=['POST'])
def validCodes():
    email = request.form.get("email")
    print("要发送验证码邮箱为:"+email)
    if email in user_dict.keys():
        print("注册邮箱已经被注册")
        return jsonify({"code":600}) #600表示邮箱已经注册过
    if email:
        vCodes = "".join(random.sample(letters,4))
        temp_codes.append(vCodes)
        print(temp_codes)
        message = Message(
            subject="检测系统验证码",
            recipients=[email],
            body="您的验证码为"+vCodes,
        )
        mail.send(message)
        return jsonify({"code":200}) #200表示正常的请求
    else:
        return jsonify({"code":400,"message":"请先传递邮箱"}) #返回后转化成register.js中的res

@bp.route("/register", methods=['GET','POST'])
def register():
    if request.method=='GET':
        return render_template("register.html",result=0)
    form = RegisterForm(request.form)
    if form.validate():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        vCodes = form.vCodes.data
        if vCodes not in temp_codes:
            return render_template("register.html",result=1)
        user_dict[email]={}
        user_dict[email]["username"] = username
        user_dict[email]["password"] = generate_password_hash(password)
        with open('./user.json','w') as fp:
            json.dump(user_dict,fp,indent=4)
        temp_codes.clear()
        return render_template("login.html",result=3)
    else:
        return redirect(url_for("user.register"))

# 验证码储存方式：memcached/redis/数据库

# @bp.route("/mail")
# def my_mail():
#     message = Message(subject="裂缝分割结果",
#                       recipients=["807077266@qq.com"],
#                       body="请查收附件",
#                       )
#     # "D:\MIT\MIT.rar"
#     with bp.open_resource("../MIT.rar") as fp:
#         # attach("文件名", "类型", 读取文件）
#         # message.attach("DMC.rar", 'application/octet-stream', fp.read())
#         message.attach("DMC.rar", 'application/x-rar-compressed', fp.read())
#
#     mail.send(message)
#     return "Seccesfully sending the message!"


@bp.route("/single")
@login_required
def single():
    return render_template("single.html")


@bp.route("/zip")
@login_required
def zip():
    return render_template("zip.html")

@bp.route("/zipOut")
def zipOut():
    return send_file('crack_result.zip', as_attachment=True)

@bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@bp.route("/search")
@login_required
def search():
    q = request.args.get("sName")
    img_list = glob.glob(os.path.join("static","*.png"))
    q = q.split('.')[0]
    for img in img_list:
        print(img)
        if q in img:
            return render_template("search_out.html",img=os.path.join("../",img))
    return render_template("search_out.html")
