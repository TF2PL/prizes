#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3 python3Packages.requests

import random
import requests
import traceback
import logging
import os


logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
    )

API_KEY = os.environ["FACEIT_API_KEY"]


def entries(hub, _, season, limit=50):
    logging.info(f"Hub {hub}, season {season}")
    offset = 0
    while True:
        logging.info(f"  page {offset // limit}")
        response = requests.get(
                f"https://open.faceit.com/data/v4/leaderboards/hubs/{hub}/seasons/{season}",
                headers=dict(authorization=f"Bearer {API_KEY}"),
                params=dict(
                    offset=offset,
                    limit=limit,
                ),
            )
        if not response.ok:
            logging.info(f"  retrying after HTTP {response.status_code}: {response.text}")
            continue
        data = response.json()
        if not data['items']:
            logging.info(f"  found empty page, assuming end")
            return
        for item in data['items']:
            name = item['player']['nickname']
            entries = item['played'] // 10
            if entries:
                logging.info(f"    {name}: {entries}")
                yield from [ f"{name} ({entries} entries)" ] * entries
        offset += limit


if __name__ == "__main__":
    random.seed("TF2PL")
    hubs = [
            ["d168a467-25a7-4eb4-92e9-d98501a15755", "NA Invite",   3],
            ["dee30db4-5db8-4ed0-a9a6-74ebbd5c612f", "NA Advanced", 3],
            ["3c265612-dd2a-4d1f-8cf4-c8a6c1d92472", "NA Amateur",  3],
            ["b23dd05f-5876-454c-9a48-4e35e105ebd8", "NA Beginner", 3],
            ["60166830-385b-4b26-acb5-4a6ba265623f", "EU Invite",   2],
            ["abce6d7d-c317-425f-944d-14b9235aec5c", "EU Advanced", 2],
            ["5dd0a523-dd96-420a-9c68-bbba6d0b1281", "EU Amateur",  2],
            ["f76beaa7-768b-4158-9a3c-0ae2b8ce3295", "EU Beginner", 2],
        ]
    for hub in hubs:
        all_entries = list(entries(*hub))
        if not all_entries:
            all_entries = [ "No participants" ]
        hub.append(random.choice(all_entries))
    for hub in hubs:
        print("Winner of the {}, season {} raffle is: {}".format(*hub[1:]))
