import os

from easydict import EasyDict

from src.notion_sdk.notion_api import NotionAPI
from src.notion_sdk.notion_exporter import NotionBackUpClient
from src.utils import read_yaml, unzip_all, find_all_files, get_dir

from src.loggers import get_logger

logger = get_logger(logger_name='notion2md')


def export_notion_data(config: EasyDict) -> list:
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
                             page_size=3)  # TODO: page_size를 3으로 설정하여 테스트 중입니다. 실제 사용시에는 적절한 값을 설정할 것

    # TODO pages의 컬럼을 확인하여 필수 컬럼이 있는지 확인하고 없으면 에러를 발생시키도록 구현
    # TODO 필수 컬럼: name, title, date, categories
    # TODO 완료된 페이지는 삭제 처리

    main_column = config.NOTION.COLUMN.MAIN.NAME
    status_column = config.NOTION.COLUMN.STATUS.NAME
    status_target_value = config.NOTION.COLUMN.STATUS.POSTING

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

    # check if there are files in download path
    exist_file_list = os.listdir(get_dir(config.NOTION.DOWNLOAD_PATH))
    if '.DS_Store' in exist_file_list:
        exist_file_list.remove('.DS_Store')
    if len(exist_file_list) > 0:
        raise ValueError(f'Files already exist in {config.NOTION.DOWNLOAD_PATH}. Please remove them before exporting')

    # export notion data
    for page_id in id_pages:
        notion_exporter.export(page_id=page_id, exportType='markdown')

    # unzip exported data
    unzip_all(config.NOTION.DOWNLOAD_PATH, remove_zip=True)
    md_files = find_all_files(config.NOTION.DOWNLOAD_PATH, extension='md')

    logger.info(f'Exported {len(md_files)} markdown files')
    return md_files


if __name__ == '__main__':
    # get config
    config = read_yaml('./config.yaml')

    export_notion_data(config)
