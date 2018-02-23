import re
from typing import List

from lxml import etree
from lxml.etree import ElementTree, Element
from nltk import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer

from anime import Anime
from animexmlparser import AnimeXMLParser
from utility import cleanText, removeStopWords, top_mean_feats

ps = PorterStemmer()


def printAnimeInfo(animes: List[Anime]) -> None:
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


def processThemes(themes: List[str]) -> str:
    processedThemes = []
    for theme in themes:
        processedTheme: str = theme
        # Data Related rules
        processedTheme = processedTheme.replace("é", "e")

        if "school" in processedTheme or "college" in processedTheme:
            processedTheme = "school"
        # combine foxgirls, cat girls, dog girls, etc
        elif re.match("\w+ ?girls", processedTheme):
            processedTheme = "animal girl"
        # combine fanservice, fan service, and ecchi
        elif "fan" in processedTheme or "ecchi" in processedTheme:
            processedTheme = "fan service"
        # combine wizards/witches, wizards, witches
        elif "wizard" in processedTheme or "witch" in processedTheme:
            processedTheme = "witch"
        # combine superhero, superhumans
        elif "super" in processedTheme:
            processedTheme = "superpowers"

        categoryWords = ["love", "gothic", "robot", "space", "crime", "spirits", "racing", "magic"]
        for categoryWord in categoryWords:
            if categoryWord in processedTheme:
                processedTheme = categoryWord
                break
        processedTheme = processedTheme.replace(" ", "__")
        processedTheme = ps.stem(processedTheme)
        processedThemes.append(processedTheme)
    return " ".join(processedThemes)


def processSummary(summary) -> str:
    # print(i + 1, "of", len(animes))
    cleanedSummary = cleanText(summary)
    summaryWordList = cleanedSummary.split()
    summaryWordList = removeStopWords(summaryWordList)
    summaryWordList = [ps.stem(word) for word in summaryWordList]
    return " ".join(summaryWordList)


def main():
    rawDataFilePath: str = "./out/raw/rawanimedata.xml"
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

    summaries = [processSummary(anime.summary) for anime in animes]
    maxFeatures = 50
    summaryVectorizer = TfidfVectorizer(norm="l2", max_features=maxFeatures, stop_words="english")
    x = summaryVectorizer.fit_transform(summaries)
    print(type(x))
    print(top_mean_feats(x, summaryVectorizer.get_feature_names(), top_n=maxFeatures))

    themes = [processThemes(anime.themes) for anime in animes]
    maxFeatures = 50
    themeVectorizer = TfidfVectorizer(norm="l2", max_features=maxFeatures, stop_words="english")
    x = themeVectorizer.fit_transform(themes)
    print(type(x))
    print(top_mean_feats(x, themeVectorizer.get_feature_names(), top_n=maxFeatures))

    # pp = PrettyPrinter(indent=4)
    # pp.pprint(animeSummaryCounters)
    # print(type(list(animeSummaryCounters.values())[0]))

    # filteredDBCounter = Counter({k: v for k, v in dbCounter.items() if v > 17})
    # print(filteredDBCounter)
    # print(len(filteredDBCounter))
    #
    # countOfCounts = Counter(dbCounter.values())
    # print(countOfCounts)

    # printAnimeInfo(animes)

    # Analysis
    # themeCounter = Counter()
    # genreCounter = Counter()
    # yearsCounter = Counter()
    # companyCounter = Counter()
    # wordSummaryCounter = Counter()
    # genreGroups = []
    # animationStudioCounter = Counter()
    # for anime in animes:
    #     themeCounter.update(anime.themes)
    #     # themeCounter.update(processThemes(anime.themes))
    #     # themeCounter.update([ps.stem(theme) for theme in anime.themes])
    #     genreCounter.update(anime.genres)
    #     genreGroups.append(tuple(sorted(anime.genres)))
    #     yearsCounter.update([anime.vintage[0:4]])
    #     companyCounter.update([company[1:] for company in anime.companies if company])
    #     wordSummaryCounter.update(anime.summary.lower().split())
    #     animationStudioCounter.update(
    #         [company[2] for company in anime.companies if company[0] == "Animation Production"]
    #     )

    # print(animationStudioCounter)
    # print(len(animationStudioCounter))
    # print(Counter(list(animationStudioCounter.values())))
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
