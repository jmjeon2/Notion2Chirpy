from datetime import datetime


def convert_date_format(date_str):
    # datetime 객체로 변환
    date_object = datetime.strptime(date_str, '%Y년 %m월 %d일')

    # 현재 시간 가져오기 (시, 분, 초)
    current_time = datetime.now()

    # 원하는 형식으로 출력 (날짜 + 현재 시간 + 타임존)
    output = date_object.strftime('%Y-%m-%d') + current_time.strftime(' %H:%M:%S +0900')

    return output


if __name__ == '__main__':
    input_date = '2024년 9월 21일'
    output = convert_date_format(input_date)
    print(output)
