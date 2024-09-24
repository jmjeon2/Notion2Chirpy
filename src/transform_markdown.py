from pathlib import Path
from pprint import pprint

from dt import convert_date_format
from icons import transform_markdown
from loggers import get_logger

logger = get_logger('notion2md', 'notion2md.log')


def processing_markdown(input_md_fp: str, output_dir: str) -> str:
    """
    Args:
        input_md_fp: markdown file path
        output_dir: output directory path
    """
    # read markdown file
    front_matter, content = transform_front_matter(input_md_fp)

    print("Markdown Front Matter")
    front_matter_md = dict_to_md(front_matter)
    print(front_matter_md)

    """ content processing """
    content = transform_markdown(content)

    # add content below front matter
    final_md = f'{front_matter_md}{content}'

    print("Final Markdown")
    print(final_md)

    # set output file path
    date = front_matter['date'].split(' ')[0]  # 2024-09-21 00:00:00 +0900 -> 2024-09-21
    title = ''.join(e for e in front_matter['title'] if e.isalnum() or e == ' ').replace(' ',
                                                                                         '-')  # get title english & number only and replace space to '-'
    output_fp = Path(output_dir) / f'{date}-{title}.md'

    # write markdown file
    with open(output_fp, 'w') as f:
        f.write(final_md)


def transform_front_matter(input_md_fp):
    with open(input_md_fp, 'r') as f:
        md = f.read()
    # delete 1 row title
    md = md.split('\n\n', 2)

    # split front matter and content
    front_matter = md[1]
    content = md[2]

    # parsing front matter (key: value)
    front_matter = front_matter.split('\n')
    front_matter = [x.split(': ') for x in front_matter]
    front_matter = dict(front_matter)
    print("DEBUG1")
    print(front_matter)

    # processing front matter
    essential_keys = ['title', 'description', 'date', 'categories', 'tags']
    fixed_matter = {'author': 'jmjeon'}  # , 'pin': 'false', 'math': 'false', 'mermaid': 'false'}
    all_keys = ['title', 'description', 'date', 'categories', 'tags', 'author', 'pin', 'math', 'mermaid']

    # remove unnecessary keys
    keys = list(front_matter.keys())
    for key in keys:
        if key not in all_keys:
            front_matter.pop(key)

    # add fixed matter to front matter
    for key in fixed_matter:
        front_matter[key] = fixed_matter[key]

    # add math, mermaid if exist
    if '$' in content:
        front_matter['math'] = 'true'
    if 'mermaid' in content:
        front_matter['mermaid'] = 'true'

    # apply date format (2024년 9월 21일 오전 12:00 (GMT+9) -> 2024-09-21 00:00:00 +0900)
    front_matter['date'] = convert_date_format(front_matter['date'])
    print("Dict Front Matter")
    pprint(front_matter)

    # convert title to "title" (제목에 기호가 들어가면 오류 발생)
    front_matter['title'] = f"\"{front_matter['title']}\""

    # convert A, B, C -> [A, B, C]
    front_matter['categories'] = front_matter['categories'].split(', ')
    front_matter['tags'] = front_matter['tags'].split(', ')
    print("Final Front Matter")
    print(front_matter)

    return front_matter, content


def dict_to_md(front_matter: dict) -> str:
    md = '---\n'
    for k, v in front_matter.items():
        if isinstance(v, list):
            v = f"[{', '.join(v)}]"
        md += f'{k}: {v}\n'
    md += '---\n\n'
    return md


if __name__ == '__main__':
    input_md_fp = './sample/input/Notion2GithubPages 10a48a6e55fc804a894ce097d6b7c445.md'
    output_dir = '../sample/output/'
    processing_markdown(input_md_fp, output_dir)

    # 예시 markdown 파일
    """
    상태: 테스트
    카테고리: Python
    대주제: MLOps, Python
    소주제: WandB
    tags: pytorch, sweep, wandb, 딥러닝, 하이퍼파라미터
    Created Time: 2024년 9월 21일 오후 1:22
    Last Edited Time: 2024년 9월 21일 오후 1:35
    date: 2024년 9월 21일 오전 12:00 (GMT+9)
    연결: No
    title: [MLOps] WandB Sweep 사용방법 (pytorch 하이퍼 파라미터 튜닝)
    """
    """
    ---
    title: Text and Typography (jmjeon)
    description: Examples of text, typography, math equations, diagrams, flowcharts, pictures, videos, and more.
    author: jmjeon
    date: 2019-08-08 11:33:00 +0800
    categories: [Blogging, Demo]
    tags: [typography, hello, worle, 정민, 테스트, HEELLLO, WORLRE]
    pin: true
    math: true
    mermaid: true
    ---
    """
