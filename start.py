#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

PROFILES_URL = "https://api.mojang.com/profiles/minecraft"
STREAM_WHITELIST_URL = "https://whitelist.twitchapps.com/list.php?id=warths5657829972d9b&format=json"
WHITELIST_FILE = "whitelist.json"
ALL_OPS = True  # If True, Every whitelisted player will be OP. May be useful for Creative Servers.
OPS_FILE = "ops.json"
OPS_PERMISSION_LEVEL = 2
OPS_BYPASSES_PLAYER_LIMIT = False
LEVEL_4_OP_NAME = ["Warths", "Guerrierra", "Everynight_MC"]
EXCLUDED_OPS = ["MyTheValentinus"]

def _post(url, body, head):
    response = requests.post(url, data=body, headers=head)
    return response.json()


def find_profiles_by_names(names):
    result = []
    pages = [names[i:i + 100] for i in range(0, len(names), 100)]
    for page in pages:
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        body = json.dumps(page)
        result += _post(PROFILES_URL, body, headers)
    return result


def format_uuid(uuid):
    full_uuid = "%s-%s-%s-%s-%s" % (uuid[:8], uuid[8:12], uuid[12:16], uuid[16:20], uuid[20:])
    return full_uuid


if __name__ == '__main__':
    # Get list from Sub Whitelist
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    request = requests.get(STREAM_WHITELIST_URL, headers=headers)
    if request.status_code == 200:
        result = request.json()
        names = []
        for name in result:
            names.append(result[name]['whitelist_name'])

        list_player = find_profiles_by_names(names)
        whitelist = []
        ops = []

        for player in list_player:
            full_uuid = format_uuid(player['id'])
            whitelist_block = {'uuid': full_uuid, 'name': player['name']}
            whitelist.append(whitelist_block)
            ops_block = {'uuid': full_uuid,
                         'name': player['name'],
                         'level': 4 if player['name'] in LEVEL_4_OP_NAME else
                                  0 if player['name'] in EXCLUDED_OPS else
                                  2,
                         'bypassesPlayerLimit': True if player['name'] in LEVEL_4_OP_NAME else
                                                True if OPS_BYPASSES_PLAYER_LIMIT else False}
            ops.append(ops_block)
        ops = json.dumps(ops, indent=4)
        whitelist = json.dumps(whitelist, indent=4)

        if ALL_OPS:
            try:
                with open(OPS_FILE, 'w') as Opslist:
                    Opslist.write(ops)
                    Opslist.close()
            except:
                print("Error when writing OP list file")

        try:
            with open(WHITELIST_FILE, 'w') as Whitelist:
                Whitelist.write(whitelist)
                Whitelist.close()
        except:
            print("Error when writing whitelist file")
