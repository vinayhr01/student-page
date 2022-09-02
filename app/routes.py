import email
from logging import exception
from os import name
from datetime import datetime
from sys import modules
from flask import render_template, flash, request, redirect, url_for
from flask_login import login_manager, login_user, LoginManager, login_required, logout_user, current_user
from app import app
from app.forms import user_form,login_form,file_upload_form,SearchForm,PostForm,file_search_form,ReplyForm
from sqlalchemy import or_,desc
from flask_ckeditor import CKEditor
from app.database import db,Users,Posts,Notes,Replies,Trig,Notification,Subject
from werkzeug.security import generate_password_hash, check_password_hash 
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from flask_admin import Admin,expose,AdminIndexView






class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        trigs = Trig.query.order_by(desc(Trig.time_stamp)).all()
        return self.render('admin/index.html', trigs=trigs)

admin = Admin(app,index_view=MyHomeView())

ckeditor = CKEditor(app)

colleges=[('RNS','RNS Institute of Technology'),
('RV','RV College Of Engeneering'),
('BMS','BMS College Of Engeneering'),
('MSR','MSR Institute of Technology'),
('PES','PES University'),
('JSS','JSS Institute of Technology'),
('BNM','BNM Institute of Technology'),
]

mod=['1','2','3','4','5','all']

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = login_form()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			# Check the hash
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash("Login Succesfull!!")
				return redirect(url_for('user'))
			else:
				flash("Wrong Password - Try Again!")
		else:
			flash("That User Doesn't Exist! Try Again...")


	return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You Have Been Logged Out!  Thanks For Stopping By...")
	return redirect(url_for('login'))

@app.route('/')
def index():
    posts = Posts.query.order_by(desc(Posts.date_posted))
    notifications=None
    if current_user.is_authenticated:
        u_id=current_user.id
        notifications=Notification.query.filter_by(notify_id=u_id)
        notifications=notifications.order_by(desc(Notification.time_stamp)).limit(10).all()
    return render_template('index.html',posts=posts,notifications=notifications)

@app.route('/search', methods=["POST"])
def search():
	form = SearchForm()
	posts = Posts.query  
	if form.validate_on_submit():
		val = form.searched.data
		posts = posts.filter(or_(Posts.content.like('%' + val + '%'),Posts.slug.like('%' + val + '%'),Posts.title.like('%' + val + '%')))
		posts = posts.order_by(Posts.title).all()

		return render_template("search.html",form=form,searched = val,posts = posts)

@app.route('/user',methods=["GET","POST"])
@login_required
def user():
    form = user_form()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    return render_template('user.html',form=form,name_to_update=name_to_update)

@app.route('/register', methods=['GET','POST'])
def register_user():
    name=None
    form=user_form()
    form.college.choices=colleges
    if form.validate_on_submit():
        user=Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user=Users.query.filter_by(username=form.username.data).first()
            if user is None:
                hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
                user = Users(username=form.username.data, name=form.name.data, email=form.email.data, clg=form.college.data, password_hash=hashed_pw)
                if form.profile_pic.data:
                    img = request.files['profile_pic']
                    filename = secure_filename(img.filename)
                    pic_name = str(uuid.uuid1()) + "_" + filename
                    img.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                    user.profile_pic = pic_name
                db.session.add(user)
                db.session.commit()
                login_user(user)
                flash("User added successfully!!!!")
                flash("Login Succesfull!!")
                return redirect(url_for('user'))
            else:
                form.username.data = ''
                flash("Username already exists")
        else:
            flash("User already exists")
            form.email.data=''
    return render_template('register.html',form=form)

@app.route('/update_user/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    if id==current_user.id:
        user_to_update = Users.query.get_or_404(id)
        if request.method == "POST":
            user=Users.query.filter_by(email=request.form['email']).first()
            if user is None or request.form['email']==current_user.email:
                user=Users.query.filter_by(username=request.form['username']).first()
                if user is None or request.form['username']==current_user.username:
                    user_to_update.name = request.form['name']
                    user_to_update.email = request.form['email']
                    user_to_update.username = request.form['username']
                    if request.files['profile_pic']:
                        pic_to_delete=user_to_update.profile_pic
                        img = request.files['profile_pic']
                        filename = secure_filename(img.filename)
                        pic_name = str(uuid.uuid1()) + "_" + filename
                        img.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                        user_to_update.profile_pic = pic_name
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], pic_to_delete))
                        flash("Image Updated Successfully!")
                    try:
                        db.session.commit()
                        flash("User Updated Successfully!")
                        return redirect(url_for('user'))
                    except:
                        flash("Error!  Looks like there was a problem...try again!" )
                        return redirect(url_for('user'))
                else:
                    flash("Username already exists")
                    return redirect(url_for('user'))
            else:
                flash("Try a different email. This email already exits!!!")
                return redirect(url_for('user'))
        else:
            return redirect(url_for('user'))
    else:
        flash("You are not authorized!!!")
        return redirect(url_for('user'))

@app.route('/delete_user/<int:id>',methods=["POST","GET"])
@login_required
def delete_user(id):
    if id==current_user.id:
        user_to_delete = Users.query.get_or_404(id)
        try:
            logout_user()
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User Deleted Successfully!!")
            return redirect(url_for('index'))
        except:
            flash("Whoops! There was a problem deleting user, try again...")
            return redirect(url_for('user'))
    else:
        flash("You are not authorized to delete this account!!!")
        return redirect(url_for('user'))

