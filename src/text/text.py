import pathlib
import random

class Text:
    def getRandomText(self) -> str:
        filePointer = open('%s/dictionary/adjectives.txt' % pathlib.Path().resolve(), 'r')
        adjectives = filePointer.read()
        filePointer.close()

        filePointer = open('%s/dictionary/nouns.txt' % pathlib.Path().resolve(), 'r')
        nouns = filePointer.read()
        filePointer.close()

        adjectives = adjectives.split('\n')
        nouns = nouns.split('\n')

        return '%s %s' % (random.choice(adjectives), random.choice(nouns))
