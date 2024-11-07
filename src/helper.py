from data import imgs
from rapidfuzz import fuzz

def getSearchKeywordHyperlink(search: str) -> str:
    allKeywords = [ item for sublist in imgs.values() for item in sublist ]

    currKeyword = allKeywords[0]
    currHighestSimilarity = fuzz.QRatio(allKeywords[0], search)
    for keywordIndex in range(len(allKeywords)):
        sim = fuzz.QRatio(allKeywords[keywordIndex], search)
        if sim > currHighestSimilarity:
            currKeyword = allKeywords[keywordIndex]
            currHighestSimilarity = sim    

    if currHighestSimilarity < 67:
        return "No match found"

    for pair in imgs.items():
        if currKeyword in pair[1]:
            print(f"Keyword '{search}' searched, found '{currKeyword}' - similarity: {currHighestSimilarity}")
            return pair[0]

    return "No match found"
