from views import db,log
from datetime import datetime
from passlib.apps import custom_app_context as pwd_context
from passlib.context import CryptContext
from flask_login import UserMixin
#from login import Login
from search import *
from login import *
class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            print("oh no")
            return cls.query.filter_by(id=0), 0
        when = []
        print("yes")
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': [obj for obj in session.new if isinstance(obj, cls)],
            'update': [obj for obj in session.dirty if isinstance(obj, cls)],
            'delete': [obj for obj in session.deleted if isinstance(obj, cls)]
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['update']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['delete']:
            remove_from_index(cls.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

pwd_context = CryptContext(

    schemes=["pbkdf2_sha512"],
    default="pbkdf2_sha512",
    all__vary_rounds = 0.2,
    pbkdf2_sha512__default_rounds = 8000,
    )

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)
#group = db.Table('Groups',
  #  db.Column('userid',db.Integer,db.ForeignKey('user.id')),
   # db.Column('groupname',db.String(64),index=True,unique=True))

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    gposts = db.relationship('Ingroup', backref='writer', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    comments=db.relationship('Comment', backref='creator', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)
    def set_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def check_password(self, password):
        return pwd_context.verify(password,self.password_hash)
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        for p in followed:
            form1 = CommentForm()
            if form1.validate_on_submit():
                post = Post(body=form1.post.data, author=current_user)
                db.session.add(post)
                db.session.commit()
                flash('You just now commented Wohoo XD!')
                return redirect(url_for('index'))
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
        

@log.user_loader
def load_user(id):
    return User.query.get(int(id))

class Post(SearchableMixin,db.Model):
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    commentS = db.relationship('Comment', backref='POst', lazy='dynamic')

    #def get_comments(self):
     #   return Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.desc())

    def __repr__(self):
        return '<Post {}>'.format(self.body)
db.event.listen(db.session, 'before_commit', Post.before_commit)
db.event.listen(db.session, 'after_commit', Post.after_commit)
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime,index=True, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    us= db.Column(db.String(64), db.ForeignKey('user.username'))
    def __repr__(self):
        return '<Comment {}>'.format(self.body)
class Group(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    userid = db.Column(db.Integer,db.ForeignKey('user.id'))
    groupname = db.Column(db.String(64),index=True)
    adminId =  db.Column(db.Integer)

    def __repr__(self):
        return '<Group {}>'.format(self.groupname)
    def addMember(self,user):
        if not self.is_member(user):
            self.members.append(user)
    def is_member(self, user):
        return self.members.filter(
            group.c.self.userid == user.id).count() > 0                                     
    def removeMember(self,user):
        if self.is_member(user):
            self.members.remove(user)
    def grouppost(self):
        gname=self.groupname
        groupusers = Group.query.filter(Group.groupname == gname).all()
        #groupusers = groupusers.items
        #print(groupusers)
        for mem in groupusers:
            groupposts = Post.query.filter(mem.userid == Post.user_id)
        return groupposts.order_by(Post.timestamp.desc())

class Ingroup(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    myuser = db.Column(db.Integer,db.ForeignKey('user.id'))
    gp = db.Column(db.String(64),db.ForeignKey('group.groupname'))
    pg = db.Column(db.String(140))
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
class Event(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    gr = db.Column(db.String(64),db.ForeignKey('group.groupname'))
    ev = db.Column(db.String(140))
    participants = db.Column(db.Integer)
    organiser = db.Column(db.Integer,db.ForeignKey('user.username')) 
class Message(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    sender = db.Column(db.String(64),db.ForeignKey('user.username'))
    msg = db.Column(db.String(700),index=True)
    reciever = db.Column(db.String(64),db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    def __repr__(self):
        return '<Message {}>'.format(self.body)