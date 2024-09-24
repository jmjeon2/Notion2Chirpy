from notion.client import NotionClient
import requests
from tqdm import tqdm
from time import sleep
from pathlib import Path
import os

from src.utils import read_yaml

NOTION_API_ROOT = "https://www.notion.so/api/v3"
BLOCK_SIZE = 1024  # download 1KB


class NotionBackUpClient:
    def __init__(self, token, download_path='~/.notion2md'):
        self.token = token
        self.space_id = NotionClient(token).current_space.id
        self.download_path = Path(download_path)

        # get filetoken
        try:
            self.file_token = NotionClient(token).session.cookies.get('file_token')
        except Exception as e:
            print(e)
            raise ValueError('[Error] file token값이 올바르지 않습니다. 다시 확인 해 주세요. [{}]'.format(token))

        # 다운로드 폴더 생성
        os.makedirs(os.path.expanduser(download_path), exist_ok=True)

    def _send_post_request(self, path, body):
        response = requests.request(
            "POST",
            f"{NOTION_API_ROOT}/{path}",
            json=body,
            cookies={"token_v2": self.token},
        )
        response.raise_for_status()
        return response.json()

    def launch_export_task(self, page_id, exportType):
        return self._send_post_request(
            "enqueueTask",
            {
                "task": {
                    "eventName": "exportBlock",
                    "request": {
                        "block": {
                            "id": page_id,
                            "spaceId": self.space_id,
                        },
                        "exportOptions": {
                            "exportType": exportType,
                            "timeZone": "Asia/Seoul",
                            "locale": "en",
                        },
                        "recursive": False
                    },
                }
            },
        )["taskId"]

    def get_user_task_status(self, task_id):
        task_statuses = self._send_post_request("getTasks", {"taskIds": [task_id]})[
            "results"
        ]

        return list(
            filter(lambda task_status: task_status["id"] == task_id, task_statuses)
        )[0]

    def download_file(self, url, export_file):
        cookies = {'file_token': self.file_token}
        with requests.get(url, stream=True, allow_redirects=True, cookies=cookies) as response:
            total_size = int(response.headers.get("content-length", 0))
            tqdm_bar = tqdm(total=total_size, unit="iB", unit_scale=True)
            with export_file.open("wb") as export_file_handle:
                for data in response.iter_content(BLOCK_SIZE):
                    tqdm_bar.update(len(data))
                    export_file_handle.write(data)
            tqdm_bar.close()

    def export(self, page_id, exportType):

        task_id = self.launch_export_task(page_id=page_id, exportType=exportType)

        for i in range(5):
            task_status = self.get_user_task_status(task_id)

            if task_status["state"] == "success":
                break

            print('Export still in progress...')
            sleep(5)
        else:
            print('Export Error.')
            return

        # download file
        export_link = task_status["status"]["exportURL"]
        save_fp = self.download_path.expanduser() / f'Export-{page_id}.zip'
        self.download_file(export_link, save_fp)
        print(f'[SUCCESS] Notion Page Export Complete in {save_fp}')


if __name__ == '__main__':
    config = read_yaml('../../config.yaml')

    # export & download
    ne = NotionBackUpClient(token=config.NOTION_API_TOKEN_V2, download_path='~/.n2t')
    page_id = " <page id> "
    exportType = 'markdown'
    ne.export(page_id=page_id, exportType=exportType)
