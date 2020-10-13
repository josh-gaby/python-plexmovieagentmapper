# -*- coding: utf-8 -*-
"""Plex Movie Agent Mapper
"""
import os.path
import sqlite3


class PlexMovieAgentMapper:
    def __init__(self, plex_db=None):
        self._plex_db = plex_db
        self._current_hash = {}
        self._imdb_hash, self._tmdb_hash, self._tvdb_hash, self._plex_hash, self._details_hash = self.generate_matching_hash()

    def get_imdb_from_plex_guid(self, plex_guid=None):
        if self._plex_hash.get(plex_guid, None):
            return self._plex_hash[plex_guid]['imdb']
        return None

    def get_tmdb_from_plex_guid(self, plex_guid=None):
        if self._plex_hash.get(plex_guid, None):
            return self._plex_hash[plex_guid]['tmdb']
        return None

    def get_tvdb_from_plex_guid(self, plex_guid=None):
        if self._plex_hash.get(plex_guid, None):
            return self._plex_hash[plex_guid]['tvdb']
        return None

    def get_plex_guid_from_imdb(self, imdb_id=None):
        if self._imdb_hash.get(imdb_id, None):
            return self._imdb_hash[imdb_id]
        return None

    def get_plex_guid_from_tmdb(self, tmdb_id=None):
        if self._tmdb_hash.get(tmdb_id, None):
            return self._tmdb_hash[tmdb_id]
        return None

    def get_plex_guid_from_tvdb(self, tvdb_id=None):
        if self._tvdb_hash.get(tvdb_id, None):
            return self._tvdb_hash[tvdb_id]
        return None

    def plex_guid_available(self, plex_guid=None):
        return True if plex_guid and self._plex_hash.get(plex_guid, None) else False

    def get_details_from_imdb(self, library_id=None, imdb_id=None):
        if imdb_id and self._imdb_hash.get(imdb_id, None):
            details = self._details_hash.get(self._imdb_hash[imdb_id])
            return details if not library_id or library_id in details.available_libraries else None
        return None

    def get_details_from_tmdb(self, library_id=None, tmdb_id=None):
        if tmdb_id and self._tmdb_hash.get(tmdb_id, None):
            details = self._details_hash.get(self._tmdb_hash[tmdb_id])
            return details if not library_id or library_id in details.available_libraries else None
        return None

    def get_details_from_tvdb(self, library_id=None, tvdb_id=None):
        if tvdb_id and self._tmdb_hash.get(tvdb_id, None):
            details = self._details_hash.get(self._tvdb_hash[tvdb_id])
            return details if not library_id or library_id in details.available_libraries else None
        return None

    def get_details_from_plex_guid(self, library_id=None, plex_guid=None):
        if plex_guid:
            details = self._details_hash.get(plex_guid, None)
            if details and library_id:
                details.filter_files(library_id)
                return details
        return None

    def generate_matching_hash(self):
        imdb_hash = {}
        tmdb_hash = {}
        tvdb_hash = {}
        plex_agent_hash = {}
        details_hash = {}
        if self._plex_db and os.path.isfile(self._plex_db):
            # Open a connection to the database file in readonly mode
            conn = sqlite3.connect('file:'+self._plex_db+'?mode=ro', uri=True, timeout=10)
            # Read each result as a row
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            # Build our query
            query = 'SELECT t.tag, mdi.guid, mdi.title, mdi.year, mi.library_section_id, GROUP_CONCAT(mp.file, \';\') as file_parts ' \
                    'FROM metadata_items mdi ' \
                    'JOIN taggings tg ON tg.metadata_item_id = mdi.id ' \
                    'JOIN tags t ON t.id = tg.tag_id AND t.tag_type = 314 ' \
                    'JOIN media_items mi ON mi.metadata_item_id = mdi.id ' \
                    'JOIN media_parts mp ON mp.media_item_id = mi.id ' \
                    'WHERE mdi.metadata_type = 1 ' \
                    'GROUP BY  mdi.guid, t.tag, mi.library_section_id'
            for row in c.execute(query):
                row_id = None
                row_type = None
                if row['tag'] and 'imdb' in row['tag']:
                    row_id = row['tag'].split('imdb://')[1]
                    row_type = 'imdb'
                    imdb_hash[row_id] = row['guid']
                elif row['tag'] and 'tmdb' in row['tag']:
                    row_id = row['tag'].split('tmdb://')[1]
                    row_type = 'tmdb'
                    tmdb_hash[row_id] = row['guid']
                elif row['tag'] and 'tvdb' in row['tag']:
                    row_id = row['tag'].split('tvdb://')[1]
                    row_type = 'tvdb'
                    tvdb_hash[row_id] = row['guid']

                if not plex_agent_hash.get(row['guid'], None):
                    plex_agent_hash[row['guid']] = {'imdb': None, 'tmdb': None, 'tvdb': None}
                    media_item = Media(row['guid'], row['title'], row['year'])
                    details_hash[row['guid']] = media_item

                details_hash[row['guid']].add_files(row['library_section_id'], row['file_parts'].split(';'))

                plex_agent_hash[row['guid']][row_type] = row_id

            conn.close()

        return imdb_hash, tmdb_hash, tvdb_hash, plex_agent_hash, details_hash


class Media(object):
    def __init__(self, guid=None, title=None, year=None):
        self.guid = guid
        self.title = title
        self.year = year
        self.file_parts = []
        self.available_libraries = []

    def __eq__(self, other):
        return other is not None and self.key == other.key

    def __hash__(self):
        return hash(repr(self))

    def __iter__(self):
        yield self

    def iterParts(self):
        if self.file_parts:
            for part in self.file_parts:
                yield part

    def add_files(self, library_id=None, file_parts=None):
        if library_id:
            if file_parts:
                for part_path in file_parts:
                    if library_id not in self.available_libraries:
                        self.file_parts.append(Part(part_path, library_id))

            self.available_libraries.append(library_id)
            # Make it unique
            self.available_libraries = list(set(self.available_libraries))

    def filter_files(self, library_id=None):
        if library_id:
            tmp_file_parts = []
            for part in self.file_parts:
                if int(part.library_id) == int(library_id):
                    tmp_file_parts.append(part)

            self.file_parts = tmp_file_parts[:]


class Part(object):
    
    def __init__(self, file=None, library_id=None):
        self.file = file
        self.library_id = library_id
