# -*- coding: utf-8 -*-
"""
Plex Movie Agent Mapper
"""
import os
import re
import logging
from pathlib import Path
import sqlite3
from plexmovieagentmapper import dbcopy
from plexmovieagentmapper import media


class PlexMovieAgentMapper:
    def __init__(self, plex_db=None, copy_db=True, debug=False):
        """

        :param plex_db:
        :param copy_db:
        """
        if not plex_db:
            raise ValueError("Database path is a required field")
        elif not os.path.isfile(plex_db):
            raise FileNotFoundError()

        self._debug = debug
        if self._debug:
            logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

        self._plex_db = plex_db
        self._copy_db = copy_db
        self._current_hash = {}
        self._imdb_hash, self._tmdb_hash, self._tvdb_hash, self._plex_hash, self._details_hash = self._generate_matching_hash()

    def get_imdb_from_plex_guid(self, plex_guid=None):
        """Returns an IMDB id for a given Plex GUID if a match is found.

        :param plex_guid:
        :return:
        """
        if self._plex_hash.get(plex_guid, None):
            return self._plex_hash[plex_guid]['imdb']
        return None

    def get_tmdb_from_plex_guid(self, plex_guid=None):
        """Returns a TMDB id for a given Plex GUID if a match is found.

        :param plex_guid:
        :return:
        """
        if self._plex_hash.get(plex_guid, None):
            return self._plex_hash[plex_guid]['tmdb']
        return None

    def get_tvdb_from_plex_guid(self, plex_guid=None):
        """Returns a TVDB id for a given Plex GUID if a match is found.

        :param plex_guid:
        :return:
        """
        if self._plex_hash.get(plex_guid, None):
            return self._plex_hash[plex_guid]['tvdb']
        return None

    def get_plex_guid_from_imdb(self, imdb_id=None):
        """Returns a Plex GUID for a given IMDB id if a match is found.

        :param imdb_id:
        :return:
        """
        if self._imdb_hash.get(imdb_id, None):
            return self._imdb_hash[imdb_id]
        return None

    def get_plex_guid_from_tmdb(self, tmdb_id=None):
        """Returns a Plex GUID for a given TMDB id if a match is found.

        :param tmdb_id:
        :return:
        """
        if self._tmdb_hash.get(tmdb_id, None):
            return self._tmdb_hash[tmdb_id]
        return None

    def get_plex_guid_from_tvdb(self, tvdb_id=None):
        """Returns a Plex GUID for a given TVDB id if a match is found.

        :param tvdb_id:
        :rtype: bool
        :return:
        """
        if self._tvdb_hash.get(tvdb_id, None):
            return self._tvdb_hash[tvdb_id]
        return None

    def plex_guid_available(self, plex_guid=None):
        """Check if a Plex GUID is in the hash

        :param plex_guid:
        :return:
        """
        return True if plex_guid and self._plex_hash.get(plex_guid, None) else False

    def get_details_from_imdb(self, library_id=None, imdb_id=None):
        """Get media item details for a given IMDB id.

        :param library_id:
        :param imdb_id:
        :return:
        """
        if imdb_id and self._imdb_hash.get(imdb_id, None):
            details = self._details_hash.get(self._imdb_hash[imdb_id])
            return details if not library_id or library_id in details.available_libraries else None
        return None

    def get_details_from_tmdb(self, library_id=None, tmdb_id=None):
        """Get media item details for a given TMDB id.

        :param library_id:
        :param tmdb_id:
        :return:
        """
        if tmdb_id and self._tmdb_hash.get(tmdb_id, None):
            details = self._details_hash.get(self._tmdb_hash[tmdb_id])
            return details if not library_id or library_id in details.available_libraries else None
        return None

    def get_details_from_tvdb(self, library_id=None, tvdb_id=None):
        """Get media item details for a given TVDB id.

        :param library_id:
        :param tvdb_id:
        :return:
        """
        if tvdb_id and self._tvdb_hash.get(tvdb_id, None):
            details = self._details_hash.get(self._tvdb_hash[tvdb_id])
            return details if not library_id or library_id in details.available_libraries else None
        return None

    def get_details_from_plex_guid(self, library_id=None, plex_guid=None):
        """Get media item details for a given Plex GUID.

        :param library_id:
        :param plex_guid:
        :return:
        """
        if plex_guid:
            details = self._details_hash.get(plex_guid, None)
            if details and library_id:
                details.filter_files(library_id)
                return details
        return None

    def _generate_matching_hash(self):
        """Generate a series of lookup hashes

        :return:
        """
        imdb_hash = {}
        tmdb_hash = {}
        tvdb_hash = {}
        plex_agent_hash = {}
        details_hash = {}

        if self._plex_db and os.path.isfile(self._plex_db):
            # Does the user want to copy the database?
            if self._copy_db:
                db_path = dbcopy.DbCopy(self._plex_db)
            else:
                db_path = Path(self._plex_db)

            with db_path as _db_path:
                if os.path.isfile(_db_path):
                    # Open a connection to the database
                    conn = sqlite3.connect(_db_path, timeout=10)
                    # Read each result as a row
                    conn.row_factory = sqlite3.Row
                    c = conn.cursor()

                    # Build a hash for Movies
                    movie_query = 'SELECT mdi.id as metadata_item_id, t.tag, mdi.guid, mdi.title, mdi.year, mi.library_section_id, GROUP_CONCAT(mp.file, \';\') as file_parts, ls.uuid ' \
                            'FROM metadata_items mdi ' \
                            'JOIN taggings tg ON tg.metadata_item_id = mdi.id ' \
                            'JOIN tags t ON t.id = tg.tag_id AND t.tag_type = 314 ' \
                            'JOIN media_items mi ON mi.metadata_item_id = mdi.id ' \
                            'JOIN media_parts mp ON mp.media_item_id = mi.id ' \
                            'JOIN library_sections ls ON ls.id = mdi.library_section_id ' \
                            'WHERE mdi.metadata_type = 1 ' \
                            'GROUP BY  mdi.guid, t.tag, mi.library_section_id'
                    for row in c.execute(movie_query):
                        row_id = None
                        row_type = None
                        if not row['guid'].startswith('com.plexapp.agents'):
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
                        else:
                            if row['guid'] and 'imdb://' in row['guid']:
                                if self._debug:
                                    logging.info(u"Matching ({}) for IMDB".format(row['guid']))

                                row_id = re.split(r'^((?:tt)?\d+)', row['guid'].split('imdb://')[1])[1]
                                row_type = 'imdb'
                                imdb_hash[row_id] = row['guid']
                            elif row['guid'] and 'themoviedb://' in row['guid']:
                                if self._debug:
                                    logging.info(u"Matching ({}) for TMDB".format(row['guid']))

                                row_id = re.split(r'^(\d+)', row['guid'].split('themoviedb://')[1])[1]
                                row_type = 'tmdb'
                                tmdb_hash[row_id] = row['guid']
                            elif row['guid'] and 'thetvdb://' in row['guid']:
                                if self._debug:
                                    logging.info(u"Matching ({}) for TVDB".format(row['guid']))

                                row_id = re.split(r'^(\d+)', row['guid'].split('thetvdb://')[1])[1]
                                row_type = 'tvdb'
                                tvdb_hash[row_id] = row['guid']
                            else:
                                if self._debug:
                                    logging.info(u"Agent not matched for Movie ({})".format(row['guid']))

                        if not plex_agent_hash.get(row['guid'], None) and row_id is not None and row_type is not None:
                            if self._debug:
                                logging.info(u"Finding media files for {} ({})".format(row['title'], row['year']))

                            plex_agent_hash[row['guid']] = {'imdb': None, 'tmdb': None, 'tvdb': None}
                            media_item = media.Media(row['guid'], row['title'], row['year'], 'video', row['metadata_item_id'], row['uuid'])
                            details_hash[row['guid']] = media_item

                        if plex_agent_hash.get(row['guid'], None):
                            details_hash[row['guid']].add_files(row['library_section_id'], row['file_parts'].split(';'))

                            plex_agent_hash[row['guid']][row_type] = row_id

                    # Add TV Series to the hash
                    tv_query = 'SELECT mdi.id as metadata_item_id, t.tag, mdi.guid, mdi.title, mdi.year, mdi.library_section_id, ls.uuid ' \
                               'FROM metadata_items mdi ' \
                               'JOIN library_sections ls ON ls.id = mdi.library_section_id ' \
                               'LEFT JOIN taggings tg ON tg.metadata_item_id = mdi.id ' \
                               'LEFT JOIN tags t ON t.id = tg.tag_id AND t.tag_type = 314 ' \
                               'WHERE mdi.metadata_type = 2 ' \
                               'GROUP BY  mdi.guid, t.tag, mdi.library_section_id'
                    c.execute(tv_query)
                    tv_series_results = c.fetchall()

                    for row in tv_series_results:
                        row_id = None
                        row_type = None
                        if not row['guid'].startswith('com.plexapp.agents'):
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
                        else:
                            if row['guid'] and 'imdb://' in row['guid']:
                                if self._debug:
                                    logging.info(u"Matching ({}) for IMDB".format(row['guid']))

                                row_id = re.split(r'^((?:tt)?\d+)', row['guid'].split('imdb://')[1])[1]
                                row_type = 'imdb'
                                imdb_hash[row_id] = row['guid']
                            elif row['guid'] and 'themoviedb://' in row['guid']:
                                if self._debug:
                                    logging.info(u"Matching ({}) for TMDB".format(row['guid']))

                                row_id = re.split(r'^(\d+)', row['guid'].split('themoviedb://')[1])[1]
                                row_type = 'tmdb'
                                tmdb_hash[row_id] = row['guid']
                            elif row['guid'] and 'thetvdb://' in row['guid']:
                                if self._debug:
                                    logging.info(u"Matching ({}) for TVDB".format(row['guid']))

                                row_id = re.split(r'^(\d+)', row['guid'].split('thetvdb://')[1])[1]
                                row_type = 'tvdb'
                                tvdb_hash[row_id] = row['guid']
                            else:
                                if self._debug:
                                    logging.info(u"Agent not matched TV series ({})".format(row['guid']))

                        if not plex_agent_hash.get(row['guid'], None) and row_id is not None and row_type is not None:
                            if self._debug:
                                logging.info(u"Finding media files for {} ({})".format(row['title'], row['year']))

                            plex_agent_hash[row['guid']] = {'imdb': None, 'tmdb': None, 'tvdb': None}
                            media_item = media.Media(row['guid'], row['title'], row['year'], 'video', row['metadata_item_id'], row['uuid'])
                            details_hash[row['guid']] = media_item
                            ep_cur = conn.cursor()
                            # We need to build an episode list
                            episode_query = 'SELECT GROUP_CONCAT(mp.file, \';\') as file_parts ' \
                                            'FROM metadata_items mdi_s ' \
                                            'JOIN metadata_items mdi_e ON mdi_e.parent_id = mdi_s.id ' \
                                            'JOIN media_items mi ON mi.metadata_item_id = mdi_e.id ' \
                                            'JOIN media_parts mp ON mp.media_item_id = mi.id ' \
                                            'WHERE mdi_s.parent_id =  ' + str(row['metadata_item_id'])

                            episodes = ep_cur.execute(episode_query)
                            ep_list = episodes.fetchone()['file_parts'].split(';')
                            details_hash[row['guid']].add_files(row['library_section_id'], ep_list)

                        if plex_agent_hash.get(row['guid'], None):
                            plex_agent_hash[row['guid']][row_type] = row_id

                    conn.close()

        return imdb_hash, tmdb_hash, tvdb_hash, plex_agent_hash, details_hash
