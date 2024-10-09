from datetime import datetime
from pathlib import Path
from easydict import EasyDict
import traceback
from src.loggers import get_logger

# set loggers (it should be set before importing other modules using logger)
today = datetime.today().strftime('%Y-%m-%d')
logger = get_logger(log_file=f'{today}.log', logger_name='notion2md')

from src.upload_github import upload_or_update_file_to_github
from src.models import PageInfo
from src.notion_sdk.notion_download import export_notion_data, get_posting_pages
from src.notion_sdk.update_notion_db import update_notion_db
from src.replace_image import replace_image_urls_v2
from src.transform_markdown import processing_markdown
from src.utils import delete_file, get_config


def save_md_file(save_fp, content):
    with open(save_fp, 'w') as f:
        f.write(content)


def process(page: PageInfo) -> bool:
    # export notion data
    md_path = export_notion_data(config.NOTION.TOKEN_V2,
                                 config.NOTION.DOWNLOAD_DIR,
                                 page)
    logger.info(f'Exported notion data in {md_path}. page name: {page.name}')

    try:
        # transform markdown to chirpy format
        md = processing_markdown(md_path)
        logger.info(f'Transform markdown file in {md.filename}, page name: {page.name}')

        # transform image url
        md_parent_path = Path(md_path).parent
        content = replace_image_urls_v2(md.content, md_parent_path, config.IMGUR.CLIENT_ID)
        logger.info(f'Image Processed(IMGUR). page name: {page.name}')

        # save md file
        save_fp = Path(config.NOTION.POST_SAVE_DIR) / md.filename
        save_md_file(save_fp, content)
        logger.info(f'Saved markdown file in {save_fp}. page name: {page.name}')

        # auto commit & push
        if config.GITHUB.AUTO_COMMIT:
            upload_or_update_file_to_github(config.GITHUB.USERNAME,
                                            config.GITHUB.REPO_NAME,
                                            config.GITHUB.BRANCH,
                                            config.GITHUB.TOKEN,
                                            save_fp)
            logger.info(f'Auto commit & push done. page name: {page.name}')

        # move to local repo _post directory
        else:
            if config.GITHUB.LOCAL_REPO_POST_DIR is None:
                logger.warning('Local repo post directory not set. Check the config.yaml file')
                logger.warning(f'Check the directories that files are saved {config.NOTION.POST_SAVE_DIR}')
                logger.warning(f'Commit and Push the markdown files to your github repository manually')
                return True

            new_save_dir = Path(config.GITHUB.LOCAL_REPO_POST_DIR)
            if new_save_dir.exists():
                new_save_path = new_save_dir / md.filename
                save_fp.rename(new_save_path)
                logger.info(f'Moved markdown file from {save_fp} to {new_save_path}. page name: {page.name}')
            else:
                logger.error(f'Local repo post directory not exists. Local repo post directory: {new_save_dir}')
                logger.error(f'Check the directories that files are saved {config.NOTION.POST_SAVE_DIR}')
                return False

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
        logger.info(f'Total failed pages: {len(failed_pages)}')
        for i, page in enumerate(failed_pages, start=1):
            logger.info(f'[{i}] Failed page: {page}')


if __name__ == '__main__':
    config = get_config()
    main(config)