@app.route('/upload',methods=["POST","GET"])
@login_required
def upload_file():
    form=file_upload_form()
    form.college.choices=colleges
    form.modules.choices=mod
    if form.validate_on_submit():
        if 'file' not in request.files:
            flash('No file attached!!')
            return render_template('upload_notes.html',form=form)
        file = request.files['file']
        filename = secure_filename(file.filename)
        if filename == '':
            flash('No selected file')
            return redirect(request.url)
        file_ext = os.path.splitext(file.filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            flash("Please upload in pdf or doc format" + str(file_ext))
        else:
            filename = str(form.subject.data) + "-" + str(form.modules.data) + "-" + str(form.college.data) + "-" + str(form.branch.data) + "-" + str(form.author.data) + str(file_ext)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            u_id=current_user.id
            notes=Notes(author=form.author.data, upload_id=u_id, sem=form.sem.data, branch=form.branch.data, subject=form.subject.data, college=form.college.data, module=form.modules.data, content=form.content.data, file=filename)
            db.session.add(notes)
            db.session.commit()
            flash('File Saved!!!!!')
            return redirect(url_for('upload_file'))
    return render_template('upload_notes.html',form=form)

@app.route('/download',methods=["POST","GET"])
@login_required
def download_file():
    today=datetime.utcnow()
    books=Notes.query.order_by(desc(Notes.date_uploaded)).limit(10).all()
    return render_template('download_notes.html',books=books,date=today.date())

@app.route('/delete_file/<int:id>',methods=["POST","GET"])
@login_required
def delete_file(id):
    book_to_delete=Notes.query.get_or_404(id)
    u_id = current_user.id
    if u_id == book_to_delete.uploader.id:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], book_to_delete.file))
            db.session.delete(book_to_delete)
            db.session.commit()

            # Return a message
            flash("Notes Was Deleted!")

        except:
            # Return an error message
            flash("Whoops! There was a problem deleting , try again...")

            # Grab all the posts from the database
            return redirect(url_for('my_uploads'))
    else:
        # Return a message
        flash("You Aren't Authorized To Delete That Note!")

    return redirect(url_for('my_uploads'))

@app.route('/my_uploads',methods=["POST","GET"])
@login_required
def my_uploads():
    today=datetime.utcnow()
    u_id=current_user.id
    books=Notes.query.filter_by(upload_id=u_id)
    books=books.order_by(desc(Notes.date_uploaded)).all()
    return render_template('my_uploads.html',books=books,date=today.date())

@app.route('/post',methods=["GET","POST"])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)        
        db.session.add(post)
        db.session.commit()
        flash("Post Submitted Successfully!")
        return redirect(url_for('add_post'))
    # Redirect to the webpage
    return render_template("post.html", form=form)

@app.route('/my_posts', methods=["GET","POST"])
@login_required
def view_my_posts():
    u_id=current_user.id
    posts = Posts.query.filter_by(poster_id = u_id)
    posts=posts.order_by(desc(Posts.date_posted)).all()
    return render_template("my_posts.html",posts = posts)

@app.route('/my_posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    u_id = current_user.id
    if u_id == post_to_delete.poster.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            # Return a message
            flash("Post Was Deleted!")

            # Grab all the posts from the database
            return redirect(url_for('view_my_posts'))


        except:
            # Return an error message
            flash("Whoops! There was a problem deleting post, try again...")

            # Grab all the posts from the database
            return redirect(url_for('view_my_posts'))
    else:
        # Return a message
        flash("You Aren't Authorized To Delete That Post!")

        # Grab all the posts from the database
        return redirect(url_for('view_my_posts'))

@app.route('/my_posts/edit_post/<int:id>',methods=["GET","POST"])
@login_required
def edit_post(id):
    u_id = current_user.id
    form=PostForm()
    post_to_update= Posts.query.get_or_404(id)
    if u_id == post_to_update.poster.id:
        if request.method=="POST":
            post_to_update.title = request.form['title']
            #post.author = form.author.data
            post_to_update.slug = request.form['slug']
            post_to_update.content = request.form['content']
            post_to_update.date_posted=datetime.utcnow()
            # Update Database
            db.session.add(post_to_update)
            db.session.commit()
            flash("Post Has Been Updated!")
            return redirect(url_for('view_my_posts'))
        else:
            form.title.data=post_to_update.title
            form.slug.data=post_to_update.slug
            form.content.data=post_to_update.content
            return render_template("edit_my_post.html",post=post_to_update,form=form)
    else:
        # Return a message
        flash("You Aren't Authorized To Edit That Post!")

        # Grab all the posts from the database
        return redirect(url_for('/'))

@app.route('/view_replies/<int:id>',methods=["GET","POST"])
def view_replies(id):
    post=Posts.query.get_or_404(id)
    replies=Replies.query.filter_by(post_for_id=id)
    replies=replies.order_by(desc(Replies.date_replied)).all()
    form=ReplyForm()
    if form.validate_on_submit() and request.method=="POST":
        u_id=current_user.id
        reply=Replies(content=form.content.data,post_for_id=id,reply_id=u_id)
        db.session.add(reply)
        db.session.commit()
        flash("Replied Successfully!")
        return redirect(url_for('view_replies',id=id))
    return render_template("view_replies.html",post=post,replies=replies,form=form)



@app.errorhandler(413)
def too_large(e):
    flash("File is too large!! Max size 20Mb.")
    return redirect(url_for('upload_file')), 413

@app.errorhandler(404)
def page_not_found(e):
    return "404 error", 404

@app.errorhandler(500)
def server_error(e):
    return "server error", 500