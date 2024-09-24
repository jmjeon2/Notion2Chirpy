from pathlib import Path

from easydict import EasyDict

from src.loggers import get_logger
from src.notion_download import export_notion_data
from src.transform_markdown import processing_markdown
from src.utils import read_yaml

logger = get_logger(logger_name='notion2md')


def main(config: EasyDict):
    # export notion data (markdown)
    md_paths = export_notion_data(config)

    logger.info(f'Exported {len(md_paths)} markdown files')

    # transform markdown to chirpy format
    for md_path in md_paths:
        output = processing_markdown(md_path)

        logger.info(f'Processed {md_path} to {output["title"]}')

        # save md file
        title, content = output['title'], output['content']
        save_fp = Path(config.GITHUB_PAGES.POST_PATH) / title
        with open(save_fp, 'w') as f:
            f.write(content)
        logger.info(f'Saved {title}')




if __name__ == '__main__':
    config = read_yaml('./config.yaml')
    main(config)
