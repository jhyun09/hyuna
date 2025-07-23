# 습작게시판 상세페이지 이미지 링크 한방에 수정

import re
from models import db, Post
from app import app

with app.app_context():
    posts = Post.query.all()
    updated = 0

    for post in posts:
        original = post.content

       # src="/static/restore_images1/..." → src="/static/restore_images/..."
        new_content = re.sub(
    r'(src=(&quot;|\"))D:/myboard/parsing/static/restore_images/([^"&]+)',
    r'\1/static/restore_images/\3',
    original

    )


        if new_content != original:
            post.content = new_content
            updated += 1

    db.session.commit()
    print(f"✅ 경로 수정 완료! 변경된 게시글 수: {updated}")