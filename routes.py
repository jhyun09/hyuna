from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from models import db, Post, Comment, Category
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from functools import wraps
import html
import re
from base64 import b64decode

# 블루프린트 정의
post_bp = Blueprint("post", __name__, url_prefix="/post")

# 로그인 체크 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("로그인이 필요합니다.")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

# 첫 번째 이미지 src 추출 함수
def extract_first_img_src(html_content):
    if not html_content:
        return None
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html_content)
    return match.group(1) if match else None

# 홈 리디렉션: / → 자유게시판
@post_bp.route("/")
def home():
    return redirect(url_for("post.index", category="자유게시판", page=1))

# 게시글 목록 (페이지네이션 포함)
@post_bp.route("/<category>")
@post_bp.route("/<category>/page/<int:page>")
@login_required
def index(category="자유게시판", page=1):
    q = request.args.get("q", "")
    per_page = 12
    query = Post.query.filter_by(category=category)

    if q:
        search = f"%{q}%"
        query = query.filter(
            db.or_(
                Post.title.like(search),
                Post.author.like(search)
            )
        )

    posts = query.order_by(Post.id.desc()).paginate(page=page, per_page=per_page)

    # 🔍 범위 계산 (Jinja에서 max/min 못 쓰니까 여기서 처리!)
    start_page = max(page - 5, 1)
    end_page = min(page + 4, posts.pages)  # 총 10개까지 표시되도록

    category_objects = {c.name: c for c in Category.query.all()}
    category_type = category_objects.get(category).type if category in category_objects else "text"

    category_obj = category_objects.get(category)
    is_gallery_category = category_obj.type == "photo" if category_obj else False

    for post in posts.items:
        decoded_content = html.unescape(post.content or "")
        match = re.search(r'<img[^>]+src=["\']?([^"\'>]+)["\']?', decoded_content)
        post.first_img_src = match.group(1) if match else None

    return render_template(
        "index.html",
        posts=posts,
        category=category,
        category_type=category_type,
        is_gallery_category=is_gallery_category,
        q=q,
        category_objects=category_objects,
        start_page=start_page,       # ✅ 템플릿으로 전달
        end_page=end_page            # ✅ 템플릿으로 전달
    )


# 게시글 상세 + 댓글 등록
@post_bp.route("/<int:post_id>", methods=["GET", "POST"])
@login_required
def detail(post_id):
    post = Post.query.get_or_404(post_id)

    # 갤러리 게시판 확인
    category_obj = Category.query.filter_by(name=post.category).first()
    is_gallery_category = category_obj.type == "photo" if category_obj else False


    if request.method == "POST":
        author = request.form["author"]
        content = request.form["content"]
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        comment = Comment(author=author, content=content, created_at=created_at, post=post)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for("post.detail", post_id=post_id))

    return render_template("detail.html", post=post, is_gallery_category=is_gallery_category)

# 새 글 작성
@post_bp.route("/write", methods=["GET", "POST"])
@login_required
def write():
    category = request.args.get("category", "자유게시판")

    # ✅ 추가: category 객체 조회 + 타입 확인
    category_obj = Category.query.filter_by(name=category).first()
    is_gallery_category = category_obj.type == "photo" if category_obj else False

    if request.method == "POST":
        # 폼 데이터 확인
        title = request.form.get("title")
        author = request.form.get("author")
        content = request.form.get("content")
        print(f"Title: {title}, Author: {author}, Content: {content}")  # 디버깅 로그

        # 필수 항목 확인
        if not title or not author or not content:
            flash("제목, 작성자, 내용은 필수 항목입니다.", "error")
            return render_template("write.html", category=category, is_gallery_category=is_gallery_category)

        # 이미지 업로드 처리
        image = request.files.get("image")
        if image and image.filename:
            filename = secure_filename(image.filename)
            image_path = os.path.join("static", "uploads", filename)
            try:
                image.save(image_path)
                content += f'<br><img src="/{image_path}" alt="첨부이미지">'
            except Exception as e:
                flash(f"이미지 업로드에 실패했습니다: {str(e)}", "error")
                return render_template("write.html", category=category, is_gallery_category=is_gallery_category)

        # DB 저장
        post = Post(
            title=title,
            author=author,
            content=content,
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            read_count=0,
            category=category
        )
        db.session.add(post)
        db.session.commit()

        flash("새 글이 성공적으로 등록되었습니다.", "success")
        return redirect(url_for("post.index", category=category, page=1))

    # ✅ 다크테마 전달
    return render_template("write.html", category=category, is_gallery_category=is_gallery_category)




