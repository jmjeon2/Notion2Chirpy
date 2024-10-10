import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List


class GmailSender:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(self, to_emails: List[str], subject: str, body: str, attachments: List[str] = None):
        try:
            # SMTP 서버 연결 설정
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)

            # 이메일 메시지 설정
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = ", ".join(to_emails)
            msg['Subject'] = subject

            # 이메일 본문 추가
            msg.attach(MIMEText(body, 'plain'))

            # 첨부 파일 추가
            if attachments:
                for file_path in attachments:
                    attachment = open(file_path, "rb")
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={file_path}')
                    msg.attach(part)
                    attachment.close()

            # 이메일 전송
            server.sendmail(self.email, to_emails, msg.as_string())
            server.quit()
            print(f"Email sent to {', '.join(to_emails)} successfully.")

        except Exception as e:
            print(f"Failed to send email. Error: {e}")

