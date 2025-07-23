# 파씽 자유게시판, 이야기게시판용


import xml.etree.ElementTree as ET
import base64
import os

from flask import Flask
from datetime import datetime
from models import db, Post, Comment
from html import unescape
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///board.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


def b64(text):
    try:
        return base64.b64decode(text).decode("utf-8")
    except:
        return ""


def decode_content_with_images(encoded_html):
    decoded = b64(encoded_html)
    decoded = unescape(decoded)
    soup = BeautifulSoup(decoded, "html.parser")
    return str(soup)


def parse_board_xml(file_path, category):
    tree = ET.parse(file_path)
    root = tree.getroot()

    for item in root.findall(".//post"):
        title = b64(item.findtext("title", ""))
        author = b64(item.findtext("nick_name", "")) or b64(item.findtext("user_id", ""))
        date_str = b64(item.findtext("regdate", ""))
        read_count = int(b64(item.findtext("readed_count", "0")) or 0)

        try:
            date = datetime.strptime(date_str, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M")
        except:
            date = date_str

        encoded_content = item.findtext("content", "")
        content = decode_content_with_images(encoded_content)

        post = Post(
            title=title.strip(),
            author=author.strip(),
            content=content.strip(),
            date=date.strip(),
            read_count=read_count,
            category=category
        )
        db.session.add(post)
        db.session.flush()

        comment_list = item.find("comments")
        if comment_list is not None:
            for c in comment_list.findall("comment"):
                try:
                    c_author = b64(c.findtext("nick_name", "")) or b64(c.findtext("user_id", ""))
                    c_content = b64(c.findtext("content", ""))
                    c_date_str = b64(c.findtext("regdate", ""))
                    try:
                        c_date = datetime.strptime(c_date_str, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M")
                    except:
                        c_date = c_date_str
                    comment = Comment(
                        author=c_author.strip(),
                        content=c_content.strip(),
                        created_at=c_date.strip(),
                        post_id=post.id
                    )
                    db.session.add(comment)
                except Exception as e:
                    print("⚠️ 댓글 처리 중 오류:", e)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # parse_board_xml("module_freeboard.000001.xml", "자유게시판")
        # parse_board_xml("module_story1.000001.xml", "이야기게시판")
        # parse_board_xml("module_galleryboard.000001.xml", "사진게시판")  ← 추가하고 싶으면 이 줄도 활성화!
        
        db.session.commit()
        print("🎉 모든 게시판 파싱 + 저장 완료!")
