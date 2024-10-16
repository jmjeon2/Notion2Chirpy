from datetime import datetime
from pathlib import Path
from typing import List, Tuple
from easydict import EasyDict
import traceback
from src.loggers import get_logger

# set loggers (it should be set before importing other modules using logger)
today = datetime.today().strftime('%Y-%m-%d')
logger = get_logger(log_file=f'{today}.log', logger_name='notion2md')

from src.alerts.send_gmail import GmailSender
from src.alerts.send_slack import SlackBot
from src.upload_github import upload_or_update_file_to_github
from src.models import PageInfo
from src.notion_sdk.notion_download import export_notion_data, get_posting_pages
from src.notion_sdk.update_notion_db import update_notion_db
from src.replace_image import replace_image_urls_v2
from src.transform_markdown import processing_markdown
from src.utils import delete_file, get_config


def save_md_file(save_fp: Path, content: str) -> None:
    with open(save_fp, 'w') as f:
        f.write(content)

def process_page(config: EasyDict, page: PageInfo) -> bool:
    try:
        md_path = export_notion_data(config.NOTION.TOKEN_V2, config.NOTION.DOWNLOAD_DIR, page)
        logger.info(f'Exported notion data: {md_path}, page: {page.name}')

        md = processing_markdown(md_path)
        logger.info(f'Transformed markdown: {md.filename}, page: {page.name}')

        content = replace_image_urls_v2(md.content, Path(md_path).parent, config.IMGUR.CLIENT_ID)
        logger.info(f'Processed images (IMGUR), page: {page.name}')

        save_fp = Path(config.NOTION.POST_SAVE_DIR) / md.filename
        save_md_file(save_fp, content)
        logger.info(f'Saved markdown: {save_fp}, page: {page.name}')

        if config.GITHUB.AUTO_COMMIT:
            upload_or_update_file_to_github(config.GITHUB.USERNAME, config.GITHUB.REPO_NAME,
                                            config.GITHUB.BRANCH, config.GITHUB.TOKEN, save_fp)
            logger.info(f'Auto commit & push done, page: {page.name}')
        else:
            move_to_local_repo(config, save_fp, md.filename, page.name)

        return True
    except Exception as e:
        logger.error(f'Error processing {page.name}: {str(e)}')
        logger.error(traceback.format_exc())
        return False
    finally:
        delete_file(md_path)
        logger.info(f'Deleted exported markdown: {md_path}')

def move_to_local_repo(config: EasyDict, save_fp: Path, filename: str, page_name: str) -> None:
    if config.GITHUB.LOCAL_REPO_POST_DIR is None:
        logger.warning('Local repo post directory not set. Check config.yaml')
        logger.warning(f'Files saved in: {config.NOTION.POST_SAVE_DIR}')
        logger.warning('Commit and Push markdown files to GitHub manually')
        return

    new_save_dir = Path(config.GITHUB.LOCAL_REPO_POST_DIR)
    if new_save_dir.exists():
        new_save_path = new_save_dir / filename
        save_fp.rename(new_save_path)
        logger.info(f'Moved markdown: {save_fp} -> {new_save_path}, page: {page_name}')
    else:
        logger.error(f'Local repo post directory not found: {new_save_dir}')
        logger.error(f'Files saved in: {config.NOTION.POST_SAVE_DIR}')

def process_pages(config: EasyDict, pages: List[PageInfo]) -> Tuple[List[PageInfo], List[PageInfo]]:
    succeed_pages, failed_pages = [], []
    for i, page in enumerate(pages, start=1):
        logger.info(f'Processing [{i}] {page.name}')
        if process_page(config, page):
            update_notion_db(config, page)
            logger.info(f'Updated Notion DB, page: {page.name}')
            succeed_pages.append(page)
        else:
            failed_pages.append(page)
        logger.info(f'Processed {page.name}')
    return succeed_pages, failed_pages

def generate_result_message(config: EasyDict, pages: List[PageInfo], succeed_pages: List[PageInfo], failed_pages: List[PageInfo]) -> str:
    msg = f'Total pages: {len(pages)}\n'
    if succeed_pages:
        msg += f'Succeed pages: {len(succeed_pages)}\n'
        for i, page in enumerate(succeed_pages, start=1):
            url = f'https://{config.GITHUB.REPO_NAME}/posts/{page.uid}/'
            msg += f'\t[{i}] {page.name}: {url}\n'
    if failed_pages:
        msg += f'Failed pages: {len(failed_pages)}\n'
        for i, page in enumerate(failed_pages, start=1):
            msg += f'\t[{i}] {page.name}\n'
    return msg

def send_notifications(config: EasyDict, msg: str, succeed_count: int, total_count: int) -> None:
    if config.ALARM.SLACK.TOKEN:
        SlackBot(token=config.ALARM.SLACK.TOKEN, channel_name=config.ALARM.SLACK.CHANNEL).send_message(msg)
        logger.info('Sent message to Slack')

    if config.ALARM.GMAIL.EMAIL:
        GmailSender(email=config.ALARM.GMAIL.EMAIL, password=config.ALARM.GMAIL.PASSWORD).send_email(
            to_emails=[config.ALARM.GMAIL.EMAIL],
            subject=f'[Notion2Chirpy] Process Result ({succeed_count}/{total_count} SUCCESS)',
            body=msg
        )
        logger.info('Sent email to Gmail')

def main(config: EasyDict) -> None:
    pages = get_posting_pages(config)
    succeed_pages, failed_pages = process_pages(config, pages)
    
    msg = generate_result_message(config, pages, succeed_pages, failed_pages)
    logger.info(msg)
    
    send_notifications(config, msg, len(succeed_pages), len(pages))
    logger.info('All processes completed!')

if __name__ == '__main__':
    config = get_config()
    main(config)
