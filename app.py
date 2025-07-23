from flask import Flask, redirect, url_for, render_template
from models import db, Post, Comment
from routes import post_bp
from auth import auth_bp
from admin import admin_bp
from flask_migrate import Migrate
from models import Category
import re

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///board.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'my_secret_key'

db.init_app(app)
migrate = Migrate(app, db)

# ✅ Jinja 템플릿 필터 등록
@app.template_filter("regex_search")
def regex_search(value, pattern, group=0):
    match = re.search(pattern, value)
    return match.group(group) if match else ""

# ✅ 라우트: 홈으로 접근 시 자유게시판으로 이동
@app.route("/")
def home():
    all_categories = Category.query.order_by(Category.name).all()
    default_names = ['자유게시판', '이야기게시판', '사진게시판', '습작게시판', '쭈야랑게시판']

    # 갤러리 게시판 카테고리 목록
    gallery_categories = ['사진게시판', '습작게시판', '쭈야랑게시판']

    # 기본 카테고리 (갤러리 게시판 포함)
    default_categories = [c for c in all_categories if c.name in default_names]
    
    # 갤러리 카테고리에 해당하는 카테고리들만 따로 구분
    gallery_categories_obj = [c for c in all_categories if c.name in gallery_categories]

    # 사용자 정의 카테고리
    custom_categories = [c for c in all_categories if c.name not in default_names]

    return render_template("main.html", 
                           default_categories=default_categories, 
                           custom_categories=custom_categories, 
                           gallery_categories=gallery_categories_obj)
# 블루프린트 등록
app.register_blueprint(admin_bp)
app.register_blueprint(post_bp)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
