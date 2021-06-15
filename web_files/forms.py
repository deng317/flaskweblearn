from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField
from wtforms import validators
from wtforms.validators import DataRequired,Length,EqualTo,Email, ValidationError
from web_files.dbmodel import User
from web_files import bcrypt

from flask_login import current_user


class RegisterForms(FlaskForm):
    username = StringField('昵称',validators=[DataRequired(message="请输入用户名"),Length(min=2,max=20)])
    email = StringField('邮箱',validators=[DataRequired(message='请输入邮箱'),Email()])
    password = PasswordField('请输入密码',validators=[DataRequired(message='请输入密码')])
    confirm_password = PasswordField('请再次输入密码',validators=[DataRequired(message='请输入密码'),EqualTo('password',message='两次输入密码不一致')])
    submit = SubmitField ('提交')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("不好意思，用户名已经被注册了，请更换一个")

    def validate_email(self,email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("不好意思,邮箱已经被注册了，请更换一个")

class UpdateAccountForm(FlaskForm):
    username = StringField('昵称',validators=[DataRequired(message="请输入用户名"),Length(min=2,max=20)])
    email = StringField('邮箱',validators=[DataRequired(message='请输入邮箱'),Email()])
    submit = SubmitField ('提交')
    picture = FileField('我的头像',validators=[FileAllowed(['jpg','png'])])

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("不好意思，用户名已经被注册了，请更换一个")

    def validate_email(self,email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError("不好意思,邮箱已经被注册了，请更换一个")


class LoginForms(FlaskForm):
    email = StringField('邮箱',validators=[DataRequired(message='请输入注册的邮箱'),Email(message='邮箱格式不正确')])
    password = PasswordField('密码',[DataRequired(message='请输入密码')])
    remember = BooleanField('记住我，下次就不用再登录了哟')
    submit = SubmitField ('Log In')

class Add_Post(FlaskForm):
    post_title = StringField('标题',[DataRequired(message=''),Length(min=1,max=100)])
    content = TextAreaField('内容',[DataRequired(message='')])
    submit = SubmitField ('点我发布')

class Add_Product(FlaskForm):
    picture_name = StringField('标题',[DataRequired(message=''),Length(min=2,max=100)])
    upload_time = StringField('内容',[DataRequired(message=''),Length(min=2,max=100)])
    picture_content = TextAreaField('产品描述',[DataRequired(message='')])
    picture = FileField('产品图片',validators=[FileAllowed(['jpg','png','Jpeg'])])
    submit = SubmitField ('点我上传')

class RequestResetForm(FlaskForm):
    email = StringField('邮箱',validators=[DataRequired(),Email()])
    submit = SubmitField ('提交')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data)
        if user is None:
            raise ValidationError("找不到对应账户")

class UpdatePasswordForm(FlaskForm):
    oldpassword = PasswordField('原密码',validators=[DataRequired(message="请输入原密码"),Length(min=2,max=20)])
    newpassword = PasswordField('新密码',validators=[DataRequired(message="请输入新密码"),Length(min=2,max=20)])
    confirm_newpassword = PasswordField('再次输入新密码',validators=[DataRequired(message="请再次输入输入原密码"),Length(min=2,max=20),EqualTo('newpassword')])
    submit = SubmitField ('提交')

    def validate_oldpassword(self, oldpassword):
        user=bcrypt.check_password_hash(current_user.password,oldpassword.data)
        if not user:
            raise ValidationError("原密码输入错误，请重试！")

class ResetPasswordForm(FlaskForm):
    newpassword = PasswordField('新密码',validators=[DataRequired(message="请输入新密码"),Length(min=2,max=20)])
    confirm_newpassword = PasswordField('再次输入新密码',validators=[DataRequired(message="请再次输入输入原密码"),EqualTo('newpassword',message='两次输入密码要一致才行哦，再试一次吧。')])
    submit = SubmitField ('提交')

