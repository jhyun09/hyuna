from flask import Flask, redirect, url_for, render_template
from models import db, Post, Comment
from routes import post_bp
from auth import auth_bp
from admin import admin_bp
from flask_migrate import Migrate
from models import Category
from flask_wtf import CSRFProtect
from logging import FileHandler, Formatter

import os
import re
import logging

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///board.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'my_secret_key'
csrf = CSRFProtect(app)

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

# 로깅 설정 (디버깅 모드가 아닐 때만 적용)
if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    app.logger.addHandler(file_handler)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # 데이터베이스 생성 (마이그레이션을 사용하는 것이 좋음)

    port = int(os.environ.get("PORT", 10000))  # Render에서 포트 자동 할당
    app.run(host="0.0.0.0", port=port)
