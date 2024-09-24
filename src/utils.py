import os
import zipfile
from glob import glob

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


def get_dir(path):
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
    pages_zip = glob(get_dir(os.path.join(directory, 'Export*.zip')))
    print(pages_zip)

    dst_folders = []
    for zip_fp in pages_zip:
        zip = zipfile.ZipFile(zip_fp)
        # 압축할 폴더 생성
        zip_folder = get_dir(zip_fp.replace('.zip', ''))
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


def find_all_files(directory: str, extension: str) -> list[str]:
    """
    directory 내의 모든 extension 확장자를 가진 파일 경로 반환
    Args:
        directory (str): 검색할 디렉토리
        extension (str): 검색할 확장자 (ex. 'md', 'html')
    """

    # 단일 html 파일
    pages_single = glob(get_dir(os.path.join(directory, f'*.{extension}')))
    # 이미지를 포함하여 폴더 형태의 html 파일
    pages_including_image = glob(get_dir(os.path.join(directory, f'Export*', f'*.{extension}')))

    pages = pages_single + pages_including_image

    # 파일은 한개여야함
    if len(pages) == 0:
        raise ValueError(f'[Error] 다운로드가 실패하였습니다. 경로를 다시 확인해주세요. Download Folder:[{directory}]')

    return pages
