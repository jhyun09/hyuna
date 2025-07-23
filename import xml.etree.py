import xml.etree.ElementTree as ET  # XML 파싱을 위한 표준 라이브러리

def parse_zeroboard_xml(file_path):
    """
    제로보드 백업 XML 파일을 파싱하여 게시글 정보를 추출하는 함수

    Parameters:
        file_path (str): 예) "module_freeboard.000001.xml"

    Returns:
        list: 게시글 정보를 담은 딕셔너리 리스트
    """
    # XML 파일 읽고 파싱
    tree = ET.parse(file_path)
    root = tree.getroot()

    posts = []  # 게시글 리스트 초기화

    # XML 내 모든 'item' 요소를 순회
    for item in root.findall(".//item"):
        # 각 항목에서 필요한 필드 추출 (존재하지 않으면 기본값 "")
        title = item.findtext("title", default="").strip()
        author = item.findtext("name", default="").strip()
        content = item.findtext("memo", default="").strip()
        date = item.findtext("reg_date", default="").strip()

        # 딕셔너리로 구성된 게시글 객체 생성
        post = {
            "title": title,
            "author": author,
            "content": content,
            "date": date
        }

        posts.append(post)  # 리스트에 추가

    return posts  # 모든 게시글 반환

# 이 모듈을 직접 실행할 경우 수행되는 블록
if __name__ == "__main__":
    file_name = "module_freeboard.000001.xml"  # 분석 대상 XML 파일명

    try:
        posts = parse_zeroboard_xml(file_name)
        for post in posts:
            print(f"[{post['date']}] {post['author']} - {post['title']}")
            print(post['content'])
            print("-" * 40)
    except FileNotFoundError:
        print(f"❗ 파일을 찾을 수 없습니다: {file_name}")
    except ET.ParseError as e:
        print(f"❗ XML 파싱 중 오류 발생: {e}")