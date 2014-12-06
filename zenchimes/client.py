#!/usr/bin/env python

import errno
import json
import os
import os.path
import requests
import socket
import sqlite3
import string
import sys
import time
import urllib
from zenchimes.utilities import logged_class
from zenchimes import settings


@logged_class
class LMSCommandLineInterface(object):
    bufsize = 2048

    def __init__(self, *args, **kwargs):
        """
        Initialize controller.
        """
        self.logger.debug("Initializing")
        self.error = False

        req = requests.get('http://localhost:3031/config')
        config = json.loads(req.text)
        player = config.get('player', None) # TODO: handle this case
        self.LMS_CHIME_PATH = player.get('lms_chime_path', None)
        self.LMS_HOSTNAME = player.get('lms_hostname', None)
        self.LMS_PORT = int(player.get('lms_port', None))
        self.MIXER_VOLUME = player.get('mixer_volume', None)

        self.logger.debug("LMS_HOSTNAME: {0}".format(self.LMS_HOSTNAME))
        self.logger.debug("LMS_PORT: {0}".format(self.LMS_PORT))
        self.logger.debug("LMS_CHIME_PATH: {0}".format(self.LMS_CHIME_PATH))
        self.logger.debug("MIXER_VOLUME: {0}".format(self.MIXER_VOLUME))

        # Quick and dirty error catch-all.
        req = requests.get("http://localhost:3031/chimes")
        chimes = json.loads(req.text)

        for chime in chimes:
            if not chime.get('is_active', False):
                continue

            # XXX: This is the new way to fetch the active chime data.
            self.chime_name = chime.get('description', None)
            self.chime_filename = "{0}/{1}".format(self.LMS_CHIME_PATH,
                    chime.get('filename', ''))
            self.logger.debug("chime_filename: {0}".format(
                self.chime_filename))

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.logger.debug("Socket connected?")
            self.s.connect((self.LMS_HOSTNAME, self.LMS_PORT))
        except socket.error as e:
            self.error = True
            self.logger.error("Unable to connect: {0}:{1} - {2}".format(
                self.LMS_HOSTNAME, self.LMS_PORT, e.strerror))
            return
        except Exception as e:
            self.error = True
            self.logger.error("Unknown error: {0}".format("crap"))
            return

        self.logger.info("LMS Connected?")
        self.get_players_initial_state()

    def __del__(self):
        """
        Destructor. Exit LMS CLI.
        """
        try:
            self.s.send('exit\n')
            self.s.recv(self.bufsize)
            self.s.close()
        except socket.error as e:
            self.logger.error("Unable to close socket: {0}".format(e.strerror))
        except AttributeError as e:
            self.logger.warning("Destructor socket not connected: {0}".format(
                e.strerror))

    def send_command(self, command):
        """
        Send the command to LMS CLI and return response.
        """
        self.s.send('{0}\n'.format(command))
        data = self.s.recv(self.bufsize)
        data = data.lstrip().rstrip()
        return data

    def get_players_initial_state(self):
        """
        Assembles a data structure with all of each player's parameters. We
        will need this later to restore initial state.
        """
        self.players_initial_state = {}
        current_player = None
        data = self.send_command('players 0')[11:]
        data = data.split(' ')
        p_count = urllib.unquote(data[0])
        data = data[1:]
        count = int(p_count.split(':')[1])
        self.players_initial_state['count'] = count
        key_list_boolean = ['canpoweroff', 'connected', 'isplayer']
        key_list_integer = ['playerindex']
        for kv in data:
            # Some kv contain multiple ':' and will result in a ValueError in
            # the try block.
            try:
                key, value = urllib.unquote(kv).split(':')
            except ValueError:
                # The only known exception is the MAC address. If the player
                # name contains a ':' then it will also be reassembled here.
                tmp = urllib.unquote(kv).split(':')
                key = tmp[0]
                value = string.join(tmp[1:], ':')

            if key == 'playerindex':
                self.players_initial_state[value] = {}
                current_player = self.players_initial_state[value]
            else:
                if key in key_list_boolean:
                    value = True if value else False
                if key in key_list_integer:
                    value = int(value)
                current_player[key] = value

        # Now fetch initial mixer volume
        for playerindex in range(count):
            current_player = self.players_initial_state[str(playerindex)]
            playerid = current_player['playerid']
            command = '{0} status'.format(playerid)
            data = self.send_command(command)
            data = data[len(command):].lstrip().rstrip().split(' ')

            # XXX: Ugh, yes there is a space in 'mixer volume'
            key_list = ['sync_master', 'mixer volume', 'mode', 'power']
            for kv in data:
                # Some kv contain multiple ':' and will result in a ValueError
                # in the try block.
                try:
                    key, value = urllib.unquote(kv).split(':')
                except ValueError:
                    # The only known exception is the MAC address. If the
                    # player name contains a ':' then it will also be
                    # reassembled here.
                    tmp = urllib.unquote(kv).split(':')
                    key = tmp[0]
                    value = string.join(tmp[1:], ':')
                if key in key_list:
                    if key == 'sync_master':
                        self.players_initial_state['sync_master'] = value
                    elif key == 'power':
                        if value == '1':
                            current_player[key] = True
                        else:
                            current_player[key] = False
                    else:
                        current_player[key] = value

        self.logger.debug("Initial State: {0}".format(self.players_initial_state))

    def restore_players_initial_state(self):
        """
        Restore specific player parameters such as volume and power.
        """
        for playerindex in range(self.players_initial_state['count']):
            playerid = self.players_initial_state[str(playerindex)]['playerid']
            initial_volume = \
                self.players_initial_state[str(playerindex)]['mixer volume']
            command = '{0} mixer volume {1}'.format(
                    urllib.quote(playerid),
                    initial_volume)
            self.send_command(command)

            # Restore power state.
            initial_power_state = \
                self.players_initial_state[str(playerindex)]['power']
            if initial_power_state:
                initial_power_state = 1
            else:
                initial_power_state = 0
            command = '{0} power {1}'.format(playerid, initial_power_state)
            #print command
            self.send_command(command)

    def set_mixer_volume(self, volume):
        """
        Set mixer volume.
        """
        for playerindex in range(self.players_initial_state['count']):
            playerid = self.players_initial_state[str(playerindex)]['playerid']
            command = '{0} mixer volume {1}'.format(
                    urllib.quote(playerid), volume)
            self.send_command(command)

    def power_on(self):
        """
        Power on all players. Kind of a hack for now cuz I'm in a hurry for POC.
        """
        for playerindex in range(self.players_initial_state['count']):
            playerid = self.players_initial_state[str(playerindex)]['playerid']
            command = '{0} power {1}'.format(
                    urllib.quote(playerid), 1)
            self.send_command(command)

    def play_chime(self):
        """
        Play the chime.
        """

        # Fetch the current value of chime_enabled.
        req = requests.get('http://localhost:3031/config/chime_enabled')
        config = json.loads(req.text)

        # Implicit conversion to boolean. Continue with chime only if currently
        # enabled.
        if config.get("value", "True") == "True":
            return

        playerid = self.players_initial_state['sync_master']
        sync_master_mode = 'play'
        for playerindex in range(self.players_initial_state['count']):
            if self.players_initial_state[str(playerindex)]['playerid'] \
                    == playerid:
                sync_master_mode = \
                    self.players_initial_state[str(playerindex)]['mode']
        command = '{0} playlist play {1} {2}'.format(
                urllib.quote(playerid), urllib.quote(self.chime_filename),
                    urllib.quote(self.chime_name))

        # Play chime only if idle
        # TODO: Consolidate restrictions like mode and quiet time in one place.
        if sync_master_mode != 'play':
            self.power_on()
            # Give it a moment to settle.
            time.sleep(1)
            self.set_mixer_volume(self.MIXER_VOLUME)
            self.send_command(command)
            time.sleep(self.get_duration() + 3)
            self.restore_players_initial_state()

    def get_duration(self):
        """
        Check duration of play for post play sleep prior to restore state.
        """
        playerid = self.players_initial_state['sync_master']
        command = '{0} duration ?'.format(playerid)
        duration = self.send_command(command).split(' ')[-1]
        return float(duration)

    def sync_players(self):
        """
        Sync the players.
        """


def main():
    sbcli = LMSCommandLineInterface()
    print sbcli.players_initial_state
    sys.exit(0)

if __name__ == '__main__':
    DEBUG = True
    main()
