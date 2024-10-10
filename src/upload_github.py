import os
import requests
import base64

from pathlib import Path
from typing import Union, Optional

from src.loggers import get_logger
from src.utils import get_config

logger = get_logger(logger_name='notion2md')


def upload_or_update_file_to_github(username: str,
                                    repo_name: str,
                                    branch_name: str,
                                    token: str,
                                    file_path: Union[str, Path],
                                    commit_message: Optional[str] = None):
    # github 내의 파일 경로 지정
    md_base_path = os.path.basename(file_path)
    github_file_path = os.path.join('_posts', md_base_path)  # GitHub 저장소 내 업로드할 파일 경로

    # parse uid from file_path (YYYY-MM-DD-UID.md)
    uid = md_base_path.replace('.md', '').split('-')[-1]

    # GitHub API 엔드포인트
    url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{github_file_path}"

    # API 요청에 사용할 헤더
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 파일의 존재 여부를 확인하기 위한 GET 요청
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # 파일이 이미 존재하는 경우 SHA 값을 가져온다
        file_sha = response.json()['sha']
        logger.info(f"[github api] 기존 파일이 존재합니다. {github_file_path} 파일을 업데이트합니다.")
    elif response.status_code == 404:
        # 파일이 존재하지 않으면 새로운 파일을 업로드
        file_sha = None
        logger.info(f"[github api] 새 파일을 업로드합니다: {github_file_path}")
    else:
        # 다른 오류가 발생하면 출력하고 종료
        logger.error(f"[github api] 오류가 발생했습니다: {response.json()}")
        return

    # 로컬 파일을 읽어서 base64로 인코딩
    if not os.path.exists(file_path):
        logger.error(f"[github api] 로컬 파일을 찾을 수 없습니다: {file_path}")
        return

    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    # 업로드 또는 수정할 데이터 설정
    data = {
        "message": f"{'update' if file_sha else 'add'} post: {uid}" if commit_message is None else commit_message,
        "content": content,
        "branch": branch_name
    }

    # 파일 수정인 경우에는 SHA 값을 포함해야 함
    if file_sha:
        data['sha'] = file_sha

    # PUT 요청을 통해 파일을 업로드 또는 수정
    response = requests.put(url, json=data, headers=headers)

    # 결과 출력
    if response.status_code in [200, 201]:
        logger.info(f"[github api] 파일 업로드 성공: {response.json()['content']['html_url']}")
    else:
        logger.info(f"[github api] 파일 업로드 실패: {response.json()}")


if __name__ == '__main__':
    config = get_config()

    file_path = '../test/samples/2024-09-26-234.md'  # 업로드할 로컬 파일 경로

    upload_or_update_file_to_github(
        config.GITHUB.USERNAME,
        config.GITHUB.REPO_NAME,
        config.GITHUB.BRANCH,
        config.GITHUB.TOKEN,
        file_path,
        commit_message="test: upload file via api"
    )
