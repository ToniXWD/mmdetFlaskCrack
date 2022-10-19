import wtforms
from wtforms.validators import length,email
from .inf import temp_codes, user_dict

class RegisterForm(wtforms.Form):
    username = wtforms.StringField(validators=[length(min=3,max=20)])
    email = wtforms.StringField(validators=[email()])
    password = wtforms.StringField(validators=[length(min=6,max=20)])
    vCodes = wtforms.StringField(validators=[length(min=4,max=4)])

    # def validate_vCodes(self, field):
    #     print(temp_codes)
    #     Codes = field.data
    #     if not Codes in temp_codes:
    #         raise wtforms.ValidationError("邮箱验证码错误!")
    # def validate_email(self, field):
    #     mail = field.data
    #     if mail in user_dict.keys():
    #         raise wtforms.ValidationError("邮箱已注册，请登录")

class LoginForm(wtforms.Form):
    email = wtforms.StringField(validators=[email()])
    password = wtforms.StringField(validators=[length(min=6,max=20)])

    # def validate_email(self, field):
    #     mail = field.data
    #     if mail not in user_dict.keys():
    #         raise wtforms.ValidationError("邮箱未注册，请注册")