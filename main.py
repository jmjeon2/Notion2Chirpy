from datetime import datetime
from pathlib import Path
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

    failed_pages: [PageInfo] = []
    succeed_pages: [PageInfo] = []

    # export notion data (markdown)
    for i, page in enumerate(pages, start=1):
        logger.info(f'Start [{i}]th Processing {page.name}')
        try:
            succeed = process(page)

            # update notion db
            if succeed:
                update_notion_db(config, page)
                logger.info(f'Updated notion db. page name: {page.name}')
                succeed_pages.append(page)
            else:
                failed_pages.append(page)

        except Exception as e:
            logger.error(f'Error occurred in {page.name}')
            logger.error(e)
            logger.error(traceback.format_exc())
            failed_pages.append(page.name)
            continue

        logger.info(f'Processed {page.name}')

    msg = f'Total pages: {len(pages)}\n'
    if succeed_pages:
        msg += f'Total succeed pages: {len(succeed_pages)}\n'
        for i, page in enumerate(succeed_pages, start=1):
            url = f'https://{config.GITHUB.REPO_NAME}/posts/{page.uid}/'
            msg += f'\t[{i}] Succeed page: {page.name}, url: {url}\n'
        logger.info(msg)

    if failed_pages:
        msg += f'Total failed pages: {len(failed_pages)}\n'
        for i, page in enumerate(failed_pages, start=1):
            msg += f'\t[{i}] Failed page: {page.name}\n'
        logger.info(msg)

    # send message to slack
    if config.ALARM.SLACK.TOKEN:
        slack_bot = SlackBot(token=config.ALARM.SLACK.TOKEN,
                             channel_name=config.ALARM.SLACK.CHANNEL)
        slack_bot.send_message(msg)
    logger.info('Send message to slack')

    # send email to gmail
    if config.ALARM.GMAIL.EMAIL:
        gmail_sender = GmailSender(email=config.ALARM.GMAIL.EMAIL,
                                   password=config.ALARM.GMAIL.PASSWORD)
        gmail_sender.send_email(to_emails=[config.ALARM.GMAIL.EMAIL],
                                subject=f'[Notion2Chirpy] Process Result Notification ({len(succeed_pages)}/{len(pages)} SUCCESS)',
                                body=msg)
    logger.info('Send email to gmail')

    logger.info('All process done!')


if __name__ == '__main__':
    config = get_config()
    main(config)
