from easydict import EasyDict

from src.models import PageInfo
from src.notion_sdk.notion_api import NotionAPI
from src.utils import read_yaml


def update_notion_db(config: EasyDict, page: PageInfo):
    client = NotionAPI(api_key=config.NOTION.API_KEY)  # notion api 사이트에서 발급받기

    # update url column
    col_url = config.NOTION.COLUMN.URL.NAME
    gh_url = config.GITHUB_PAGES.URL
    client.update(page_id=page.id, properties={col_url: {"url": f"{gh_url}/posts/{page.uid}"}})

    # update status column
    col_status = config.NOTION.COLUMN.STATUS.NAME
    val_posted = config.NOTION.COLUMN.STATUS.POSTED
    client.update(page_id=page.id, properties={col_status: {"select": {"name": val_posted}}})


if __name__ == '__main__':
    config = read_yaml('../../config.yaml')
    update_notion_db(config, PageInfo(name='test', id='test'))
