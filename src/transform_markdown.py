from src.dt import convert_date_format
from src.icons import transform_callout
from src.loggers import get_logger
from src.models import MDInfo

logger = get_logger(logger_name='notion2md')


def processing_markdown(input_md_fp: str) -> MDInfo:
    """
    notion의 markdown file을 chirpy에 맞게 변환하는 함수
        1. Read markdown file
        2. Transform front matter (notion의 컬럼 정보를 front matter로 변환)
        3. Transform markdown content (notion의 markdown 내용 중 chirpy에 맞게 변환)
            - callout <aside>를 info prompt로 변경
            - 날짜 포맷 변경
        4. http link를 https로 변경
        5. Write markdown file (파일명: 날짜-제목.md)

    Args:
        input_md_fp: markdown file path
        output_dir: output directory path
    """

    """ front matter processing """
    front_matter, content = transform_front_matter(input_md_fp)
    front_matter_md = _dict_to_md(front_matter)

    """ content processing """
    # transform callout
    content = transform_callout(content)

    # replace http to https
    content = content.replace('http://', 'https://')

    # add content below front matter
    final_md = f'{front_matter_md}{content}'

    # set output file path
    date = front_matter['date'].split(' ')[0]  # 2024-09-21 00:00:00 +0900 -> 2024-09-21
    post_uid = front_matter['uid']
    output_filepath = f'{date}-{post_uid}.md'

    md = MDInfo(filepath=output_filepath, content=final_md)

    return md


def transform_front_matter(input_md_fp) -> (dict, str):
    with open(input_md_fp, 'r') as f:
        md = f.read()
    # delete 1 row title
    md = md.split('\n\n', 2)

    # split front matter and content
    page_name = md[0][2:]  # delete '# ' in title
    front_matter = md[1]
    content = md[2]

    # parsing front matter (key: value)
    front_matter = front_matter.split('\n')
    front_matter = [x.split(': ') for x in front_matter]
    front_matter = dict(front_matter)

    # merge category
    front_matter['categories'] = front_matter['category1'] + ', ' + front_matter['category2']

    # processing front matter
    essential_keys = ['title', 'date', 'categories', 'tags', 'uid']  # 'description'
    fixed_matter = {}  # 'author': 'jmjeon', 'pin': 'false', 'math': 'false', 'mermaid': 'false'} # author 미지정시 _config.yaml 기본 값으로 사용함
    all_keys = ['title', 'description', 'date', 'categories', 'tags', 'author', 'pin', 'math', 'mermaid', 'uid']

    # remove unnecessary keys
    keys = list(front_matter.keys())
    for key in keys:
        if key not in all_keys:
            front_matter.pop(key)

    # add fixed matter to front matter
    for key in fixed_matter:
        front_matter[key] = fixed_matter[key]

    # validate essential keys
    for key in essential_keys:
        if key not in front_matter:
            logger.error(f'Essential key not found: {key}')
            raise KeyError(f'Essential key not found: {key}')

    # add math, mermaid if exist
    if '$' in content:
        front_matter['math'] = 'true'
    if 'mermaid' in content:
        front_matter['mermaid'] = 'true'

    # apply date format (2024년 9월 21일 오전 12:00 (GMT+9) -> 2024-09-21 00:00:00 +0900)
    front_matter['date'] = convert_date_format(front_matter['date'])

    # convert title to "title" (제목에 기호가 들어가면 오류 발생)
    front_matter['title'] = f"\"{front_matter['title']}\""

    # convert A, B, C -> [A, B, C]
    front_matter['categories'] = front_matter['categories'].split(', ')
    front_matter['tags'] = front_matter['tags'].split(', ')

    return front_matter, content


def _dict_to_md(front_matter: dict) -> str:
    """
    Convert dictionary front matter to markdown format with ---
    """
    md = '---\n'
    for k, v in front_matter.items():
        if isinstance(v, list):
            v = f"[{', '.join(v)}]"
        md += f'{k}: {v}\n'
    md += '---\n\n'
    return md


if __name__ == '__main__':
    input_md_fp = '/Users/jmjeon/Desktop/Project/Personal/039_Notion2Chirpy/test/samples/exported_md/[테스트페이지] pyenv 사용 10d48a6e55fc800a995befe6dfe52b98 2.md'
    md = processing_markdown(input_md_fp)
    print(md)

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
