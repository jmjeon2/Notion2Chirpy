import os
from pathlib import Path
from PIL import Image
import time
import requests
import base64

from src.loggers import get_logger
from src.utils import decode_url

IMGUR_API_URL = 'https://api.imgur.com/3/image'
VALID_IMAGE_FORMATS = {'JPEG', 'PNG', 'GIF', 'JPG'}
UPLOAD_DELAY = 0.5

logger = get_logger(logger_name='notion2md')


def upload_image(image_path: str, client_id: str) -> str:
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read())

    response = requests.post(
        IMGUR_API_URL,
        headers={'Authorization': f'Client-ID {client_id}'},
        data={'image': image_data}
    )
    response.raise_for_status()

    image_url = response.json()['data']['link']
    logger.info(f'Uploaded image URL: {image_url}')
    return image_url


def validate_image_format(image_path: str) -> str:
    img = Image.open(image_path)
    fmt = img.format

    if fmt == 'WEBP':
        new_path = Path(image_path).with_suffix('.png')
        img.save(new_path, 'PNG')
        return str(new_path)
    elif fmt not in VALID_IMAGE_FORMATS:
        raise ValueError(f'Invalid image format: {fmt}')

    return image_path


def process_image_line(line: str, data_dir: str, imgur_client_id: str) -> str:
    start_idx = line.find('](') + 2
    img_rel_path_md = line[start_idx:-1]
    img_rel_path = decode_url(img_rel_path_md)

    if img_rel_path.startswith('http'):
        return line

    img_path = os.path.join(data_dir, img_rel_path)
    img_path = validate_image_format(img_path)
    new_url = upload_image(img_path, imgur_client_id)
    return line.replace(img_rel_path_md, new_url)


def replace_image_urls_v2(markdown_text: str, data_dir: str, imgur_client_id: str) -> str:
    if '![' not in markdown_text:
        return markdown_text

    output_lines = []
    for line in markdown_text.split('\n'):
        if line.strip().startswith('!['):
            line = process_image_line(line, data_dir, imgur_client_id)
            time.sleep(UPLOAD_DELAY)
        output_lines.append(line)

    return '\n'.join(output_lines)
