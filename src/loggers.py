import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(log_folder: str = './logs', log_file: str = 'app.log', logger_name: str = 'my_shared_logger'):
    # 로그 디렉토리 생성 (존재하지 않으면)
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # 로그 파일 경로
    log_path = os.path.join(log_folder, log_file)

    # 로거 설정 (이미 로거가 존재하는 경우, 중복 설정 방지)
    logger = logging.getLogger(logger_name)
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        # 포맷 설정 (파일명과 라인 번호 추가)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 파일 핸들러 설정 (최대 10MB, 10개까지 롤링)
        file_handler = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=10)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# 이미 설정된 로거를 가져오는 함수, 없으면 자동 설정 (로거 이름을 인자로 받음)
def get_logger(log_folder: str = './logs', log_file: str = 'app.log', logger_name: str = 'my_shared_logger'):
    logger = logging.getLogger(logger_name)

    # 로거에 핸들러가 없으면, 즉 설정되지 않았으면 setup_logger 호출
    if not logger.hasHandlers():
        setup_logger(log_folder, log_file, logger_name)

    return logger


if __name__ == '__main__':
    # 사용 예시
    log_folder = './logs'  # 로그 파일 저장 폴더 경로
    logger = get_logger(log_folder)

    # 테스트 로그 출력
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

    logger = get_logger(log_folder, 'my_app.log', 'my_app_logger')

    # 테스트 로그 출력
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
