class AnimeNotFound(Exception):
    def __init__(self, name: str, url_attempt: str) -> None:
        msg = f"{name} not found\nTried {url_attempt}"
        super().__init__(msg)


class CloudflareError(Exception):
    def __init__(self) -> None:
        msg = "Could not get cloudflare credentials"
        super().__init__(msg)


class CaptchaError(Exception):
    def __init__(self) -> None:
        msg = "Could not solve captcha"
        super().__init__(msg)
