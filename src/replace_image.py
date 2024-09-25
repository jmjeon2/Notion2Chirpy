import os
import re

import requests
import base64

from src.loggers import get_logger
from src.utils import decode_url

IMGUR_API_URL = 'https://api.imgur.com/3/image'

logger = get_logger(logger_name='notion2md')


def upload_image(image_path: str, client_id: str):
    # Imgur API 클라이언트 ID
    # 이미지를 base64 형식으로 인코딩
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read())
    # Imgur API에 이미지 업로드 요청
    response = requests.post(
        IMGUR_API_URL,
        headers={'Authorization': f'Client-ID {client_id}'},
        data={'image': image_data}
    )
    # 응답에서 이미지 URL 추출
    image_url = response.json()['data']['link']
    print(f'Uploaded image URL: {image_url}')
    return image_url


def replace_image_urls(markdown_text: str, data_dir: str, imgur_client_id: str):
    # 정규식을 사용하여 ![title](url) 형태의 값을 찾음
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'

    # URL을 새로운 값으로 바꾸는 함수
    def replace_url(match):
        title = match.group(1)  # title 부분
        old_url = match.group(2)  # 기존 url 부분
        old_url = decode_url(old_url)

        # get img path
        img_path = os.path.join(data_dir, old_url)
        if not os.path.exists(img_path):
            print(f'Image not found: {img_path}')
            raise FileNotFoundError(f'Image not found: {img_path}')

        # 이미지가 인터넷 URL이 아닌 경우에만 업로드
        if old_url.startswith('http'):
            return f'![{title}]({old_url})'
        else:
            new_url = upload_image(img_path, imgur_client_id)
            return f'![{title}]({new_url})'  # 새로운 url로 변경

    # 모든 ![title](url) 패턴에 대해 URL을 교체
    updated_markdown = re.sub(pattern, replace_url, markdown_text)
    return updated_markdown


if __name__ == '__main__':
    # 예시 사용
    markdown_text = """
    content...

    ![스크린샷 2022-10-04 오후 8.19.50.png](./images/test.png)

    content...
    """

    from src.utils import read_yaml

    config = read_yaml('../../config.yaml')

    updated_text = replace_image_urls(markdown_text, config.IMGUR.CLINET_ID)

    print(updated_text)
