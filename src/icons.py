import re


def transform_markdown(md_text):
    """
        notion의 callout 블록은 markdown 출력시 <aside>로 변환됨
        따라서 <aside> 태그를 찾아서 이모지를 제거하고 chirpy의 prompt-tip으로 출력하도록 변환
    """
    # 패턴: <aside> ... 이모지 ... </aside> 형식을 찾습니다
    pattern = re.compile(r"<aside>\s*([\U0001F000-\U0001FFFF])\s*(.*?)\s*</aside>", re.DOTALL)

    # content 안에서 줄바꿈을 <br>로 대체
    def replace_newlines(match):
        content = match.group(2).strip()
        content_with_br = content.replace('\n', '<br>')
        return f"> {content_with_br}\n{{: .prompt-tip }}"

    # 대체 작업
    transformed_text = pattern.sub(replace_newlines, md_text)

    return transformed_text


if __name__ == '__main__':
    # 예시 마크다운 텍스트
    md_example = """<aside>
    💡

    This is a tip on the first line.
    This is a tip on the second line.
    aosdihf

    adosifh
    aosdihf

    asoigdhlkhadsfioh
    aosdihg

    asdoifh

    </aside>

    hello world
    # thisis a test

    <aside>
    🔥

    Another tip with multiple lines.
    More information here.

    </aside>
    """

    # 변환 후 결과 출력
    transformed = transform_markdown(md_example)
    print(transformed)
