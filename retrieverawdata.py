import time
from collections import namedtuple
from itertools import zip_longest
from typing import List

import requests
from lxml import etree
from lxml.etree import ElementTree, Element, XMLSyntaxError, XMLParser


def grouper(iterable, n):
    """Collect data into fixed-length chunks or blocks"""
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args)


def getAnimeInformation(animeIds: List[int], maxBatchSize: int = 50, waitTime: float = 1):
    utf8Parser: XMLParser = XMLParser(encoding="utf-8")
    totalBatches = len(animeIds) // maxBatchSize
    baseGetByTitleIdURL = "https://cdn.animenewsnetwork.com/encyclopedia/api.xml?title="

    elements = []
    problems = []

    for index, animeIdsBatch in enumerate(grouper(animeIds, maxBatchSize)):
        print(index + 1, "of", totalBatches)
        # Remove nones
        animeIdsBatch = [animeRecordId for animeRecordId in animeIdsBatch if animeRecordId]
        batchRequestURL = baseGetByTitleIdURL + "/".join(animeIdsBatch)
        request = requests.get(batchRequestURL)
        try:
            requestXMLString = request.content.decode(encoding="utf-8")
            requestXMLRoot = etree.fromstring(requestXMLString, utf8Parser)
            for element in requestXMLRoot:
                elements.append(element)
        except XMLSyntaxError:
            print("Error at", index + 1)
            for batchIndex, animeId in enumerate(animeIdsBatch):
                print(batchIndex, "of", maxBatchSize, "in batch", index)
                batchRequestURL = baseGetByTitleIdURL + str(animeId)
                request = requests.get(batchRequestURL)
                requestXMLString = request.content.decode(encoding="utf-8")
                try:
                    requestXMLRoot = etree.fromstring(requestXMLString, utf8Parser)
                    for element in requestXMLRoot:
                        elements.append(element)
                except XMLSyntaxError:
                    print("problem at", batchIndex, "of", maxBatchSize, "in batch", index)
                    problems.append(requestXMLString)
                    time.sleep(waitTime)
        time.sleep(waitTime)
    return elements, problems


def main():
    reportsFilePath = "./out/raw/reports.xml"

    # Parse the anime records
    with open(reportsFilePath, mode="r", encoding="utf8") as reportsFile:
        reportsXML: ElementTree = etree.parse(reportsFile)

    reportsRoot: Element = reportsXML.getroot()
    headers: list = ["id", "gid", "type", "name", "precision", "vintage"]

    AnimeRecord = namedtuple("AnimeRecord", headers)
    animeRecords: list = []

    # Read all of the anime records
    for animeElement in reportsRoot[1:]:
        currentAnimeRecord = AnimeRecord(
            id=animeElement.findtext("id"),
            gid=animeElement.findtext("gid"),
            type=animeElement.findtext("type"),
            name=animeElement.findtext("name"),
            precision=animeElement.findtext("precision"),
            vintage=animeElement.findtext("vintage")
        )
        animeRecords.append(currentAnimeRecord)

    # dataFrame = DataFrame(animeRecords, columns=headers)
    # print(dataFrame)

    root = etree.Element("animes")
    animeRecordIds = [animeRecord.id for animeRecord in animeRecords]
    animeXMLElements, problemResponses = getAnimeInformation(animeRecordIds)

    print(len(animeXMLElements))

    for animeXMLElement in animeXMLElements:
        root.append(animeXMLElement)

    myTree = etree.ElementTree(root)
    with open("./out/raw/rawanimedata.xml", "wb") as rawDataFile:
        rawDataFile.write(etree.tostring(myTree))


if __name__ == '__main__':
    main()
