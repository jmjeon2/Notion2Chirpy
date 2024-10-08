import os
import urllib.parse
import zipfile
from glob import glob
from shutil import rmtree

import yaml
from easydict import EasyDict


def read_yaml(file_path) -> EasyDict:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        data = EasyDict(data)
    except Exception as e:
        print(e)
        raise ValueError(f'[Error] yaml 파일을 읽는데 실패했습니다. {file_path}')

    return data


def get_config():
    """
    config 파일을 읽어서 반환 (private config 파일이 있는 경우 private config 파일을 우선적으로 읽음)
    """

    private_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config_private.yaml')
    public_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')

    if os.path.exists(private_config_path):
        config = read_yaml(private_config_path)
    else:
        config = read_yaml(public_config_path)

    return config


def expanduser(path):
    """경로에 ~가 붙으면 expanduser 처리"""
    if path.startswith('~'):
        return os.path.expanduser(path)
    else:
        return path


def unzip_all(directory: str, remove_zip=False):
    """
    download_dir 폴더 내에 있는 모든 zip 파일 중 Export로 시작하는 파일들을 압축 해제
    Args:
        directory (str): 압축 해제할 디렉토리
        remove_zip (bool): 압축 해제 후 zip 파일 삭제 여부
    """

    # zip 파일로 다운로드 한 경우 압축해제
    pages_zip = glob(expanduser(os.path.join(directory, 'Export*.zip')))

    dst_folders = []
    for zip_fp in pages_zip:
        zip = zipfile.ZipFile(zip_fp)
        # 압축할 폴더 생성
        zip_folder = expanduser(zip_fp.replace('.zip', ''))
        os.makedirs(zip_folder, exist_ok=True)
        # 압축 풀기
        zip.extractall(zip_folder)
        zip.close()

        # 압축 해제된 폴더 경로 저장
        dst_folders.append(zip_folder)

        # zip 파일 제거
        if remove_zip:
            os.remove(zip_fp)

    return dst_folders


def find_md_file(directory: str, extension: str) -> str:
    """
    directory 내의 모든 extension 확장자를 가진 파일 경로 반환 (md 파일이 여러개인 경우 에러 발생)
    Args:
        directory (str): 검색할 디렉토리
        extension (str): 검색할 확장자 (ex. 'md', 'html')
    """

    # 단일 html 파일
    pages_single = glob(expanduser(os.path.join(directory, f'*.{extension}')))
    # 이미지를 포함하여 폴더 형태의 html 파일
    pages_including_image = glob(expanduser(os.path.join(directory, f'Export*', f'*.{extension}')))

    pages = pages_single + pages_including_image

    # 파일은 한개여야함
    if len(pages) == 0:
        raise ValueError(f'[Error] 다운로드가 실패하였습니다. 경로를 다시 확인해주세요. Download Folder:[{directory}]')
    elif len(pages) > 1:
        raise ValueError(f'[Error] 다운로드된 파일이 여러개입니다. 경로를 다시 확인해주세요. Download Folder:[{directory}]')

    return pages[0]


def delete_file(filepath):
    if not os.path.exists(filepath):
        raise ValueError(f'[Error] 삭제할 파일이 존재하지 않습니다. [{filepath}]')

    # Export~/~.html 이미지를 포함한 폴더인 경우
    if 'Export' in filepath:
        dir_path = os.path.dirname(filepath)
        rmtree(dir_path)
    # ~.html 단일 파일인 경우
    else:
        os.remove(filepath)


def encode_url(url):
    return urllib.parse.quote(url)


def decode_url(encoded_url):
    return urllib.parse.unquote(encoded_url)
