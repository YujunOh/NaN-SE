"""SRP 위반 예시. nanse analyze로 돌려보기 위한 샘플.

AuthService가 인증, 이메일 발송, 토큰 발급, 비밀번호 검증까지 담당한다.
LCOM4가 1보다 커야 하고 finding이 떠야 한다.
"""


class AuthService:
    def __init__(self):
        self.user = None
        self.smtp_host = "localhost"
        self.token_secret = "secret"
        self.failed_attempts = 0

    def login(self, username, password):
        if self._verify_password(password):
            self.user = username
            self.failed_attempts = 0
            return True
        self.failed_attempts += 1
        return False

    def logout(self):
        self.user = None

    def _verify_password(self, password):
        return len(password) >= 8

    def send_welcome_email(self, address):
        return f"sending via {self.smtp_host} to {address}"

    def issue_token(self):
        return f"token-{self.token_secret}"


class Counter:
    """응집된 클래스. finding이 안 떠야 한다."""

    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

    def value(self):
        return self.count
