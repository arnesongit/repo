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

import re

from koditidal2 import ArtistItem2, AlbumItem2, TrackItem2, VideoItem2, FolderItem2

from .config import settings
from .fuzzywuzzy import fuzz

#------------------------------------------------------------------------------
# Fuzzy Functions
#------------------------------------------------------------------------------

# Patterns to remove from Labels
PATTERNS = [ '\[COLOR \w+\]', '\[\/COLOR\]', '\[\/?B\]', '\[\/?I\]', '\[\/?LIGHT\]',
             '\[\/?UPPERCASE\]','\[\/?LOWERCASE\]', '\[\/?CAPITALIZE\]', '\[CR\]',
             '\(\s*Explicit\s*\)', '\(\s*Album Version\s*\)', '\(Stream locked\)', '\(Stream gesperrt\)',
              '\(?f(ea)?t\.?\s*\w+[\s\w]+\)?']

FOLDER_MASK = FolderItem2('','').FOLDER_MASK

def cleanupText(txt):
    resubs = [re.compile(pattern) for pattern in PATTERNS]
    for resub in resubs:
        txt = resub.sub('', txt)
    # Remove text with brackets
    #txt = re.sub('\[.*\]', '', txt)
    #txt = re.sub('\(.*\)', '', txt)
    #txt = txt.replace("whos", "who's")
    return txt


def initFuzzyLevel(item):
    item._matchLevel = 0
    item._blacklist = []
    item._blacklisted = False

def addFuzzyLevel(item, multiplier, searchField, resultField, checkBlacklist=True):
    level = fuzz.utils.intr(multiplier * fuzz.token_sort_ratio(searchField, cleanupText(resultField)))
    if checkBlacklist:
        # Check Blacklists
        blacklist1 = [word for word in settings.blacklist1 if word.lower() in resultField.lower() and not word.lower() in searchField.lower()]
        blacklist2 = [word for word in settings.blacklist2 if word.lower() in resultField.lower() and not word.lower() in searchField.lower()]
        blacklist3 = [word for word in settings.blacklist3 if word.lower() in resultField.lower() and not word.lower() in searchField.lower()]
        if blacklist1:
            level = fuzz.utils.intr(level * settings.blacklist1_percent / 100)
            item._blacklisted = item._blacklisted or settings.blacklist1_percent == 0.0
        if blacklist2:
            level = fuzz.utils.intr(level * settings.blacklist2_percent / 100)
            item._blacklisted = item._blacklisted or settings.blacklist2_percent == 0.0
        if blacklist3:
            level = fuzz.utils.intr(level * settings.blacklist3_percent / 100)
            item._blacklisted = item._blacklisted or settings.blacklist3_percent == 0.0
        item._blacklist += [word for word in blacklist1 if not word in item._blacklist]
        item._blacklist += [word for word in blacklist2 if not word in item._blacklist]
        item._blacklist += [word for word in blacklist3 if not word in item._blacklist]            
    item._matchLevel += level
    return level


#------------------------------------------------------------------------------
# Class FuzzyArtistItem
#------------------------------------------------------------------------------

class FuzzyArtistItem(ArtistItem2):

    _matchLevel = 0
    _blacklist = []
    _blacklisted = False

    def __init__(self, item):
        self.__dict__.update(vars(item))

    def getSortField(self, field='name'):
        if field == 'match':
            return self.getFuzzyLevel()
        return cleanupText(self.getLabel())

    def getComments(self):
        comments = [] # ArtistItem2.getComments(self)
        if self._matchLevel > 0:
            comments.append('MatchLevel:%s' % self.getFuzzyLevel())
        return comments

    def setFuzzyLevel(self, s_artist, level=-1):
        initFuzzyLevel(self)
        if level < 0:
            level = settings.fuzzy_artist_level
        addFuzzyLevel(self, level, s_artist.lower(), self.name.lower())
        if self._matchLevel < settings.artist_min_level:
            self._matchLevel = 0
            #self._blacklisted = True

    def getFuzzyLevel(self):
        return self._matchLevel

    def isBlacklisted(self):
        return self._blacklisted

#------------------------------------------------------------------------------
# Class FuzzyAlbumItem
#------------------------------------------------------------------------------

class FuzzyAlbumItem(AlbumItem2):

    _matchLevel = 0
    _blacklist = []
    _blacklisted = False

    def __init__(self, item):
        self.__dict__.update(vars(item))
        self.artist = FuzzyArtistItem(self.artist)
        self.artists = [FuzzyArtistItem(artist) for artist in self.artists]
        self._ftArtists = [FuzzyArtistItem(artist) for artist in self._ftArtists]

    def getSortField(self, field='name'):
        if field == 'match':
            return self.getFuzzyLevel()
        return cleanupText(self.getLabel())

    def getComments(self):
        comments = [] # AlbumItem2.getComments(self)
        if self._matchLevel > 0:
            comments.append('MatchLevel:%s' % self.getFuzzyLevel())            
        return comments

    def setFuzzyLevel(self, s_artist, s_album, s_albumartist, s_year):
        initFuzzyLevel(self)
        addFuzzyLevel(self, settings.fuzzy_album_level, s_album.lower(), self.title.lower())
        if s_year and self.year:
            # self.addFuzzyLevel(settings.fuzzy_album_year_level, '%s' % s_year, '%s' % self.year, checkBlacklist=False)
            try:
                intYear = int('0%s' % s_year)
                d = abs(intYear - self.year)
                if d < 10:
                    self._matchLevel += fuzz.utils.intr(settings.fuzzy_album_level * (100 - (d * 10)))  # 1 Year difference = 10%
            except:
                pass
        if self.artist:
            if s_albumartist:
                self.artist.setFuzzyLevel(s_albumartist, level=settings.fuzzy_album_artist_level)
            elif s_artist:
                self.artist.setFuzzyLevel(s_artist)

    def getFuzzyLevel(self):
        if self.artist:
            return self._matchLevel + self.artist._matchLevel
        return self._matchLevel

    def isBlacklisted(self):
        if self.artist:
            return self._blacklisted or self.artist._blacklisted
        return self._blacklisted

