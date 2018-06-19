#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3 python3Packages.requests

import datetime
import requests
import traceback
import logging
import os
import collections


logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
    )

API_KEY = os.environ["FACEIT_API_KEY"]


def entries(hub, start, end, name, limit=20):
    counter = collections.Counter()
    logging.info(f"Hub {name}")
    offset = 0
    while True:
        logging.info(f"  page {offset // limit}")
        response = requests.get(
                "https://api.faceit.com/match-history/v4/matches/competition",
                # headers=dict(authorization=f"Bearer {API_KEY}"),
                params=dict(
                    id=hub,
                    page=offset//limit,
                    size=limit,
                    type="hub",
                ),
            )
        if response.status_code == 500:
            logging.error("FACEIT broke")
            break
        if not response.ok:
            logging.info(f"  retrying after HTTP {response.status_code}: {response.text}")
            continue
        data = response.json()
        if not data['payload']:
            logging.info(f"  found empty page, assuming end")
            break
        for item in data['payload']:
            item["finishedAt"] = datetime.datetime.strptime(item["finishedAt"], "%a %b %d %H:%M:%S %Z %Y").timestamp()
            if item["finishedAt"] < start:
                logging.info("  found match younger than the range we're looking for, ending")
                break
            if item["finishedAt"] not in range(start, end):
                continue
            if item["state"] != "finished":
                continue
            logging.info(f"  Match {item['matchId']} ({item['state']})")
            stats_response = requests.get(
                    f"https://open.faceit.com/data/v4/matches/{item['matchId']}/stats",
                    headers=dict(authorization=f"Bearer {API_KEY}"),
                )
            if not stats_response.ok:
                logging.info(f"    got HTTP {stats_response.status_code}: {stats_response.text}")
                continue
            stats = stats_response.json()
            for team in stats['rounds'][0]['teams']:
                for player in team["players"]:
                    counter[player['nickname']] += int(player['player_stats']['ÜberCharges'])
        else:
            offset += limit
            continue
        break
    return counter


if __name__ == "__main__":
    hubs = [
            {"hub": "d168a467-25a7-4eb4-92e9-d98501a15755", "start": 1525132800, "end": 1527811200, "name": "NA Invite"},
            {"hub": "dee30db4-5db8-4ed0-a9a6-74ebbd5c612f", "start": 1525132800, "end": 1527811200, "name": "NA Advanced"},
            {"hub": "3c265612-dd2a-4d1f-8cf4-c8a6c1d92472", "start": 1525132800, "end": 1527811200, "name": "NA Amateur"},
            {"hub": "b23dd05f-5876-454c-9a48-4e35e105ebd8", "start": 1525132800, "end": 1527811200, "name": "NA Beginner"},
            {"hub": "60166830-385b-4b26-acb5-4a6ba265623f", "start": 1525132800, "end": 1527811200, "name": "EU Invite"},
            {"hub": "abce6d7d-c317-425f-944d-14b9235aec5c", "start": 1525132800, "end": 1527811200, "name": "EU Advanced"},
            {"hub": "5dd0a523-dd96-420a-9c68-bbba6d0b1281", "start": 1525132800, "end": 1527811200, "name": "EU Amateur"},
            {"hub": "f76beaa7-768b-4158-9a3c-0ae2b8ce3295", "start": 1525132800, "end": 1527811200, "name": "EU Beginner"},
        ]
    for hub in hubs:
        hub['counter'] = entries(**hub)
        print("Top 4 Medics for {name}:".format_map(hub))
        for (rank, (name, ubers)) in enumerate(hub['counter'].most_common(4), start=1):
            print(f" #{rank} {name} with {ubers} ubercharges")
        print("\n\n\n")
    for hub in hubs:
        print("Top 4 Medics for {name}:".format_map(hub))
        for (rank, (name, ubers)) in enumerate(hub['counter'].most_common(4), start=1):
            print(f" #{rank} {name} with {ubers} ubercharges")
