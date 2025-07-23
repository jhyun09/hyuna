# 자유게시판 이미지 안보여서 치환

import os
import re
from urllib.parse import urlparse
from models import db, Post
from app import app

with app.app_context():
    posts = Post.query.all()
    updated = 0

    for post in posts:
        orig = post.content

        # 이미지 src="..." 전부 찾아서 치환 준비
        def replace_src(match):
            src = match.group(1)
            fname = os.path.basename(urlparse(src).path)
            ext = os.path.splitext(fname)[1].lower()

            if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                # 업로드 경로 결정
                category = post.category.strip()
                if category == "자유게시판":
                    new_path = f"/static/uploads/freeboard/{fname}"
                elif category == "이야기게시판":
                    new_path = f"/static/uploads/storyboard/{fname}"
                else:
                    new_path = f"/static/uploads/unknown/{fname}"
                return f'src="{new_path}"'
            else:
                return match.group(0)

        new_content = re.sub(r'src=["\']([^"\'>]+)', replace_src, orig)

        if new_content != orig:
            post.content = new_content
            updated += 1

    db.session.commit()
    print(f"\n✅ 게시글 내용 이미지 경로 업데이트 완료! 수정된 게시글 수: {updated}")