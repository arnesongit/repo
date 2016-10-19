# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Arne Svenson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import os
import xbmcaddon

#------------------------------------------------------------------------------
# Global Definitions
#------------------------------------------------------------------------------


USER_AGENTS = {
    'Windows IE':      'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
    'Windows Firefox': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
    'MacOS Firefox':   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:41.0) Gecko/20100101 Firefox/41.0',
    'MacOS Chrome':    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    'MacOS Safari':    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7',
    'iPad':            'Mozilla/5.0 (iPad; CPU OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
    'iPhone':          'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25',
    'Mobile':          'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36',
    'Android-App':     'TIDAL_ANDROID/679 okhttp/3.3.1'
    }

# Constants from appTidal.js
class CONST(object):
    addon_name = 'TIDAL Search'
    addon_id = 'context.item.tidal2'
    youtube_addon_id = 'plugin.video.youtube'

#------------------------------------------------------------------------------
# Configuration Class
#------------------------------------------------------------------------------

class Config(object):

    def __init__(self, addon):
        self.reload(addon)

    def reload(self, addon):
        # Addon Info
        self.addon_id = addon.getAddonInfo('id')
        self.addon_name = addon.getAddonInfo('name')
        self.addon_path = addon.getAddonInfo('path').decode('utf-8')
        self.addon_base_url = 'plugin://' + self.addon_id
        self.addon_fanart = os.path.join(self.addon_path, 'fanart.jpg').decode('utf-8')
        self.addon_icon = os.path.join(self.addon_path, 'icon.png').decode('utf-8')

        self.import_export_path = addon.getSetting('import_export_path').decode('utf-8')

        self.debug = True if addon.getSetting('debug') == 'true' else False
        self.debug_server = addon.getSetting('debug_server')
        self.log_details = int('0%s' % addon.getSetting('log_details'))

        # Blacklist Settings
        self.blacklist1 = addon.getSetting('blacklist1').split()
        self.blacklist2 = addon.getSetting('blacklist2').split()
        self.blacklist3 = addon.getSetting('blacklist3').split()
        self.blacklist1_brackets = True if addon.getSetting('blacklist1_brackets') == 'true' else False
        self.blacklist2_brackets = True if addon.getSetting('blacklist2_brackets') == 'true' else False
        self.blacklist3_brackets = True if addon.getSetting('blacklist3_brackets') == 'true' else False
        self.blacklist1_percent = float('0%s' % addon.getSetting('blacklist1_percent'))
        self.blacklist2_percent = float('0%s' % addon.getSetting('blacklist2_percent'))
        self.blacklist3_percent = float('0%s' % addon.getSetting('blacklist3_percent'))

        # Fuzzy-Settings
        self.artist_favorite_addition = float('0%s' % addon.getSetting('artist_favorite_addition'))
        self.artist_min_level = float('0%s' % addon.getSetting('artist_min_level'))
        self.fuzzy_artist_level = float('0%s' % addon.getSetting('fuzzy_artist_level'))
        self.fuzzy_title_level = float('0%s' % addon.getSetting('fuzzy_title_level'))
        self.fuzzy_album_level = float('0%s' % addon.getSetting('fuzzy_album_level'))
        self.fuzzy_album_artist_level = float('0%s' % addon.getSetting('fuzzy_album_artist_level'))
        self.fuzzy_album_year_level = float('0%s' % addon.getSetting('fuzzy_album_year_level'))

#------------------------------------------------------------------------------
# Configuration
#------------------------------------------------------------------------------

addon = xbmcaddon.Addon(CONST.addon_id)
settings = Config(addon)

def reloadConfig():
    settings.reload(addon)
    return settings

def getSetting(setting):
    return addon.getSetting(setting)

def setSetting(setting, value):
    addon.setSetting(setting, value)

def _S(txtid):
    try:
        txt = addon.getLocalizedString(txtid)
        return txt
    except:
        return '?: %s' % txtid

# End of File
