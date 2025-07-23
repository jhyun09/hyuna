from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    author = db.Column(db.String(50))
    content = db.Column(db.Text)
    date = db.Column(db.String(20))
    read_count = db.Column(db.Integer)
    category = db.Column(db.String(50), nullable=False, default="자유게시판")
       
    # 💬 댓글 연결
    comments = db.relationship(
        'Comment',
        backref='post',
        cascade='all, delete-orphan',
        lazy=True
    )

    def __repr__(self):
        return f"<Post {self.id} | {self.title}>"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50))
    content = db.Column(db.Text)
    created_at = db.Column(db.String(20))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return f"<Comment {self.id} | post_id={self.post_id}>"
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)    
    

# models.py
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(20), default="text") 