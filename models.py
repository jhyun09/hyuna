from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# 게시글 모델
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    author = db.Column(db.String(50))
    content = db.Column(db.Text)
    date = db.Column(db.String(20))
    read_count = db.Column(db.Integer)
    category = db.Column(db.String(50), nullable=False, default="자유게시판")
    password = db.Column(db.String(200), nullable=True)  # 게시글 비밀번호 (옵션)

    # 💬 댓글 연결
    comments = db.relationship(
        'Comment',
        backref='post',
        cascade='all, delete-orphan',
        lazy=True
    )

    def __repr__(self):
        return f"<Post {self.id} | {self.title}>"

    # 비밀번호 보호된 게시글 체크
    def check_password(self, password):
        return check_password_hash(self.password, password) if self.password else True

# 댓글 모델
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50))
    content = db.Column(db.Text)
    created_at = db.Column(db.String(20))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return f"<Comment {self.id} | post_id={self.post_id}>"

# 사용자 모델
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # 이메일 필드 추가
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # 관리자 여부
    is_active = db.Column(db.Boolean, default=False)  # 승인 상태

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

# 카테고리 모델
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # 카테고리 이름
    type = db.Column(db.String(20), default="text")  # 카테고리 타입 (text / photo 등)
    description = db.Column(db.Text, nullable=True)  # 카테고리 설명

    def __repr__(self):
        return f"<Category {self.name}>"

