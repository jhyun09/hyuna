from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models import Post, Comment, User, Category, db
from werkzeug.security import generate_password_hash
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 관리자 권한 체크
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('관리자만 접근할 수 있습니다.')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# IP 제한
def ip_restricted(allowed_prefixes):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            client_ip = request.remote_addr
            if not any(client_ip.startswith(prefix) for prefix in allowed_prefixes):
                flash(f'허용되지 않은 IP({client_ip})에서의 접근입니다.')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

# 관리자 대시보드
@admin_bp.route('/')
@admin_required
@ip_restricted(['127.', '192.168.'])
def admin_dashboard():
    categories = Category.query.order_by(Category.name).all()
    selected_category = request.args.get('category', '전체')

    if selected_category == '전체':
        posts = Post.query.order_by(Post.id.desc()).all()
    else:
        posts = Post.query.filter_by(category=selected_category).order_by(Post.id.desc()).all()

    post_ids = [p.id for p in posts]
    comments = Comment.query.filter(Comment.post_id.in_(post_ids)).order_by(Comment.id.desc()).all()

    # ✅ 여기가 핵심!
    pending_users = User.query.filter_by(is_active=False).order_by(User.created_at.desc()).all()

    return render_template(
        'admin_dashboard.html',
        posts=posts,
        comments=comments,
        categories=categories,
        selected_category=selected_category,
        pending_users=pending_users  # ✅ 추가!
    )

# 비밀번호 변경
@admin_bp.route('/change_password', methods=['GET', 'POST'])
@admin_required
@ip_restricted(['127.', '192.168.'])
def change_password():
    if request.method == 'POST':
        current_pw = request.form.get('current_password')
        new_pw = request.form.get('new_password')
        confirm_pw = request.form.get('confirm_password')

        user_id = session.get('user_id')
        user = User.query.get(user_id)

        if not user or not user.check_password(current_pw):
            flash('현재 비밀번호가 올바르지 않습니다.')
            return redirect(url_for('admin.change_password'))

        if new_pw != confirm_pw:
            flash('새 비밀번호와 확인 비밀번호가 일치하지 않습니다.')
            return redirect(url_for('admin.change_password'))

        user.password_hash = generate_password_hash(new_pw)
        db.session.commit()

        flash('비밀번호가 성공적으로 변경되었습니다.')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin_change_password.html')

# 게시판 추가
@admin_bp.route('/add_category', methods=['POST'])
@admin_required
@ip_restricted(['127.', '192.168.'])
def add_category():
    name = request.form.get('category_name')
    category_type = request.form.get('category_type')

    if not name:
        flash('게시판 이름을 입력하세요.')
        return redirect(url_for('admin.admin_dashboard'))

    if Category.query.filter_by(name=name).first():
        flash('이미 존재하는 게시판입니다.')
        return redirect(url_for('admin.admin_dashboard'))

    new_category = Category(name=name, type=category_type)
    db.session.add(new_category)
    db.session.commit()
    flash(f'{name} 게시판이 추가되었습니다.')

    return redirect(url_for('admin.admin_dashboard'))


# 게시판 삭제 (수정 완료!)
@admin_bp.route('/delete_category', methods=['POST'])
@admin_required
@ip_restricted(['127.', '192.168.'])
def delete_category():
    cat_id = request.form.get('category_id')

    if not cat_id:
        flash('삭제할 게시판 ID가 전달되지 않았습니다.')
        return redirect(url_for('admin.admin_dashboard'))

    category = Category.query.get(cat_id)
    if not category:
        flash('해당 게시판이 존재하지 않습니다.')
        return redirect(url_for('admin.admin_dashboard'))

    # 이 게시판 이름과 일치하는 글 삭제
    Post.query.filter_by(category=category.name).delete()

    db.session.delete(category)
    db.session.commit()

    flash(f"'{category.name}' 게시판이 삭제되었습니다.")
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/edit_category', methods=['POST'])
@admin_required
@ip_restricted(['127.', '192.168.'])
def edit_category():
    category_id = request.form.get('category_id')
    category_type = request.form.get('category_type')

    category = Category.query.get(category_id)
    if category:
        category.type = category_type
        db.session.commit()
        flash(f"{category.name} 게시판 타입이 '{category_type}'로 변경되었습니다.")
    else:
        flash("해당 게시판이 존재하지 않습니다.")

    return redirect(url_for('admin.admin_dashboard'))

# 승인 대기 중인 사용자 리스트
@admin_bp.route('/users/pending')
@admin_required
@ip_restricted(['127.', '192.168.'])
def pending_users():
    users = User.query.filter_by(is_active=False).all()
    return render_template('admin_pending_users.html', users=users)

# 사용자 승인
@admin_bp.route('/users/approve/<int:user_id>', methods=['POST'])
@admin_required
@ip_restricted(['127.', '192.168.'])
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash(f"사용자 {user.username} 님이 승인되었습니다.")
    return redirect(url_for('admin.pending_users'))

# 사용자 삭제 (승인 거절)
@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
@ip_restricted(['127.', '192.168.'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"사용자 {user.username} 님이 삭제되었습니다.")
    return redirect(url_for('admin.pending_users'))

