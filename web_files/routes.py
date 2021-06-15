import os
import secrets
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message
from web_files import tiebadb,app,db,bcrypt,mail
from flask import render_template,url_for,flash,redirect,request,abort
from web_files.forms import RegisterForms,LoginForms,Add_Post,UpdateAccountForm,UpdatePasswordForm,Add_Product,RequestResetForm,ResetPasswordForm
import time
from PIL import Image
from web_files.dbmodel import User,Post,Picture
from datetime import datetime


@app.route('/cover')
def cover():
    return render_template('cover.html')

#主页
@app.route('/',methods=['GET','POST'])
def index():
    page = request.args.get('page',1,type=int)
    posts=Post.query.order_by(Post.post_time.desc()).paginate(per_page=5)
    
    return render_template('main.html',posts=posts)

#关于我们
@app.route('/about')
def about():
    return render_template('about.html',title='关于我们')

#注册页面
@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated :
        return redirect (url_for('index'))
    form = RegisterForms()
    if form.validate_on_submit():
        hashed_passwd=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data,email=form.email.data,password=hashed_passwd)
        try:
            tiebadb.save_user_info(form.username.data,form.email.data,hashed_passwd)
            db.create_all()
            db.session.add(user)
            db.session.commit()
            flash('[{}] 您好，欢迎加入,请登录'.format(form.username.data),'success')
            return redirect (url_for('login'))
        except:
            flash('邮箱已被注册，请确认。','danger')
            return redirect (url_for('register'))
    return render_template('register.html',form=form,title='注册页面')

