from pathlib import Path

from easydict import EasyDict

from src.loggers import get_logger
from src.models import PageInfo
from src.notion_sdk.notion_download import export_notion_data, get_posting_pages
from src.replace_image import replace_image_urls_v2
from src.transform_markdown import processing_markdown
from src.utils import read_yaml, delete_file

logger = get_logger(logger_name='notion2md')


def save_md_file(save_fp, content):
    with open(save_fp, 'w') as f:
        f.write(content)
    logger.info(f'Saved markdown file in {save_fp}')


def process(page: PageInfo):
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
        logger.info(f'IMGUR Image Processed. page name: {page.name}')

        # save md file
        save_fp = Path(config.GITHUB_PAGES.POST_PATH) / md.filepath
        save_md_file(save_fp, content)
        logger.info(f'Saved markdown file in {save_fp}. page name: {page.name}')

    except Exception as e:
        logger.error(f'Error occurred in {page.name}')
        logger.error(e)
        return

    finally:
        # delete exported md file
        delete_file(md_path)
        logger.info(f'Deleted exported markdown file in {md_path}')


def main(config: EasyDict):
    # get posting pages
    pages = get_posting_pages(config)

    # export notion data (markdown)
    for i, page in enumerate(pages):
        logger.info(f'Start {i}th Processing {page.name}')
        try:
            process(page)
        except Exception as e:
            logger.error(f'Error occurred in {page.name}')
            logger.error(e)
            continue
        logger.info(f'Processed {page.name}')

    logger.info('All process done!')


if __name__ == '__main__':
    config = read_yaml('./config.yaml')
    main(config)
