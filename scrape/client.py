import re
from exceptions import AnimeNotFound
from string import capwords
from subprocess import PIPE, run
from typing import ClassVar, List, Optional
from urllib.parse import quote_plus, urlparse

import cfscrape
from bs4 import BeautifulSoup
from models import Episode


class KissAnimeClient:
    base_url: ClassVar = "https://kissanime.ru"

    def __init__(self, cookie_jar: str = "cookies.txt") -> None:
        self.cookie_jar = cookie_jar
        self.cf_cookies, self.user_agent = cfscrape.get_cookie_string(
            self.base_url
        )

    @property
    def base_command(self) -> List[str]:
        return [
            "curl",
            "--cookie",
            self.cf_cookies,
            "-b",
            self.cookie_jar,
            "-c",
            self.cookie_jar,
            "-A",
            self.user_agent,
        ]

    def solve_kissanime_captcha(self, redirected_url: str) -> None:
        attempt = quote_plus(f"{1},{3},")
        re_url = quote_plus(
            urlparse(redirected_url).path
            + "?"
            + urlparse(redirected_url).query
            + "&s=default"
        )

        post_url = f"{self.base_url}/Special/AreYouHuman2"
        get_url = f"{post_url}/?reUrl={re_url}"
        payload = f"reUrl={re_url}&answerCap={attempt}"

        for i in range(100):
            self.get_source(get_url)
            post_response = self.post_target(post_url, payload)

            if "Click here to try again" not in post_response:
                print(post_response)
                break

    def get_source(self, source_url: str) -> str:
        cmd = self.base_command + [source_url]
        stream = run(cmd, stdout=PIPE, universal_newlines=True).stdout
        return "".join(stream.splitlines())

    def post_target(self, target_url: str, payload: str) -> str:
        cmd = self.base_command + [
            target_url,
            "-L",
            "--data",
            payload,
        ]
        stream = run(cmd, stdout=PIPE, universal_newlines=True).stdout
        return "".join(stream.splitlines())

    def get_status_code(self, source_url: str) -> str:
        cmd = self.base_command + ["-I", source_url]
        stream = run(cmd, stdout=PIPE, universal_newlines=True).stdout
        return stream.splitlines()[0]

    @staticmethod
    def format_anime_name(anime_name: str) -> str:
        return (
            capwords(anime_name).replace(" ", "-").replace("'", "-")
        )

    @staticmethod
    def episode_number_to_tag(episode_number: int) -> str:
        return f"Episode-{str(episode_number).rjust(3, '0')}"

    @staticmethod
    def episode_tag_to_number(episode_tag: str) -> int:
        return int(episode_tag[-3:])

    def get_episode_links(
        self, anime_name: str, specified_episodes: Optional[List[int]]
    ) -> List[Episode]:
        url = f"{self.base_url}/Anime/{self.format_anime_name(anime_name)}"

        if self.get_status_code(url).split() == ["HTTP/2", "302"]:
            raise AnimeNotFound(anime_name, url)

        soup = BeautifulSoup(self.get_source(url), "html.parser")
        tagged_links = {
            re.search(r"Episode-\d{3}", a["href"]).group(0): a["href"]
            for a in soup.find(
                "table", {"class": "listing"}
            ).find_all("a", href=True)
            if re.search(r"Episode-\d{3}", a["href"])
        }

        episodes = [
            Episode(tag, self.base_url + link)
            for tag, link in tagged_links.items()
            if not specified_episodes
            or self.episode_tag_to_number(tag) in specified_episodes
        ]

        return sorted(
            episodes, key=lambda x: self.episode_tag_to_number(x.tag)
        )

    def get_download_link(self, episode_link) -> str:
        if self.get_status_code(episode_link).split() == [
            "HTTP/2",
            "302",
        ]:
            self.solve_kissanime_captcha(episode_link)

        # soup = BeautifulSoup(self.get_source(episode_link), "html.parser")
        # return soup.find(id="divDownload").find("a", href=True)["href"]
