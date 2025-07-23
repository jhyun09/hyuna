# 제로보드 xe 게시판 .xml 백업파일 사진 파싱 파일 후 이미지 새로 복사
# 사진게시판에 사진이 안보일때...


import os
import shutil

# 📂 이미지가 흩어져 있는 루트 경로
SOURCE_ROOT = r'D:\myboard\parsing\bbs'

# 📁 복사 대상 폴더 (Flask static 내부)
TARGET_FOLDER = os.path.join(os.getcwd(), 'static', 'restore_images1')
os.makedirs(TARGET_FOLDER, exist_ok=True)

# ✅ 복사 대상 확장자들
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

copied = 0
skipped = 0

for dirpath, dirnames, filenames in os.walk(SOURCE_ROOT):
    for filename in filenames:
        ext = os.path.splitext(filename)[1].lower()
        if ext in IMAGE_EXTENSIONS:
            src_path = os.path.join(dirpath, filename)
            dst_path = os.path.join(TARGET_FOLDER, filename)

            if not os.path.exists(dst_path):
                shutil.copy2(src_path, dst_path)
                copied += 1
            else:
                skipped += 1

print(f"✅ 이미지 복사 완료!")
print(f"📥 새로 복사된 이미지: {copied}개")
print(f"⏩ 이미 존재해서 건너뜀: {skipped}개")
print(f"📁 대상 폴더: {TARGET_FOLDER}")