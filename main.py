from pathlib import Path

from easydict import EasyDict

from src.loggers import get_logger
from src.notion_sdk.notion_download import export_notion_data
from src.replace_image import replace_image_urls
from src.transform_markdown import processing_markdown
from src.utils import read_yaml, delete_file

logger = get_logger(logger_name='notion2md')


def main(config: EasyDict):
    # export notion data (markdown)
    md_paths = export_notion_data(config)

    logger.info(f'Exported {len(md_paths)} markdown files')

    for md_path in md_paths:
        # transform markdown to chirpy format
        output = processing_markdown(md_path)
        title, content = output['title'], output['content']

        # transform image url
        md_parent_path = Path(md_path).parent
        content = replace_image_urls(content, md_parent_path, config.IMGUR.CLIENT_ID)

        logger.info(f'Markdown Processed {md_path} to {output["title"]}')

        # save md file
        save_fp = Path(config.GITHUB_PAGES.POST_PATH) / title
        with open(save_fp, 'w') as f:
            f.write(content)
        logger.info(f'Saved markdown file in {save_fp}')

        # delete exported md file
        delete_file(md_path)


if __name__ == '__main__':
    config = read_yaml('./config.yaml')
    main(config)
