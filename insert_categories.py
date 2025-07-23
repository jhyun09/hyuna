from models import db, Category

default_categories = ['자유게시판', '사진게시판', '이야기게시판', '습작게시판', '쭈야랑게시판']

def insert_default_categories():
    for cat_name in default_categories:
        existing = Category.query.filter_by(name=cat_name).first()
        if not existing:
            new_cat = Category(name=cat_name)
            db.session.add(new_cat)
    db.session.commit()
    print("기본 게시판명 DB 입력 완료!")

if __name__ == "__main__":
    from app import app  # 여기서 app.py의 app 객체 import
    with app.app_context():
        insert_default_categories()
