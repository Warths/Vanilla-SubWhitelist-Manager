# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import subprocess
import time

PROFILES_URL = "https://api.mojang.com/profiles/minecraft"
STREAM_WHITELIST_URL = "https://whitelist.twitchapps.com/list.php?id=warths5657829972d9b&format=json"
WHITELIST_FILE = "whitelist.json"
OPS_FILE = "ops.json"
ALL_OPS = True  # If True, Every whitelisted player will be OP. May be useful for Creative Servers.
OPS_PERMISSION_LEVEL = 2 # AS
OPS_BYPASSES_PLAYER_LIMIT = False
LEVEL_4_OP_NAME = ["Warths", "Guerrierra", "Everynight_MC"]
EXCLUDED_OPS = ["MyTheValentinus"]
RELOAD_OP_LIST = True  # Force a Server Restart if OP list is changed
SCREEN_NAME = "minecraft"


def _post(url, body, head):
    response = requests.post(url, data=body, headers=head)
    return response.json()


def find_profiles_by_names(subwl_names):
    result = []
    pages = [subwl_names[i:i + 100] for i in range(0, len(subwl_names), 100)]
    for page in pages:
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        body = json.dumps(page)
        result += _post(PROFILES_URL, body, headers)
    return result


def format_uuid(uuid):
    formatted_uuid = "%s-%s-%s-%s-%s" % (uuid[:8], uuid[8:12], uuid[12:16], uuid[16:20], uuid[20:])
    return formatted_uuid


def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError:
        print('Echec de la commande : ' + cmd)
        return


def stop_server():
    for t in range(15, 0, -5):
        run_minecraft_cmd('say Stopping in %s ...' % str(t))
        time.sleep(5)
    run_minecraft_cmd('stop')


def run_minecraft_cmd(string):
    string = string.replace('"', '\\"')
    run_cmd('screen -S %s -X stuff "%s^M"' % (SCREEN_NAME, string))


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
        for player in list_player:
            full_uuid = format_uuid(player['id'])
            whitelist_block = {'uuid': full_uuid, 'name': player['name']}
            whitelist.append(whitelist_block)
        whitelist = json.dumps(whitelist, indent=4)
        try:
            with open(WHITELIST_FILE, 'w') as Whitelist:
                Whitelist.write(whitelist)
                Whitelist.close()
        except:
            print("Error when writing whitelist file")
        if ALL_OPS:
            with open(OPS_FILE, 'r') as file:
                ops_json = json.load(file)
            with open(WHITELIST_FILE, 'r') as file:
                whitelist_json = json.load(file)
            for op_player in ops_json:
                if op_player['uuid'] in whitelist:
                    if op_player['name'] in EXCLUDED_OPS:
                        run_minecraft_cmd("deop %s" % (op_player['name']))
                else:
                    run_minecraft_cmd("op %s" % (op_player['name']))
            ops_json = json.dumps(ops_json, indent=4)
            for whitelisted_player in whitelist_json:
                if whitelisted_player['uuid'] in ops_json:
                    if whitelisted_player['name'] in EXCLUDED_OPS:
                        run_minecraft_cmd("deop %s" % (whitelisted_player['name']))
                elif whitelisted_player['name'] not in EXCLUDED_OPS:
                        run_minecraft_cmd("op %s" % (whitelisted_player['name']))




