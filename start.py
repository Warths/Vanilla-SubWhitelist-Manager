#!/usr/bin/env python
# encoding:utf-8

import json
import requests
import subprocess

PROFILES_URL = "https://api.mojang.com/profiles/minecraft"
# Twitch Partners and Affiliates can use whitelist.twitchapps.com json export
# You can use something else as long as json keys are respected
STREAM_WHITELIST_URL = "https://whitelist.twitchapps.com/list.php?id=warths5657829972d9b&format=json"
# Relative path to Whitelist and OP files
WHITELIST_FILE = "whitelist.json"
OPS_FILE = "ops.json"
# If True, all players will be OP on the server, with the Userlevel specified in server.properties
GLOBAL_OP_PERMISSIONS = True
EXCLUDED_OPS = []
EXCLUDED_OPS = [name.lower() for name in EXCLUDED_OPS]
# Op that can't be altered by the program.
PRECONFIGURED_OP = ["Warths", "Guerrierra", "Everynight_MC", "Verrhues"]
PRECONFIGURED_OP = [name.lower() for name in PRECONFIGURED_OP]
SCREEN_NAME = "server"
# Will log every changes in the Minecraft Chat if True
TELLRAW_LOG = True



def _post(url, body, head):
    response = requests.post(url, data=body, headers=head)
    return response.json()

def GetUUID(name):
    result = []
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    body = json.dumps(name)
    result = _post(PROFILES_URL, body, headers)
    return result

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError:
        print('Echec de la commande : ' + cmd)
        return


def run_minecraft_cmd(string):
    string = string.replace('"', '\\"')
    run_cmd('screen -S %s -X stuff "%s^M"' % (SCREEN_NAME, string))


def action(action, player_name, reason="Unspecified"):
    if not GetUUID(player_name):
        print("UUID doesn't refer to existing account, skipping %s" % player_name)
        return

    if action == "whitelist":
        command_strings = ["whitelist add %s" % player_name, "Ajout de %s dans la Whitelist" % player_name]
    elif action == "unwhitelist":
        command_strings = ["whitelist remove %s" % player_name, "Retrait de %s de la Whitelist" % player_name]
        run_minecraft_cmd("kick %s Le joueur n'est pas dans la whitelist" % player_name)
    elif action == "op":
        command_strings = ["op %s" % player_name, "Ajout de %s dans le groupe Operators" % player_name]
    elif action == "deop":
        command_strings = ["deop %s" % player_name, "Retrait de %s du groupe Operators" % player_name]
    else:
        log('tellraw @a {"text":"Commande non gérée( %s ).'
            + 'Abandon","italic":true,"color":"red"}' % action)
        return
    run_minecraft_cmd(command_strings[0])
    log('tellraw @a {"text":"%s (Raison : %s)","italic":true,"color":"gray"}' % (command_strings[1], reason))


def log(log_content):
        if TELLRAW_LOG:
            run_minecraft_cmd(log_content)


def mc_json_to_list(file):
    file_list = []
    with open(file, "r") as loadedfile:
        file_list_json = json.load(loadedfile)
    for name in file_list_json:
        file_list.append(name['name'].lower())
    return file_list


if __name__ == '__main__':
    # Get list from Sub Whitelist
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    request = requests.get(STREAM_WHITELIST_URL, headers=headers)
    if request.status_code == 200:
        result = request.json()

        old_whitelist = mc_json_to_list(WHITELIST_FILE)
        new_whitelist = []
        for name in result:
            new_whitelist.append(result[name]['whitelist_name'].lower())

        for player_name in new_whitelist: # Adding new players to whitelist
            if player_name not in old_whitelist:
                action("whitelist", player_name.capitalize(), "Ajout dans la SubWhitelist")

        for player_name in old_whitelist: # Removing old players from new whitelist
            if player_name not in new_whitelist:
                action("unwhitelist", player_name.capitalize(), "Le joueur n'est pas dans la SubWhitelist")

        old_oplist = mc_json_to_list(OPS_FILE)
        if GLOBAL_OP_PERMISSIONS:
            for player_name in new_whitelist:
                if player_name not in old_oplist \
                        and player_name not in EXCLUDED_OPS \
                        and player_name not in PRECONFIGURED_OP:
                    action("op", player_name.capitalize(), "Droits OP globaux")
                elif player_name in old_oplist and player_name in EXCLUDED_OPS:
                    action("deop", player_name.capitalize(), "Joueur exclu des permissions")

            for player_name in old_oplist:
                if player_name not in new_whitelist and player_name not in PRECONFIGURED_OP:
                    action("deop", player_name.capitalize(), "Le joueur n'est pas dans la Whitelist.")
        else:
            for player_name in old_oplist:
                if player_name not in PRECONFIGURED_OP:
                    action("deop", player_name.capitalize(), "Permissions globales inactives")
