import os
from PIL import Image
import re
import time

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
    logger.debug(f'Imgur API response: {response.json()}')
    # 응답에서 이미지 URL 추출
    image_url = response.json()['data']['link']
    logger.info(f'Uploaded image URL: {image_url}')
    return image_url


def replace_image_urls(markdown_text: str, data_dir: str, imgur_client_id: str):
    """
    deprecated: use replace_image_urls_v2
    url 내에 ()가 포함되어 있을 경우, url이 잘못 인식되는 문제가 있음
    """
    # 정규식을 사용하여 ![title](url) 형태의 값을 찾음
    pattern = r'!\[([^\]]+)\]\(([^)]+)\)'

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


def replace_image_urls_v2(markdown_text: str, data_dir: str, imgur_client_id: str):
    content = markdown_text.split('\n')

    output_content = []
    for i, line in enumerate(content):
        if line.strip().startswith('!['):
            # get image path from line (starts with "](" and ends with ".jpg)" or ".png)")
            start_idx = line.find('](') + 2
            img_rel_path_md = line[start_idx:-1]  # remove ')', url encoded markdown text
            img_rel_path = decode_url(img_rel_path_md)  # decoded path

            # replace image url using imgur
            img_path = os.path.join(data_dir, img_rel_path)
            img_path = _validate_image_format(img_path)
            new_url = upload_image(img_path, imgur_client_id)
            line = line.replace(img_rel_path_md, new_url)

            # sleep for 0.5 sec to avoid rate limit
            time.sleep(0.5)

        output_content.append(line)

    return '\n'.join(output_content)


def _validate_image_format(image_path: str) -> str:
    # 이미지 포맷 확인
    img = Image.open(image_path)
    fmt = img.format

    # WEBP 포맷인 경우 png로 변환
    if fmt == 'WEBP':
        # save to png format
        image_path = os.path.extsep.join(image_path.split(os.path.extsep)[:-1]) + '.png'
        img.save(image_path, 'PNG')

    # 아래 포맷이 아닌 경우 에러 발생
    elif fmt not in ['JPEG', 'PNG', 'GIF', 'JPG']:
        logger.error(f'Invalid image format: {fmt}')
        raise ValueError(f'Invalid image format: {fmt}')

    return image_path


if __name__ == '__main__':
    # 예시 사용
    markdown_text = """
    content...


    ![스크린샷 2022-10-04 오후 8.19.50.png](./images/sample(test).png)

    content...
    """

    from src.utils import read_yaml

    config = read_yaml('../config.yaml')

    # updated_text = replace_image_urls_v2(markdown_text, './', config.IMGUR.CLIENT_ID)

    # print(updated_text)

    path = '/Users/jmjeon/.notion2md/Export-10a48a6e-55fc-804a-894c-e097d6b7c445/테스트 페이지 (Github Pages Chirpy) 10a48a6e55fc804a894ce097d6b7c445/luigi.jpg'
    # upload_image(path, config.IMGUR.CLIENT_ID)
    print(_validate_image_format(path))
