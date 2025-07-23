from app import app, db
from models import User

with app.app_context():
    admin = User(username='jhyun', is_admin=True)
    admin.set_password('123456789')
    db.session.add(admin)
    db.session.commit()

    print("관리자 계정 생성 완료")