#------------------------------------------------------------------------------
# Class FuzzyTrackItem
#------------------------------------------------------------------------------

class FuzzyTrackItem(TrackItem2):

    _matchLevel = 0
    _blacklist = []
    _blacklisted = False

    def __init__(self, item):
        self.__dict__.update(vars(item))
        self.artist = FuzzyArtistItem(self.artist)
        self.artists = [FuzzyArtistItem(artist) for artist in self.artists]
        self._ftArtists = [FuzzyArtistItem(artist) for artist in self._ftArtists]
        self.album = FuzzyAlbumItem(self.album)

    def getSortField(self, field='name'):
        if field == 'match':
            return self.getFuzzyLevel()
        return cleanupText(self.getLabel())

    def getListItem(self):
        url, li, isFolder = TrackItem2.getListItem(self)
        li.setInfo('music', {'comment': ','.join(self.getComments()) })
        return (url, li, isFolder)

    def getComments(self):
        comments = [] # TrackItem2.getComments(self)
        if self._matchLevel > 0:
            comments.append('MatchLevel:%s' % self.getFuzzyLevel())
            if settings.debug:
                ftlevel = 0
                for item in self._ftArtists:
                    ftlevel += item.getFuzzyLevel()
                comments.append('ar:%s,t:%s,al:%s,aa:%s,ft:%s' % (self.artist.getFuzzyLevel(), self._matchLevel, self.album._matchLevel, self.album.artist.getFuzzyLevel(), ftlevel))
        return comments

    def setFuzzyLevel(self, s_artist, s_title, s_album, s_albumartist, s_ftartist, s_year):
        initFuzzyLevel(self)
        addFuzzyLevel(self, settings.fuzzy_title_level, s_title.lower(), self.title.lower())
        if self.artist:
            self.artist.setFuzzyLevel(s_artist)
        if s_ftartist and self._ftArtists:
            for item in self._ftArtists:
                item.setFuzzyLevel(s_ftartist)
        if self.album:
            self.album.setFuzzyLevel(s_artist, s_album, s_albumartist, s_year)

    def getFuzzyLevel(self):
        level = self._matchLevel
        if self.artist:
            level += self.artist.getFuzzyLevel()
        if self._ftArtists:
            for item in self._ftArtists:
                if item._matchLevel >= settings.artist_min_level and not item.isBlacklisted():
                    level += item.getFuzzyLevel()
        if self.album:
            level += self.album.getFuzzyLevel()
        return level

    def isBlacklisted(self):
        blacklisted = self._blacklisted
        if self.artist:
            blacklisted = blacklisted or self.artist.isBlacklisted()
        if self.album:
            blacklisted = blacklisted or self.album.isBlacklisted() or self.album.artist.isBlacklisted()
        return blacklisted

#------------------------------------------------------------------------------
# Class FuzzyVideoItem
#------------------------------------------------------------------------------

class FuzzyVideoItem(VideoItem2):

    _matchLevel = 0
    _blacklist = []
    _blacklisted = False

    def __init__(self, item):
        self.__dict__.update(vars(item))
        self.artist = FuzzyArtistItem(self.artist)
        self.artists = [FuzzyArtistItem(artist) for artist in self.artists]
        self._ftArtists = [FuzzyArtistItem(artist) for artist in self._ftArtists]

    def getSortField(self, field='name'):
        if field == 'match':
            return self.getFuzzyLevel()
        return cleanupText(self.getLabel())

    def getListItem(self):
        url, li, isFolder = VideoItem2.getListItem(self)
        li.setInfo('music', {'comment': ','.join(self.getComments()) })
        return (url, li, isFolder)

    def getComments(self):
        comments = [] # VideoItem2.getComments(self)
        if self._matchLevel > 0:
            comments.append('MatchLevel:%s' % self.getFuzzyLevel())            
        return comments

    def setFuzzyLevel(self, s_artist, s_title, s_year):
        initFuzzyLevel(self)
        addFuzzyLevel(self, settings.fuzzy_title_level, s_title.lower(), self.title.lower())
        if s_year and self.year:
            addFuzzyLevel(self, settings.fuzzy_album_year_level, '%s' % s_year, '%s' % self.year, checkBlacklist=False)
        if self.artist:
            self.artist.setFuzzyLevel(s_artist)

    def getFuzzyLevel(self):
        if self.artist:
            return self._matchLevel + self.artist._matchLevel
        return self._matchLevel

    def isBlacklisted(self):
        if self.artist:
            return self._blacklisted or self.artist._blacklisted
        return self._blacklisted

# End of File
