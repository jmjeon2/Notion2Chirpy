import re
from enum import Enum


class CallOutEmoji(Enum):
    TIP = ["💡"]  # all the other emojis
    INFO = ["📌", "🔍", "📝", "📢", "📚", "📖"]
    WARNING = ["⚠️", "⚡", "🚧", "🟠" "🟧"]
    DANGER = ["🔥", "🚨", "🚫", "❌", "🛑", "⛔"]


class PromptType(Enum):
    TIP = "{: .prompt-tip }"
    INFO = "{: .prompt-info }"
    WARNING = "{: .prompt-warning }"
    DANGER = "{: .prompt-danger }"


def set_prompt_type(emoji):
    if emoji in CallOutEmoji.INFO.value:
        return PromptType.INFO.value
    elif emoji in CallOutEmoji.WARNING.value:
        return PromptType.WARNING.value
    elif emoji in CallOutEmoji.DANGER.value:
        return PromptType.DANGER.value
    else:
        return PromptType.TIP.value


def transform_callout(md_text):
    """
        notion의 callout 블록은 markdown 출력시 <aside>로 변환됨
        따라서 <aside> 태그를 찾아서 이모지를 제거하고 chirpy의 prompt-tip으로 출력하도록 변환
    """
    # 패턴: <aside> ... 이모지 ... </aside> 를 찾음
    pattern = re.compile(
        r"<aside>\s*(["
        "\U0001F000-\U0001FFFF"  # 이모지, 기호 등 유니코드 확장 영역
        "\U0001F600-\U0001F64F"  # 얼굴 이모지
        "\U0001F300-\U0001F5FF"  # 상징 및 객체
        "\U0001F680-\U0001F6FF"  # 교통 및 기계
        "\U0001F700-\U0001F77F"  # 기호 및 도형
        "\U0001F780-\U0001F7FF"  # 추가 기호
        "\U0001F800-\U0001F8FF"  # 확장된 이모지
        "\U0001F900-\U0001F9FF"  # 이모지 확장
        "\U0001FA00-\U0001FAFF"  # 새로운 객체 및 활동
        "\u2600-\u26FF"  # 기타 기호
        "\u2700-\u27BF"  # 추가 기호 및 체크 표시
        "])\s*(.*?)\s*</aside>",
        re.DOTALL
    )

    def replace_newlines(match):
        emoji = match.group(1)
        content = match.group(2).strip()

        # prompt 설정
        prompt = set_prompt_type(emoji)

        # content의 줄바꿈을 처리
        content = content.split('\n')
        content = ['> ' + line for line in content]
        content = '\n'.join(content)

        return f"{content}\n{prompt}\n"

    # 대체 작업
    transformed_text = pattern.sub(replace_newlines, md_text)

    return transformed_text


if __name__ == '__main__':
    # 예시 마크다운 텍스트
    md_example = """
<aside>
✅

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

Another tip with multiple lines.
More information here.

</aside>
    """

    md_example = """

<aside>
💡

제목 엔터침

줄글1 엔터침

줄글2 엔터

</aside>

<aside>
🔥

제목 
엔터 안침
엔터 안침

- helloworld

### aosdihf

- 이 안에 내용
- 이 안에 수식
- 인라인 수식 $E=mc^2$
- 그냥 수식

$$
E=mc^2
$$

후후..

</aside>

    """

    # 변환 후 결과 출력
    transformed = transform_callout(md_example)
    print(transformed)