# 글 수정
@post_bp.route("/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)

    category_obj = Category.query.filter_by(name=post.category).first()
    is_gallery_category = category_obj.type == "photo" if category_obj else False

    
    if request.method == "POST":
        post.title = request.form["title"]
        post.author = request.form["author"]
        post.content = request.form["content"]

        image = request.files.get("image")
        if image and image.filename:
            filename = secure_filename(image.filename)
            image_path = os.path.join("static", "uploads", filename)
            try:
                image.save(image_path)
                post.content += f'<br><img src="/{image_path}" alt="첨부이미지">'
            except Exception as e:
                flash(f"이미지 업로드 실패: {str(e)}", "error")
                return redirect(request.url)

        db.session.commit()
        flash("글이 수정되었습니다.", "success")
        return redirect(url_for("post.detail", post_id=post.id))

    return render_template("edit.html", post=post, is_gallery_category=is_gallery_category)

# 글 삭제
@post_bp.route("/delete/<int:post_id>", methods=["POST"])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    pw = request.form.get("password", "")
    real_pw = b64decode(post.password).decode() if hasattr(post, "password") else ""

    if pw != real_pw:
        return "<script>alert('비밀번호가 틀렸습니다!');history.back();</script>"

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("post.index", category=post.category, page=1))

# 댓글 수정
@post_bp.route("/comment/edit/<int:comment_id>", methods=["GET", "POST"])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if request.method == "POST":
        comment.author = request.form["author"]
        comment.content = request.form["content"]
        db.session.commit()
        return redirect(url_for("post.detail", post_id=comment.post_id))
    return render_template("edit_comment.html", comment=comment)

# 댓글 삭제
@post_bp.route("/comment/delete/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for("post.detail", post_id=comment.post_id))

# 관리자 페이지
@post_bp.route("/admin")
@login_required
def admin():
    posts = Post.query.order_by(Post.id.desc()).all()
    comments = Comment.query.order_by(Comment.id.desc()).all()
    return render_template("admin.html", posts=posts, comments=comments)

# 배치 삭제
@post_bp.route("/admin/delete", methods=["POST"])
@login_required
def bulk_delete():
    ids = request.form.getlist("post_ids")
    for post_id in ids:
        post = Post.query.get(post_id)
        if post:
            db.session.delete(post)
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))

# 이미지 업로드
@post_bp.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    file = request.files.get('upload')  # CKEditor는 이 키를 사용!
    
    if not file:
        return jsonify({"error": {"message": "파일이 첨부되지 않았습니다"}}), 400

    # 파일명 안전하게 처리
    filename = secure_filename(file.filename)
    save_path = os.path.join('static', 'uploads', filename)
    
    try:
        file.save(save_path)
        url = url_for('static', filename=f'uploads/{filename}', _external=False)
        return jsonify({ "url": url })  # ✅ 반드시 이 형태여야 CKEditor가 성공 인식!

    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

@post_bp.route("/comment/bulk-delete", methods=["POST"])
@login_required
def bulk_delete_comment():
    ids = request.form.getlist("comment_ids")
    for comment_id in ids:
        comment = Comment.query.get(comment_id)
        if comment:
            db.session.delete(comment)
    db.session.commit()
    return redirect(url_for("post.admin"))

