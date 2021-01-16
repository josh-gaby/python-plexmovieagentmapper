from plexmovieagentmapper import part
from plexmovieagentmapper import section

class Media(object):
    def __init__(self, guid=None, title=None, year=None, list_type=None, rating_key=None, uuid=None):
        self.guid = guid
        self.title = title
        self.year = year
        self.file_parts = []
        self.available_libraries = []
        self.listType = list_type
        self.ratingKey = rating_key
        self.library_uuid = uuid

    def __eq__(self, other):
        return other is not None and self.key == other.key

    def __hash__(self):
        return hash(repr(self))

    def __iter__(self):
        yield self

    def files(self):
        if self.file_parts:
            for part in self.file_parts:
                yield part

    def add_files(self, library_id=None, file_parts=None):
        if library_id:
            if file_parts:
                for part_path in file_parts:
                    if library_id not in self.available_libraries:
                        self.file_parts.append(part.Part(part_path, library_id))

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

    def section(self):
        return section.Section(self.library_uuid)
