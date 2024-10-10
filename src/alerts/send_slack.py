from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackBot:
    def __init__(self, token, channel_name):
        """Slack API 클라이언트 초기화 및 채널 ID 설정"""
        self.client = WebClient(token=token)
        self.channel_name = channel_name
        self.channel_id = self.get_channel_id()

    def get_channel_id(self):
        """채널 ID 조회"""
        response = self.client.conversations_list()
        for channel in response['channels']:
            if channel['name'] == self.channel_name.replace('#', ''):
                return channel['id']
        print(f"'{self.channel_name}' 채널을 찾을 수 없습니다.")
        raise ValueError(f"'{self.channel_name}' 채널을 찾을 수 없습니다.")

    def find_message_ts_by_keyword(self, keyword):
        """키워드를 포함한 최근 메시지의 타임스탬프 찾기"""
        try:
            # 최근 20개의 메시지 조회
            response = self.client.conversations_history(channel=self.channel_id, limit=20)
            messages = response['messages']

            # 키워드가 포함된 메시지 찾기
            for message in messages:
                if keyword in message.get('text', ''):
                    return message['ts']  # 키워드를 포함한 메시지의 타임스탬프 반환
            return None  # 키워드를 포함한 메시지가 없으면 None 반환
        except SlackApiError as e:
            print(f"메시지 조회 실패: {e.response['error']}")
            return None

    def send_message(self, text, parent_msg: str = None):
        """
        parent_msg가 있으면 해당 키워드가 포함된 최근 메시지에 댓글로 전송.
        parent_msg가 없으면 새로운 메시지를 전송.
        """
        try:
            target_message_ts = None
            if parent_msg:
                # 키워드가 포함된 최근 메시지의 타임스탬프 찾기
                target_message_ts = self.find_message_ts_by_keyword(parent_msg)

            # 해당 메시지에 댓글 달기
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                text=text,
                thread_ts=target_message_ts if target_message_ts else None
            )
            print(f"새 메시지가 성공적으로 전송되었습니다: {response['ts']}")

        except SlackApiError as e:
            print(f"메시지 전송 실패: {e.response['error']}")

    def upload_file(self, file_path, file_comment=None, parent_msg=None):

        """파일을 특정 채널로 업로드"""
        try:
            target_message_ts = None
            if parent_msg:
                # 키워드가 포함된 최근 메시지의 타임스탬프 찾기
                target_message_ts = self.find_message_ts_by_keyword(parent_msg)

            response = self.client.files_upload_v2(
                channel=self.channel_id,
                initial_comment=file_comment,
                file=file_path,
                thread_ts=target_message_ts if target_message_ts else None
            )
            print(f"파일이 성공적으로 업로드되었습니다: {response['file']['id']}")
        except SlackApiError as e:
            print(f"파일 업로드 실패: {e.response['error']}")

