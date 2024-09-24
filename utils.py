import yaml
from easydict import EasyDict


def read_yaml(file_path) -> EasyDict:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        data = EasyDict(data)
    except Exception as e:
        print(e)
        raise ValueError(f'[Error] yaml 파일을 읽는데 실패했습니다. {file_path}')

    return data


if __name__ == '__main__':
    file_path = 'config.yaml'
    data = read_yaml(file_path)
    print(data)