#登录页面
@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated :
        return redirect (url_for('index'))
    form = LoginForms()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not bcrypt.check_password_hash(user.password,form.password.data):
            flash('登录失败，用户名或密码错误，请确认一下哟','danger')
            return redirect(url_for('login'))
        login_user(user,remember=form.remember.data)
        flash('登录成功','success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('index')) 
    return render_template('login.html',form=form,title="登录页面")

#登出
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#用户信息
@app.route('/account')
@login_required
def account():
    image_file =url_for("static",filename="pic/"+current_user.image)
    return render_template('account.html',image_file=image_file)

#添加文章
@app.route('/addpost',methods=['GET','POST'])
@login_required
def addpost():
    form=Add_Post()
    if form.validate_on_submit():
        now_time=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        post=Post(userID= current_user.id,post_title=form.post_title.data,post_content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(f'发帖成功!!!','success')
        return redirect (url_for('index'))
    return render_template('addpost.html',form=form , legend = '发表文章',title='发表文章')


'''Updage user infomation'''
def save_icon_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,file_extention = os.path.splitext(form_picture.filename)
    picture_file_name= random_hex + file_extention
    picture_path = os.path.join(app.root_path,"static/pic",picture_file_name)

    # Re-size image
    output_pic_size=(100,100)
    thumbnail_img=Image.open(form_picture)
    thumbnail_img.thumbnail(output_pic_size)
    thumbnail_img.save(picture_path)
    # form_picture.save(picture_path)
    return picture_file_name

#更新个人信息
@app.route('/update_info',methods=['GET','POST'])
@login_required
def update_info():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username=form.username.data
        current_user.email = form.email.data
        if form.picture.data:
            current_user.image = save_icon_picture(form.picture.data)
        db.session.commit()
        flash('个人信息更新成功','success')
        return redirect(url_for('account'))
    elif request.method== "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file =url_for("static",filename="pic/"+current_user.image)
    return render_template('update_info.html',form=form,image_file=image_file,title='更新个人信息')

#依据原密码，更新密码
@app.route('/update_password',methods=['GET','POST'])
@login_required
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        current_user.password=bcrypt.generate_password_hash(form.newpassword.data).decode('utf-8')
        db.session.commit()
        flash('密码修改成功','success')
        return redirect(url_for('account'))
    return render_template('update_password.html',form=form)

def send_reset_mail(user):
    token=user.get_reset_token()
    msg=Message('重置用户信息邮件', sender='我<dwyyue@163.com>', recipients=[user.email])
    msg.body=f'''请查看以下链接进行密码更新,链接10分钟内有效:\n{url_for('reset_password',token=token, _external=True)}'''
    mail.send(msg)


#忘记密码，请求变更密码链接
@app.route('/request_reset',methods=['GET','POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=RequestResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        
        send_reset_mail(user)
        flash('重置密码链接已发送到您邮箱，请在10分钟内打开链接重置密码后再来登录！！！','success')
        return redirect(url_for('login'))
        
    return render_template('request_reset.html',form=form,title="找回密码")

#依据邮件链接，变更密码
@app.route('/reset_password/<string:token>',methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=ResetPasswordForm()
    user=User.verify_token(token)
    if user != None:
        if form.validate_on_submit():
            user.password= bcrypt.generate_password_hash(form.newpassword.data).decode('utf-8')
            db.session.commit()
            flash("密码更新成功","success")
            return redirect(url_for('login'))
    else:
        flash("密码重置链接已过期，请重新发送请求",'danger')
        return redirect(url_for('request_reset'))
    return render_template('reset_password.html',form=form,token=token,title='重置密码')


#产品页面
@app.route('/products',methods=['GET','POST'])
def gallery():
    db.create_all()
    pictures=Picture.query.all()
    return render_template('gallery.html',pictures=pictures)

#upload picture function
def save_product_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,file_extention = os.path.splitext(form_picture.filename)
    picture_file_name= random_hex + file_extention
    picture_path = os.path.join(app.root_path,"static/products",picture_file_name)
    # re size picture
    output_image_size=(1000,1000)
    thumbnail_img = Image.open(form_picture)
    thumbnail_img.thumbnail(output_image_size)
    thumbnail_img.save(picture_path)
    # form_picture.save(picture_path)
    return picture_file_name

#上传图片
@app.route('/upload_product',methods=['GET','POST'])
@login_required
def upload_product():
    form = Add_Product()
    if form.validate_on_submit():
        if form.picture.data:
            product_picture_name = save_product_picture(form.picture.data)
            picture=Picture(picture_name = form.picture_name.data,picture_content = form.picture_content.data,picture_path = product_picture_name)
            db.session.add(picture)
            db.session.commit()
            flash('产品信息上传成功','success')
            image_name=product_picture_name
            image_file = url_for('static',filename='products/'+image_name)
        else:
            flash('产品信息上传失败','danger')
        return render_template('upload_product.html',form=form,image_file=image_file)
    elif request.method== "GET":
        image_name='default.jpg'
    image_file = url_for('static',filename='products/'+image_name)
    return render_template('upload_product.html',form=form,image_file=image_file)

#文章页面
@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html',post=post)

#更新文章
@app.route('/post/<int:post_id>/update',methods=['GET','POST'])
@login_required
def updatepost(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = Add_Post()
    if form.validate_on_submit():
        now_time=datetime.now()
        post.post_title=form.post_title.data
        post.post_content=form.content.data
        post.post_time = now_time
        db.session.commit()
        flash(f'更新成功!!!','success')
        return redirect (url_for('post',post_id=post_id))
    elif request.method == 'GET':
        form.post_title.data = post.post_title
        form.content.data = post.post_content
    return render_template('addpost.html',form=form,legend='更新内容' )


#删除文章
@app.route('/post/<int:post_id>/delete',methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

#切换用户-登出
@app.route('/account/change_account',methods=['POST'])
@login_required
def change_account():
    logout_user()
    return redirect(url_for('login',title='更新个人信息'))

#依据用户名查询文章
@app.route('/<username>-posts',methods=['GET','POST'])
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user=User.query.filter_by(username=username).first()
    posts=Post.query.filter_by(author=user).order_by(Post.post_time.desc()).paginate(page=page,per_page=5)
    return render_template('user_posts.html',posts=posts,user=user,title=f'{user.username}的文章')


@app.route('/test')
def test():
    form1=RequestResetForm()
    return render_template('test.html',form1=form1)
