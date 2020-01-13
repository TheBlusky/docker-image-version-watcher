from time import sleep

import docker
from dxf import DXF
from dxf.exceptions import DXFError
from functools import reduce
import requests
import os


def log(message, notify=False):
    print(message)
    if notify:
        if gotify_url := os.environ.get("GOTIFY_URL", False):
            requests.post(
                gotify_url,
                json={"title": "Docker Image Version Watcher", "message": message},
            )
        if slack_url := os.environ.get("SLACK_URL", False):
            channel = os.environ.get("SLACK_CHANNEL", "#general")
            username = os.environ.get("SLACK_USERNAME", "DockerImageVersionWatcher")
            requests.post(
                slack_url,
                json={"text": message, "username": username, "channel": channel},
            )


def check_remote(repo, tag, image_digest, container_name):
    if "/" not in repo:
        repo = "library/" + repo
    try:
        dxf = DXF("index.docker.io", repo)
        dxf.token = requests.get(
            "https://auth.docker.io/token?service=registry.docker.io&scope=repository:"
            + repo
            + ":pull"
        ).json()["token"]
        remote_digest = dxf.get_digest(alias=tag)
        if remote_digest != image_digest:
            log(f"{container_name}\t{repo}:{tag}\tOutdated", notify=True)
        else:
            log(f"{container_name}\t{repo}:{tag}\tUp to date", notify=False)
    except DXFError:
        log(
            f"{container_name}\t{repo}:{tag}\tNot Found",
            notify=True,
        )


def do_check():
    client = docker.from_env()
    containers = client.containers.list(all=True)
    for container in containers:
        container_name = container.name
        image = container.image
        image_repotag = image.attrs["RepoTags"][0]
        tag = image_repotag.split(":")[1]
        image_digest = image.attrs["Id"]
        miss = reduce(
            lambda res, element: (
                (res[0] + 1, res[1])
                if element["Id"] == "<missing>"
                else (res[0], res[1] + 1)
            ),
            image.history(),
            (0, 0),
        )
        repo = image_repotag.split(":")[0]
        if miss[1] > 1:
            from_image_tag = None
            from_image_id = None
            for sub_image in image.history()[1:]:
                if from_image_tag is None and sub_image["Tags"]:
                    from_image_tag = sub_image["Tags"][0]
                    from_image_id = sub_image["Id"]
            if from_image_tag is not None:
                log(
                    f"{container_name}\t{repo}:{tag}\tFROM {from_image_tag}",
                    notify=False,
                )
                check_remote(
                    from_image_tag.split(":")[0],
                    from_image_tag.split(":")[1],
                    from_image_id,
                    container_name,
                )
            else:
                log(f"{container_name}\t{repo}:{tag}\tUnknown FROM", notify=True)
        else:
            check_remote(repo, tag, image_digest, container_name)


if __name__ == "__main__":
    while True:
        do_check()
        sleep(3600 * 24)
