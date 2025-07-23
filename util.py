import re
from models import db, Post
from app import app

with app.app_context():
    posts = Post.query.all()
    updated = 0

    for post in posts:
        original = post.content

        # src="..." 또는 src=&quot;... 형태 모두 처리
        new_content = re.sub(
            r'src=(["\']|&quot;)/static/uploads/unknown/([^"\']+)',
            r'src="/static/restore_images/\2"',
            original
        )

        if new_content != original:
            post.content = new_content
            updated += 1

    db.session.commit()
    print(f"✅ 이미지 경로 수정 완료! 수정된 게시글 수: {updated}")