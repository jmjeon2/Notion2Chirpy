from pathlib import Path
from easydict import EasyDict
import traceback

from src.loggers import get_logger
from src.models import PageInfo
from src.notion_sdk.notion_download import export_notion_data, get_posting_pages
from src.notion_sdk.update_notion_db import update_notion_db
from src.replace_image import replace_image_urls_v2
from src.transform_markdown import processing_markdown
from src.utils import read_yaml, delete_file

logger = get_logger(logger_name='notion2md')


def save_md_file(save_fp, content):
    with open(save_fp, 'w') as f:
        f.write(content)


def process(page: PageInfo) -> bool:
    # export notion data
    md_path = export_notion_data(config, page)
    logger.info(f'Exported notion data in {md_path}. page name: {page.name}')

    try:
        # transform markdown to chirpy format
        md = processing_markdown(md_path)
        logger.info(f'Transform markdown file in {md.filepath}, page name: {page.name}')

        # transform image url
        md_parent_path = Path(md_path).parent
        content = replace_image_urls_v2(md.content, md_parent_path, config.IMGUR.CLIENT_ID)
        logger.info(f'Image Processed(IMGUR). page name: {page.name}')

        # save md file
        save_fp = Path(config.GITHUB_PAGES.POST_PATH) / md.filepath
        save_md_file(save_fp, content)
        logger.info(f'Saved markdown file in {save_fp}. page name: {page.name}')
        return True

    except Exception as e:
        logger.error(f'Error occurred in {page.name}')
        logger.error(e)
        logger.error(traceback.format_exc())
        return False

    finally:
        # delete exported md file
        delete_file(md_path)
        logger.info(f'Deleted exported markdown file in {md_path}')


def main(config: EasyDict):
    # get posting pages
    pages = get_posting_pages(config)

    failed_pages = []

    # export notion data (markdown)
    for i, page in enumerate(pages, start=1):
        logger.info(f'Start [{i}]th Processing {page.name}')
        try:
            succeed = process(page)

            # update notion db
            if succeed:
                update_notion_db(config, page)
                logger.info(f'Updated notion db. page name: {page.name}')
            else:
                failed_pages.append(page.name)

        except Exception as e:
            logger.error(f'Error occurred in {page.name}')
            logger.error(e)
            logger.error(traceback.format_exc())
            failed_pages.append(page.name)
            continue

        logger.info(f'Processed {page.name}')

    logger.info('All process done!')

    if failed_pages:
        logger.error(f'Total failed pages: {len(failed_pages)}')
        for i, page in enumerate(failed_pages, start=1):
            logger.error(f'[{i}] Failed page: {page}')


if __name__ == '__main__':
    config = read_yaml('./config.yaml')
    main(config)
