from easydict import EasyDict

from src.notion_sdk.notion_api import NotionAPI
from src.notion_sdk.notion_exporter import NotionBackUpClient
from utils import read_yaml, unzip_all, find_all_files

from loggers import get_logger

logger = get_logger(log_file='notion2md.log', logger_name='notion2md')


def export_notion_data(config: EasyDict):
    # notion client
    notion = NotionAPI(api_key=config.NOTION.API_KEY)

    # get pages
    pages = notion.get_pages(database_id=config.NOTION.DATABASE_ID,
                             filters={
                                 "property": config.NOTION.STATUS_COLUMN,
                                 "select": {
                                     "equals": config.NOTION.STATUS_VALUE_FOR_POSTING
                                 }
                             },
                             page_size=10)

    main_column = config.NOTION.MAIN_COLUMN
    status_column = config.NOTION.STATUS_COLUMN
    status_target_value = config.NOTION.STATUS_VALUE_FOR_POSTING

    # get name of pages
    name_pages = [page['properties'][main_column]['title'][0]['plain_text'] for page in pages['results']]

    # get id of pages
    id_pages = [page['id'] for page in pages['results']]

    # print page ids
    logger.info("Pages to export:")
    for i, (name, page_id) in enumerate(zip(name_pages, id_pages), start=1):
        logger.info(f'\t[{i:02}] Page Name: {name}, Page ID: {page_id}')

    # set notion exporter
    notion_exporter = NotionBackUpClient(config.NOTION.TOKEN_V2,
                                         download_path=config.NOTION.DOWNLOAD_PATH)

    # export notion data
    for page_id in id_pages:
        notion_exporter.export(page_id=page_id, exportType='markdown')

    # unzip exported data
    unzip_all(config.NOTION.DOWNLOAD_PATH)
    md_files = find_all_files(config.NOTION.DOWNLOAD_PATH, extension='md')

    logger.info(f'Exported {len(md_files)} markdown files')


if __name__ == '__main__':
    # get config
    config = read_yaml('./config.yaml')

    export_notion_data(config)
