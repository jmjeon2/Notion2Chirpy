import os

from easydict import EasyDict

from src.models import PageInfo
from src.notion_sdk.notion_api import NotionAPI
from src.notion_sdk.notion_exporter import NotionBackUpClient
from src.utils import read_yaml, unzip_all, find_md_file, expanduser

from src.loggers import get_logger

logger = get_logger(logger_name='notion2md')


def get_posting_pages(config: EasyDict) -> [PageInfo]:
    # notion client
    notion = NotionAPI(api_key=config.NOTION.API_KEY)

    # get pages
    pages = notion.get_pages(database_id=config.NOTION.DATABASE_ID,
                             filters={
                                 "property": config.NOTION.COLUMN.STATUS.NAME,
                                 "select": {
                                     "equals": config.NOTION.COLUMN.STATUS.POSTING
                                 }
                             },
                             page_size=config.NOTION.MAX_PAGE_SIZE)

    main_column = config.NOTION.COLUMN.MAIN.NAME
    uid_column = config.NOTION.COLUMN.UID.NAME

    pages = [
        PageInfo(name=page['properties'][main_column]['title'][0]['plain_text'],
                 id=page['id'],
                 uid=page['properties'][uid_column]['unique_id']['number'])
        for page in pages['results']
    ]

    logger.info("Pages to export:")
    for i, page in enumerate(pages, start=1):
        logger.info(f'\t[{i:02}] Page Name: {page.name}, Page ID: {page.id}')

    return pages


def export_notion_data(config: EasyDict, page: PageInfo) -> str:
    # get notion exporter client
    notion_exporter = NotionBackUpClient(config.NOTION.TOKEN_V2,
                                         download_path=config.NOTION.DOWNLOAD_PATH)

    # check if there are files in download path
    exist_file_list = os.listdir(expanduser(config.NOTION.DOWNLOAD_PATH))
    if '.DS_Store' in exist_file_list:
        exist_file_list.remove('.DS_Store')
    if len(exist_file_list) > 0:
        logger.warning(f'Files already exist in {config.NOTION.DOWNLOAD_PATH}. Please remove them before exporting')
        raise ValueError(f'Files already exist in {config.NOTION.DOWNLOAD_PATH}. Please remove them before exporting')

    # export notion data
    notion_exporter.export(page_id=page.id, exportType='markdown')

    # unzip exported data and remove
    unzip_all(config.NOTION.DOWNLOAD_PATH, remove_zip=True)
    md_file_path = find_md_file(config.NOTION.DOWNLOAD_PATH, extension='md')

    logger.info(f'Exported {page.name} markdown file: {md_file_path}')
    return md_file_path


if __name__ == '__main__':
    # get config
    config = read_yaml('./config.yaml')

    export_notion_data(config)
