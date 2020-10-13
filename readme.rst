Plex Movie Agent Mapper
=======================
With the new Plex Movie Agent not supporting search by IMDB/TMDB/TVDB anymore I needed a new way of accessing the API to map between the new Plex Movie Agent guids and IMDB/TMDB/TVDB ids.

**Important:**
--------------
The plex_guid being used is **NOT** necessarily one of the new plex://move/XXXXXXXX guids, it is whatever agent guid that the library uses. If the agent being used is still the Plex Movie Agent (legacy) then this guid will be the old com.plexapp.agents.imdb://ttXXXXXXXX or com.plexapp.agents.themoviedb://XXXXXXXX format

Usage
-----
.. code-block:: python

    import plexmovieagentmapper

    plex_db_path = 'PATH TO YOUR PLEX DB'

    test_plex_guid = 'plex://movie/5d776834880197001ec93294'
    test_imdb_id = 'tt0113243'
    test_tmdb_id = '10428'
    test_tvdb_id = '4534'

    # Initialize the mapper with the required DB path
    plex_mapper = plexmovieagentmapper.mapper.PlexMovieAgentMapper(plex_db_path)

    # Retrieve an IMDB id from the Plex GUID
    imdb_id = plex_mapper.get_imdb_from_plex_guid(test_plex_guid)          # imdb_id will equal tt0113243

    # Retrieve a TMDB id from the Plex GUID
    tmdb_id = plex_mapper.get_tmdb_from_plex_guid(test_plex_guid)          # tmdb_id will now equal 10428

    # Retrieve a TVDB id from the Plex GUID
    tvdb_id = plex_mapper.get_tvdb_from_plex_guid(test_plex_guid)          # tvdb_id will now equal 4534

    # Retrieve Plex guid from an IMDB id
    plex_guid = plex_mapper.get_plex_guid_from_imdb(test_imdb_id)  # plex_guid will now equal plex://movie/5d776834880197001ec93294

    # Retrieve Plex guid from an TMDB id
    # plex_guid = plex_mapper.get_plex_guid_from_imdb(test_tmdb_id)  # plex_guid will now equal plex://movie/5d776834880197001ec93294

    # Retrieve Plex guid from an TVDB id
    # plex_guid = plex_mapper.get_plex_guid_from_tvdb(test_imdb_id)  # plex_guid will now equal plex://movie/5d776834880197001ec93294