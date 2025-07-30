from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, db
from datetime import datetime, timedelta
from urllib.parse import urlparse

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# 로그인 시도 제한 설정
MAX_ATTEMPTS = 5
LOCK_TIME_MINUTES = 5

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        now = datetime.now()

        # 로그인 시도 제한: 실패 횟수 및 잠금 체크
        if "lock_until" in session and now < session["lock_until"]:
            remaining = (session["lock_until"] - now).seconds // 60 + 1
            flash(f"🔒 너무 많은 로그인 시도로 잠금 중입니다. {remaining}분 후 다시 시도하세요.")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            session["failed_attempts"] = session.get("failed_attempts", 0) + 1

            if session["failed_attempts"] >= MAX_ATTEMPTS:
                session["lock_until"] = now + timedelta(minutes=LOCK_TIME_MINUTES)
                flash(f"❌ 로그인 실패 {MAX_ATTEMPTS}회로 인해 {LOCK_TIME_MINUTES}분간 잠깁니다.")
            else:
                left = MAX_ATTEMPTS - session["failed_attempts"]
                flash(f"❌ 로그인 정보가 올바르지 않습니다. 남은 시도 횟수: {left}회")

            return redirect(url_for("auth.login"))

        # 로그인 성공 전 is_active 체크 (관리자 승인 여부)
        if not user.is_active:
            flash("관리자의 승인 대기 중입니다. 승인이 완료되면 로그인할 수 있습니다.")
            return redirect(url_for("auth.login"))

        # 로그인 성공 시 초기화
        session.clear()
        session["user_id"] = user.id
        session["username"] = user.username
        session["is_admin"] = user.is_admin
        flash("✅ 로그인 성공!")

        # 'next' 파라미터가 있으면 그 페이지로 리다이렉트 (유효한 URL인지 확인)
        next_page = request.form.get('next')
        if next_page and urlparse(next_page).netloc == '':  # 외부 링크 방지
            next_page = next_page
        else:
            next_page = url_for('home')
        
        return redirect(next_page)

    return render_template("login.html")

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        if password != confirm:
            flash("비밀번호가 일치하지 않습니다.")
            return redirect(url_for("auth.signup"))

        if User.query.filter_by(username=username).first():
            flash("이미 존재하는 사용자입니다.")
            return redirect(url_for("auth.signup"))

        # 비밀번호 최소 길이 체크 (예: 8자 이상)
        if len(password) < 8:
            flash("비밀번호는 최소 8자 이상이어야 합니다.")
            return redirect(url_for("auth.signup"))

        hashed = generate_password_hash(password)
        # is_active=False로 관리자가 승인할 때까지 대기 상태
        user = User(username=username, password_hash=hashed, is_admin=False, is_active=False)
        db.session.add(user)
        db.session.commit()
        flash("회원가입 성공! 관리자의 승인을 기다려주세요.")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("로그아웃 되었습니다.")
    return redirect(url_for("home"))
