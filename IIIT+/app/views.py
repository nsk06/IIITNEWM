from flask import *
from flask_bootstrap import Bootstrap
from Key import Config
from werkzeug.urls import url_parse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import login_user, logout_user, current_user
from flask_login import login_required,LoginManager
import os
from elasticsearch import Elasticsearch
from flask_babel import *
app = Flask(__name__,static_url_path = "/static",static_folder = "static")
bootstrap = Bootstrap(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
log = LoginManager(app)
log.login_view = 'login'
from login import *
from database import *
from upload import *
from datetime import datetime
from flask_admin import *
from flask_admin.contrib.sqla import ModelView
from flask_moment import Moment
#app.config['SECRET_KEY'] = 'I have a dream'
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/static'
with app.app_context():
    # within this block, current_app points to app.
    print (current_app.name)

app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

configure_uploads(app, photos)
patch_request_class(app)

ad = "nonidh"
#print(app.config)
admin = Admin(app)

moment = Moment(app)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    #g.locale = str(get_locale())

@app.route('/',methods = ['GET','POST'])
@app.route('/index',methods=['GET','POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
prev_url=prev_url)
    #return render_template('index.html', title='Home', posts=posts)
@app.route('/Messages')
@login_required
def messages():
    msgs = Message.query.filter(Message.reciever == current_user.username)
    m = Message.query.filter(Message.sender == current_user.username)
    myMessages = msgs.union(m).all()
    return render_template('mymessages.html',title = 'Message',messages = myMessages)

@app.route('/send_message/<username>',methods=['GET','POST'])
@login_required
def send_message(username):
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(sender = current_user.username, msg = form.msg.data ,reciever = username)
        db.session.add(msg)
        db.session.commit()
        flash('Message sent!')
        return redirect(url_for('send_message',username = username))
        #form.about_me.data = current_user.about_me
    return render_template('send_message.html', title='Send Message',
                           form=form)

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)
@app.route('/Allgroups')
@login_required
def Allgroups():
    page = request.args.get('page', 1, type=int)
    groups = Group.query.all()
    d = set()
    for x in groups:
        d.add(x.groupname)
    d = list(d)
    #.paginate(
      #  page, app.config['POSTS_PER_PAGE'], False)
   # next_url = url_for('Allgroups', page=groups.next_num) \
       # if groups.has_next else None
  #  prev_url = url_for('Allgroups', page=groups.prev_num) \
     #   if groups.has_prev else None
    return render_template('Allgroups.html', title='Allgroups', groups=d)

@app.route('/groupview/<groupname>')
@login_required
def vu(groupname):
    cur_group = Group.query.filter_by(groupname = groupname).first()
    #print(cur_group)
    #page = request.args.get('page', 1, type=int)
    posts = cur_group.grouppost().all()
    events = Event.query.filter(Event.gr == groupname).all()
    gposts = Ingroup.query.filter(Ingroup.gp == groupname).all()
    access = Group.query.filter(Group.groupname == groupname).filter(Group.userid == current_user.id).all()
    if len(access) == 0:
        flash('You have to join the group!')
        return redirect(url_for('Allgroups'))
    #paginate(
        #page, app.config['POSTS_PER_PAGE'], False)
    #print(posts.items)
    #next_url = url_for('groupview', page=posts.next_num) \
       # if posts.has_next else None
    #prev_url = url_for('groupview', page=posts.prev_num) \
      #  if posts.has_prev else None
    else:
        return render_template('gview.html', title='Home',
                           posts=gposts,curr = groupname,events = events)


@app.route('/like/<pos>')
@login_required
def like(pos):
    x = Like.query.filter(Like.liker == current_user.username).all()
    if len(x) >= 1:
        flash('already liked')
        return redirect(url_for('index'))
    else:
        like = Like(liker = current_user.username, po = pos)
        db.session.add(like)
        db.session.commit()
        flash('You liked this')
        return redirect(url_for('index'))

@app.route('/groupjoin/<groupname>')
@login_required
def join(groupname):
    myad = Group.query.filter(Group.groupname == groupname).first()
    newgroupmem = Group(groupname = groupname, adminId = myad.adminId, userid = current_user.id )
    num = Group.query.filter(Group.groupname == groupname).filter(Group.userid == current_user.id).all()
    print(len(num))
    if len(num)  == 0:        
            print("yo")
            db.session.add(newgroupmem)
            db.session.commit()
            print("aaja")
            flash('You are now member of the group!')
            return redirect(url_for('Allgroups'))
    else:
        print("hi")
        flash('already member')
        return redirect(url_for('Allgroups'))

@app.route('/eventjoin/<eventname>')
@login_required
def eventjoin(eventname):
    my = Event.query.filter(Event.ev == eventname).first()
    my.participants+=1
    db.session.commit()
    c = my.gr
    print(c)
    flash('you have decided to join event!')
    return redirect(url_for('vu',groupname = c))


@app.route('/Mygroups')
@login_required
def my():
    page = request.args.get('page', 1, type=int)
    groups = Group.query.filter(Group.userid == current_user.id).all()
    print(groups)
    #.paginate(
       # page, app.config['POSTS_PER_PAGE'], False)
        #print(groups.items)
    #next_url = url_for('mygroups', page=groups.next_num) \
        #if groups.has_next else None
    #prev_url = url_for('mygroups', page=groups.prev_num) \
       # if groups.has_prev else None
    return render_template('mygroups.html', title='Mygroup', groups=groups)

@app.route('/login',methods  = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form,admin = ad)

@app.route('/admin',methods  = ['GET', 'POST'])
@login_required
def myadmin():
    pass


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url,admin = ad)

