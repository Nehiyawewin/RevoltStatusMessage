# revolt_status: Set Revolt status as current song.
#
# Copyright (c) 2024 Nehiyawewin
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from quodlibet import _, app, print_e
from quodlibet.plugins import PluginConfig, ConfProp
from quodlibet.plugins.events import EventPlugin
from quodlibet.pattern import Pattern
from gi.repository import Gtk
import requests
import time

'''
    Big thanks to the QuodLibet docs, and github code.
    Also thank you to Aditi K <105543244+teeleafs@users.noreply.github.com> for their discord status plugin.
    It was very useful to figure out how to handle settings & format the plugin.
'''


# How the description will appear in Revolt
REVOLT_DESCRIPTION = "<artist> - <title>"

# Manually ask for the token (Until I replace with with revolt.py when aiohttp supports python 3.1x because I cant be bothered downgrading to python 3.8)
TOKEN = ""

# Revolt api url
url = "https://api.revolt.chat/users/@me"

# Setup our config
class RevoltStatusConfig:
    _config = PluginConfig(__name__)
    token = ConfProp(_config, "token", TOKEN)
    description = ConfProp(_config, "description", REVOLT_DESCRIPTION)

# Get config
revoltStatusConfig = RevoltStatusConfig()

# MAIN PLUGIN CLASS HERE
class RevoltStatusMessage(EventPlugin):
    PLUGIN_ID = _("Revolt status message")
    PLUGIN_NAME = _("Revolt Status Message")
    PLUGIN_DESC = _("Update your Revolt description to what you're listening to")
    VERSION = "1.0"

    def __init__(self):
        self.song = None

    def update_status(self, state, desc = None):
        # Make sure our token exists
        if (len(revoltStatusConfig.token) > 0):

            # Send our request to Revolt
            headers = {"Content-Type": "application/json", "X-Session-Token": revoltStatusConfig.token}
            payload = {"status": {"text": state + ": "+ desc}}
            response = requests.patch(url, json = payload, headers = headers)

    # Handles playback of music. Updates listening state.
    def handle_play(self):
        if self.song:
            state = _("Playing")
            desc = Pattern(revoltStatusConfig.description) % self.song
            self.update_status(state = state, desc = desc)

    # Handles pausing of music. Updates listening state.
    def handle_paused(self):
        state = _("Paused")
        desc = Pattern(revoltStatusConfig.description) % self.song
        self.update_status(state = state, desc = desc)

    # Handles unpausing of music.
    def handle_unpaused(self):
        if not self.song:
            self.song = app.player.song
        self.handle_play()

    # Called when a song starts
    def plugin_on_song_started(self, song):
        self.song = song
        if not app.player.paused:
            self.handle_play()

    # Called when a song ends
    def plugin_on_song_ended(self, song, stopped):
        pass

    def plugin_on_paused(self):
        self.handle_paused()

    def plugin_on_unpaused(self):
        self.handle_unpaused()

    # Called when the plugin is enabled
    def enabled(self):
        if app.player.paused:
            self.handle_paused()
        else:
            self.handle_unpaused()

    # Called when the plugin is disabled
    def disabled(self):
        self.song = None

    # Setup plugin settings
    def PluginPreferences(self, parent):
        vb = Gtk.VBox(spacing = 6)

        # Handle the changing of our token field
        def token_changed(entry):
            revoltStatusConfig.token = entry.get_text()
            if not app.player.paused:
                self.handle_play()

        # Handle the changing of our description field
        def description_changed(entry):
            revoltStatusConfig.description = entry.get_text()
            if not app.player.paused:
                self.handle_play()


        token_box = Gtk.HBox(spacing = 6)
        token_box.set_border_width(3)

        token_line = Gtk.Entry()
        token_line.set_text(revoltStatusConfig.token)
        token_line.connect("changed", token_changed)

        token_box.pack_start(Gtk.Label(label = _("Token")), False, True, 0)
        token_box.pack_start(token_line, True, True, 0)

        description_box = Gtk.HBox(spacing = 3)
        description_box.set_border_width(3)

        description_line = Gtk.Entry()
        description_line.set_text(revoltStatusConfig.description)
        description_line.connect("changed", description_changed)

        description_box.pack_start(Gtk.Label(label = _("Description")), False, True, 0)
        description_box.pack_start(description_line, True, True, 0)

        vb.pack_start(token_box, True, True, 0)
        vb.pack_start(description_box, True, True, 0)

        return vb
