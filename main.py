import json
from enum import Enum

from datalist import DataList


class DictionaryEntry:

    def __init__(self, word, part_of_speech, definition, example=None):
        self.word = word
        self.part_of_speech = part_of_speech
        self.definition = definition
        self.example = example

    def __str__(self):
        string = "Word: {word}\n" \
                 "Part of speech: {part_of_speech}\n" \
                 "Definition: {definition}\n" \
                 "Example: {example}"
        return string.format(word=self.word,
                             part_of_speech=self.part_of_speech,
                             definition=self.definition,
                             example=self.example)


class LocalDictionary:

    def __init__(self, dictionary_json_name="dictionary.json"):
        self.dictionary = dict()
        try:
            with open(dictionary_json_name) as file:
                json_file = json.load(file)
                entries = json_file["entries"]
                for e in entries:
                    entry = json.loads(json.dumps(e), object_hook=self.decode)
                    if isinstance(entry, DictionaryEntry):
                        self.dictionary[str(entry.word)] = entry
        except FileNotFoundError:
            raise FileNotFoundError("File not found")

    @staticmethod
    def decode(o):
        try:
            return DictionaryEntry(**o)
        except KeyError:
            return o

    def search(self, word):
        try:
            return self.dictionary[word]
        except KeyError:
            raise KeyError("Word not found from Local")


class DictionaryEntryCache(DataList):

    def __init__(self, capacity=10):
        if capacity < 1:
            raise ValueError("Invalid capacity")
        super().__init__()
        self.size = 0
        self.capacity = capacity
        self.reset_current()

    def add(self, entry):
        if not isinstance(entry, DictionaryEntry):
            raise TypeError("Invalid type")
        if self.size == self.capacity:
            for x in range(self.size):
                if x == self.size - 1:
                    self.current.remove_after()
                    self.reset_current()
                    self.add_to_head(entry)
                self.iterate()
        else:
            self.size += 1
            self.add_to_head(entry)

    def search(self, word):
        found = None
        self.iterate()
        while self.current:
            if self.current.data.word == word:
                found = self.current.data
                break
            self.iterate()
        self.reset_current()

        if found:
            return found
        raise KeyError("Word not found from Cache")


class DictionarySource(Enum):
    LOCAL = 'LOCAL'
    CACHE = 'CACHE'

    def __str__(self):
        return 'Found in ' + self.name


class Dictionary:
    def __init__(self):
        self.localDictionary = LocalDictionary()
        self.cache = DictionaryEntryCache()

    def search(self, word):
        try:
            tuple_ = self.cache.search(word), DictionarySource.CACHE
        except KeyError:
            entry = self.localDictionary.search(word)
            self.cache.add(entry)
            tuple_ = entry, DictionarySource.LOCAL
        if tuple_:
            return tuple_
        return KeyError(f'Error when searching: {word}')


if __name__ == "__main__":
    dic = Dictionary()
    while True:
        try:
            searchWord = str(input('Enter a word to lookup: ')).lower()
            output = dic.search(searchWord)
            print('{}\n({})\n'.format(output[0], output[1]))
        except KeyError as error:
            print(error)
