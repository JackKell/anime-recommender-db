from lxml.etree import Element

from anime import Anime


class AnimeXMLParser(object):
    @staticmethod
    def parse(animeElement: Element):
        anime = Anime(
            animeId=AnimeXMLParser.parseId(animeElement),
            title=AnimeXMLParser.parseTitle(animeElement),
            mediaType=AnimeXMLParser.parseMediaType(animeElement),
            genres=AnimeXMLParser.parseGenres(animeElement),
            themes=AnimeXMLParser.parseThemes(animeElement),
            vintage=AnimeXMLParser.parseVintage(animeElement),
            summary=AnimeXMLParser.parseSummary(animeElement),
            cast=AnimeXMLParser.parseCast(animeElement),
            staff=AnimeXMLParser.parseStaff(animeElement),
            companies=AnimeXMLParser.parseCompany(animeElement),
            averageRating=AnimeXMLParser.parseAverageRating(animeElement),
            totalVotes=AnimeXMLParser.parseTotalVotes(animeElement)
        )
        return anime

    @staticmethod
    def __parseTypeAttFromInfoTag(animeElement: Element, typeAttribute: str):
        for infoNodes in animeElement.findall("info"):
            if infoNodes.get("type").lower() == typeAttribute:
                return infoNodes.text
        return ""

    @staticmethod
    def __parseTypeAttFromInfoTags(animeElement: Element, typeAttribute: str):
        attributes = []
        for infoNode in animeElement.findall("info"):
            if infoNode.get("type").lower() == typeAttribute:
                attributes.append(infoNode.text.lower())
        return attributes

    @staticmethod
    def parseId(animeElement: Element):
        return animeElement.get("id")

    @staticmethod
    def parseTitle(animeElement: Element):
        return animeElement.get("name")

    @staticmethod
    def parseSummary(animeElement: Element):
        summary = AnimeXMLParser.__parseTypeAttFromInfoTag(animeElement, "plot summary")
        summary = ' '.join(summary.split())
        return summary

    @staticmethod
    def parseGenres(animeElement: Element):
        return AnimeXMLParser.__parseTypeAttFromInfoTags(animeElement, "genres")

    @staticmethod
    def parseThemes(animeElement: Element):
        return AnimeXMLParser.__parseTypeAttFromInfoTags(animeElement, "themes")

    @staticmethod
    def parseCast(animeElement: Element):
        cast = []
        for creditNode in animeElement.findall("cast"):
            roleNode = creditNode.find("role")
            personNode = creditNode.find("person")
            cast.append((
                roleNode.text,
                personNode.get("id"),
                personNode.text
            ))
        return cast

    @staticmethod
    def parseStaff(animeElement: Element):
        staff = []
        for staffNode in animeElement.findall("staff"):
            taskNode = staffNode.find("task")
            personNode = staffNode.find("person")
            staff.append((
                taskNode.text,
                personNode.get("id"),
                personNode.text
            ))
        return staff

    @staticmethod
    def parseCompany(animeElement: Element):
        company = []
        for creditNode in animeElement.findall("credit"):
            taskNode = creditNode.find("task")
            companyNode = creditNode.find("company")
            company.append((
                taskNode.text,
                companyNode.get("id"),
                companyNode.text
            ))
        return company

    @staticmethod
    def parseMediaType(animeElement: Element):
        return animeElement.get("type")

    @staticmethod
    def parseVintage(animeElement: Element):
        return AnimeXMLParser.__parseTypeAttFromInfoTag(animeElement, "vintage")

    @staticmethod
    def parseAverageRating(animeElement: Element):
        ratingNode = animeElement.find("ratings")
        if ratingNode is not None:
            return ratingNode.get("weighted_score")
        return None

    @staticmethod
    def parseTotalVotes(animeElement: Element):
        ratingNode = animeElement.find("ratings")
        if ratingNode is not None:
            return ratingNode.get("nb_votes")
        return None
