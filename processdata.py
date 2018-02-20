from typing import List

from collections import Counter
from pprint import PrettyPrinter

from lxml import etree
from lxml.etree import ElementTree, Element
from nltk import PorterStemmer

from anime import Anime
from animexmlparser import AnimeXMLParser
from utility import cleanText, removeStopWords


def printAnimeInfo(animes):
    for anime in animes:
        print("name:", anime.title)
        print("id:", anime.animeId)
        print("summary:", anime.summary)
        print("vintage:", anime.vintage)
        print("themes:", anime.themes)
        print("genres:", anime.genres)
        print("mediaType:", anime.mediaType)
        print("companies:", anime.companies)
        print("staff:", anime.staff)
        print("cast:", anime.cast)
        print()


def analysisAnimeSummaries(animes):
    pass


def main():
    rawDataFilePath = "./out/raw/rawanimedata.xml"

    # Parse the anime records
    with open(rawDataFilePath, mode="r", encoding="utf8") as rawDataFile:
        rawDataXMLTree: ElementTree = etree.parse(rawDataFile)

    # Create the list of anime objects
    animeXMLParser: AnimeXMLParser = AnimeXMLParser()
    animeElements: Element = rawDataXMLTree.getroot()

    animes: List = []
    for animeElement in animeElements:
        anime: Anime = animeXMLParser.parse(animeElement)
        animes.append(anime)

    ps = PorterStemmer()
    animeSummaryCounters = {}
    dbCounter = Counter()
    for i, anime in enumerate(animes):
        # print(i + 1, "of", len(animes))
        cleanedSummary = cleanText(anime.summary)
        summaryWordList = cleanedSummary.split()
        summaryWordList = removeStopWords(summaryWordList)
        summaryWordList = [ps.stem(word) for word in summaryWordList]
        dbCounter.update(summaryWordList)
        animeSummaryCounters[anime.animeId] = Counter(summaryWordList)

    pp = PrettyPrinter(indent=4)
    # pp.pprint(animeSummaryCounters)
    # print(type(list(animeSummaryCounters.values())[0]))

    filteredDBCounter = Counter({k: v for k, v in dbCounter.items() if v > 17})
    # print(filteredDBCounter)
    # print(len(filteredDBCounter))
    #
    # countOfCounts = Counter(dbCounter.values())
    # print(countOfCounts)

    # printAnimeInfo(animes)

    # Analysis
    themeCounter = Counter()
    genreCounter = Counter()
    yearsCounter = Counter()
    companyCounter = Counter()
    wordSummaryCounter = Counter()
    genreGroups = []
    animationStudioCounter = Counter()
    for anime in animes:
        themeCounter.update(anime.themes)
        genreCounter.update(anime.genres)
        genreGroups.append(tuple(sorted(anime.genres)))
        yearsCounter.update([anime.vintage[0:4]])
        companyCounter.update([company[1:] for company in anime.companies if company])
        wordSummaryCounter.update(anime.summary.lower().split())
        animationStudioCounter.update(
            [company[2] for company in anime.companies if company[0] == "Animation Production"]
        )

    print(animationStudioCounter)
    print(len(animationStudioCounter))
    print(Counter(list(animationStudioCounter.values())))
    # print(themeCounter)
    # print(len(themeCounter))
    # print(genreCounter)
    # print(len(genreCounter))

    #
    # genreGroupCounter = Counter(genreGroups)
    # print(genreGroupCounter)
    # print("Anime Count:", len(animes))
    # print("Theme Count:", len(themeCounter))
    # print("Themes:", list(themeCounter.keys()))
    # print("Genre Count:", len(genreCounter))
    # print("Genres:", list(genreCounter.keys()))
    # print(list(sorted(yearsCounter.keys())))
    # print(yearsCounter)
    # print("Companies Count:", len(companyCounter.keys()))
    # print("Companies:", companyCounter)
    # print([item for item in wordSummaryCounter.items() if 50 < item[1] < 100])

    # bloblist = [TextBlob(anime.summary.lower()) for anime in animes]
    # print(len(bloblist))
    #
    # scores = {}
    # for i, blob in enumerate(bloblist):
    #     print(i, "of", len(bloblist))
    #     scores = {word: tfidf(word, blob, bloblist) for word in blob.words}
    #     break
    #
    # sortedWords = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    # print(sortedWords)


if __name__ == '__main__':
    main()