@app.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
@app.route('/Postgroup/<groupname>',methods=['GET','POST'])
@login_required
def Postgroup(groupname):
    form = PostForm()
    if form.validate_on_submit():
        post = Ingroup(pg=form.post.data, myuser=current_user.id,gp = groupname)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('Postgroup',groupname = groupname))
        #form.about_me.data = current_user.about_me
    return render_template('postgroup.html', title='Post In Group',
                           form=form)

@app.route('/GroupEvent/<groupname>',methods=['GET','POST'])
@login_required
def GroupEvent(groupname):
    form = PostForm()
    if form.validate_on_submit():
        event = Event(ev=form.post.data, organiser=current_user.username,gr = groupname,participants = 1)
        db.session.add(event)
        db.session.commit()
        flash('You have hosted an upcoming Event')
        return redirect(url_for('vu',groupname = groupname))
        #form.about_me.data = current_user.about_me
    return render_template('postgroup.html', title='Add Event',
                           form=form)

@app.route('/post/<i>',methods=['GET','POST'])
@login_required
def post(i):
    form=CommentForm()
    post=Post.query.get(int(i))
    if form.validate_on_submit():
        comment=Comment(body=form.post.data,post_id=i,us=current_user.username)
        db.session.add(comment)
        db.session.commit()
        flash('Comment Over')
        return redirect(url_for('index'))
    return render_template('comment.html',title='comment',form=form)

@app.route('/picture',methods=['GET','POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        myname = str(current_user.username)
        filename = photos.save(form.photo.data,myname,"profile.jpg")
        file_url = photos.url(filename)
        #print(file_url)
    else:
        file_url = None
    return render_template('upload.html', form=form, file_url=file_url)

@app.route('/Create_Group',methods=['GET','POST'])
@login_required
def group():
    form = GroupForm()
    if form.validate_on_submit():
        group = Group(groupname = form.name.data, adminId = current_user.id, userid = current_user.id)
        if Group.query.filter(Group.groupname == group.groupname).count() == 0:
            db.session.add(group)
            db.session.commit()
        else:
            flash("already exists")
            return redirect(url_for('my'))
        #print(group.groupname)
    return render_template('creategroup.html',form = form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/search')
@login_required
def search():
    #print("hi")
    #print(current_app)
    if not g.search_form.validate():
        return redirect(url_for('explore'))
    #print("yo")
    page = request.args.get('page', 1, type=int)
    print(g.search_form.q.data)
    posts,total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    print(total)
    for x in posts:
        print(x.body)
    next_url = url_for('search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='Search', posts=posts,
                           next_url=next_url, prev_url=prev_url)


class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.username == ad:
            return True
        else:
            return False

admin.add_view(MyModelView(User,db.session))
admin.add_view(MyModelView(Post,db.session))
admin.add_view(MyModelView(Group,db.session))
admin.add_view(MyModelView(Ingroup,db.session))
admin.add_view(MyModelView(Message,db.session))
admin.add_view(MyModelView(Comment,db.session))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
if __name__ == '__main__':
    app.debug = True
    app.run()
