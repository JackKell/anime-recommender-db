import re
from collections import Counter
from typing import List

import pandas
from lxml import etree
from lxml.etree import ElementTree, Element
from nltk import PorterStemmer
from pandas import DataFrame
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

from anime import Anime
from animexmlparser import AnimeXMLParser
from utility import cleanText, removeStopWords, intRound

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


def processVintage(vintage) -> str:
    vintageYear = vintage[:4]
    try:
        vintageYear = int(vintageYear)
        if vintageYear < 1970:
            return "Old"
        else:
            return str(intRound(vintageYear, base=5))
    except ValueError:
        return "NoYear"


def processGenres(genres: List[str]) -> str:
    processedGenres = []
    for genre in genres:
        processedGenre = genre.replace(" ", "__")
        processedGenres.append(processedGenre)
    return " ".join(processedGenres)


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

    indexes = [anime.animeId for anime in animes]
    titles = [anime.title for anime in animes]

    titleIdDF = DataFrame({"animeid": indexes, "title": titles})

    summaries = [processSummary(anime.summary) for anime in animes]
    maxFeatures = 60
    summaryVectorizer = TfidfVectorizer(norm="l2", max_features=maxFeatures, stop_words="english")
    x = summaryVectorizer.fit_transform(summaries)
    summariesDF = DataFrame(x.toarray(), columns=summaryVectorizer.get_feature_names())
    # print("Top", maxFeatures, "most important summary words")
    # print(top_mean_feats(x, summaryVectorizer.get_feature_names(), top_n=maxFeatures))

    themes = [processThemes(anime.themes) for anime in animes]
    maxFeatures = 30
    themeVectorizer = TfidfVectorizer(norm="l2", max_features=maxFeatures, stop_words="english")
    x = themeVectorizer.fit_transform(themes)
    themesDF = DataFrame(x.toarray(), columns=themeVectorizer.get_feature_names())
    # print("Top", maxFeatures, "most important themes")
    # print(top_mean_feats(x, themeVectorizer.get_feature_names(), top_n=maxFeatures))

    vintages = [processVintage(anime.vintage) for anime in animes]
    vintageVectorizer = CountVectorizer(stop_words="english", binary=True)
    x = vintageVectorizer.fit_transform(vintages)
    vintagesDF = DataFrame(x.toarray(), columns=vintageVectorizer.get_feature_names()).drop(["noyear"], axis=1)

    processedGenres = [processGenres(anime.genres) for anime in animes]
    genreVectorizer = CountVectorizer(stop_words="english", binary=True)
    x = genreVectorizer.fit_transform(processedGenres)
    genresDF = DataFrame(x.toarray(), columns=genreVectorizer.get_feature_names())

    featuresDF: DataFrame = pandas.concat([titleIdDF, summariesDF, themesDF, genresDF, vintagesDF], axis=1)
    featuresDF.set_index("animeid")
    # print(featuresDF)
    print(list(featuresDF))
    print(featuresDF.shape)

    featuresDF.to_csv("./out/processed/features.csv")

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
    #     themeCounter.update(processThemes(anime.themes))
    #     themeCounter.update([ps.stem(theme) for theme in anime.themes])
    #     genreCounter.update(anime.genres)
    #     genreGroups.append(tuple(sorted(anime.genres)))
    #     yearsCounter.update([processVintage(anime.vintage[0:4])])
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


if __name__ == '__main__':
    main()
