from inspect import cleandoc
from typing import Any

import ruamel.yaml
from docopt import docopt  # type: ignore

from client import KissAnimeClient
from models import Anime

cli = cleandoc(
    """
    Usage:
      scrape <config_path> [--dry-run]

    Options:
      --dry-run
    """
)


def entrypoint() -> None:
    arguments = docopt(cli)
    main(arguments["<config_path>"], arguments["--dry-run"])


def main(config_path: str, dry_run: bool) -> None:
    config = load_yaml(config_path)
    client = KissAnimeClient()
    anime_list = [
        Anime(
            anime_name,
            client.get_episode_links(anime_name, specified_episodes),
        )
        for anime_name, specified_episodes in config.items()
    ]

    for anime in anime_list:
        for episode in anime.episodes:
            client.get_download_link(episode.link)


def load_yaml(path: str) -> Any:
    with open(path, "r") as stream:
        return ruamel.yaml.load(stream, Loader=ruamel.yaml.Loader)


if __name__ == "__main__":
    entrypoint()
