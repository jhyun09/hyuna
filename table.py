# create_tables.py
from app import app
from models import db

with app.app_context():
    db.create_all()
    print("✅ 모든 테이블 생성 완료!")
