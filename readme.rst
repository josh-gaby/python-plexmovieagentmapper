Python - PlexMovieAgentMapper
=============================
With the new Plex Movie Agent not providing a way to search by IMDB/TMDB/TVDB I needed a way to map IMDB/TMDB/TVDB ids to plex guid values.

By default the Plex database is copied on initialization so that we aren't working on a live copy that Plex may be accessing, this behaviour can be disabled by setting `copy_db=False` when initializing PlexMovieAgentMapper, this is useful if you have downloaded a copy of the database using the plexapi downloadDatabases() function and don't want too have 2 temporary copies.

The plex_guid returned is **NOT** necessarily one of the new plex://move/XXXXXXXX guids, it is whatever agent guid that the library uses. If the agent being used is still the Plex Movie Agent (legacy) then this guid will be the old com.plexapp.agents.imdb://ttXXXXXXXX or com.plexapp.agents.themoviedb://XXXXXXXX format.


Requirements
------------
    * Python 3
    * Plex

Installation
------------

.. code-block:: bash

    python3 -m pip install git+https://github.com/josh-gaby/python-plexmovieagentmapper.git


Usage
-----
.. code-block:: python

    import plexmovieagentmapper
    # Path to your Plex library database
    plex_db_path = '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db'

    test_plex_guid = 'plex://movie/5d776834880197001ec93294'
    test_imdb_id = 'tt0113243'
    test_tmdb_id = '10428'
    test_tvdb_id = '4534'

    # Initialize the mapper with the required DB path
    plex_mapper = plexmovieagentmapper.mapper.PlexMovieAgentMapper(plex_db_path)

    print("Test retrieving external agent id from Plex guid:")
    # Retrieve an IMDB id from the Plex GUID
    imdb_id = plex_mapper.get_imdb_from_plex_guid(test_plex_guid)
    print(u"IMDB id from Plex guid {} -> {}".format(test_plex_guid, imdb_id))

    # Retrieve a TMDB id from the Plex GUID
    tmdb_id = plex_mapper.get_tmdb_from_plex_guid(test_plex_guid)
    print(u"TMDB id from Plex guid {} -> {}".format(test_plex_guid, tmdb_id))

    # Retrieve a TVDB id from the Plex GUID
    tvdb_id = plex_mapper.get_tvdb_from_plex_guid(test_plex_guid)
    print(u"TVDB id from Plex guid {} -> {}".format(test_plex_guid, tvdb_id))

    print("Test retrieving Plex guid from external agent ids:")
    # Retrieve Plex guid from an IMDB id
    plex_guid = plex_mapper.get_plex_guid_from_imdb(test_imdb_id)
    print(u"Plex guid from IMDB id {} -> {}".format(test_imdb_id, plex_guid))

    # Retrieve Plex guid from an TMDB id
    plex_guid = plex_mapper.get_plex_guid_from_tmdb(test_tmdb_id)
    print(u"Plex guid from TMDB id {} -> {}".format(test_tmdb_id, plex_guid))

    # Retrieve Plex guid from an TVDB id
    plex_guid = plex_mapper.get_plex_guid_from_tvdb(test_tvdb_id)
    print(u"Plex guid from TVDB id {} -> {}".format(test_tvdb_id, plex_guid))


A list of media files for an item can also be retrieved using the following functions:


.. code-block:: python

    imdb_details = plex_mapper.get_details_from_imdb(imdb_id=test_imdb_id)
    if imdb_details:
        for imdb_file in imdb_details.files():
            print(imdb_file.file)

    tmdb_details = plex_mapper.get_details_from_tmdb(tmdb_id=test_tmdb_id)
    if tmdb_details:
        for tmdb_file in tmdb_details.files():
            print(tmdb_file.file)

    tvdb_details = plex_mapper.get_details_from_tvdb(tvdb_id=test_tvdb_id)
    if tvdb_details:
        for tvdb_file in tvdb_details.files():
            print(tvdb_file.file)

    plex_details = plex_mapper.get_details_from_plex_guid(plex_guid=test_plex_guid)
    if plex_details:
        for plex_file in plex_details.files():
            print(plex_file.file)


**Important information about get details functions**

    - For a TV series these functions return a list of ALL episodes, they are not organised into seasons.
    - All of the `get_details_from_XXX` functions take a second parameter `library_id` if provided then media files will only be returned if they are available in that library.