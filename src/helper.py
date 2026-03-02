import json
import os
from rapidfuzz import fuzz

tags_path = os.path.join(os.path.dirname(__file__), 'data.json')

with open(tags_path, 'r') as f:
    tags = json.load(f)

def _save():
    # God I fucking love manually writing json syntax. I love fstrings I love fstrings why didn't I do yaml
    lines = ['[']
    for i, entry in enumerate(tags):
        comma = ',' if i < len(tags) - 1 else ''
        url = json.dumps(entry['url'])
        keywords = json.dumps(entry['keywords'])
        notes = json.dumps(entry['notes']) if 'notes' in entry else None

        lines.append(f'  {{')
        lines.append(f'    "url": {url},')
        if notes:
            lines.append(f'    "notes": {notes},')
        lines.append(f'    "keywords": {keywords}')
        lines.append(f'  }}{comma}')

    lines.append(']')

    with open(tags_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')

def addTag(url: str, keywords: list[str], notes_url: str = None):
    entry = {'url': url, 'keywords': keywords}
    if notes_url:
        entry['notes'] = [{'label': 'Additional Notes', 'url': notes_url}]
    tags.append(entry)
    _save()
    print(f"Tag for \"{url}\" added with keywords {keywords}")

def removeTag(keyword: str) -> bool:
    keyword = keyword.strip().lower()
    for i, entry in enumerate(tags):
        if keyword in entry['keywords']:
            tags.pop(i)
            _save()
            print(f"Tag for {keyword} removed.")
            return True
    return False

def getTag(search: str) -> dict | None:
    """Returns the best-matching entry dict, or None if no match found."""
    currKeyword = None
    currHighestSimilarity = 0
    currTag = None

    for tag in tags:
        for keyword in tag['keywords']:
            sim = fuzz.QRatio(keyword, search)
            if sim > currHighestSimilarity:
                currKeyword = keyword
                currHighestSimilarity = sim
                currTag = tag

    if currHighestSimilarity < 60 or currTag is None:
        return "No match found."

    print(f"Keyword '{search}' searched, found '{currKeyword}' - similarity: {currHighestSimilarity}")
    return currTag

"""
def getSearchKeywordHyperlink(search: str) -> str:
    currKeyword = None
    currHighestSimilarity = 0
    currUrl = None

    for tag in tags:
        for keyword in tag['keywords']:
            sim = fuzz.QRatio(search, keyword)
            if sim > currHighestSimilarity:
                currKeyword = keyword
                currHighestSimilarity = sim
                currUrl = tag['url']

    if currHighestSimilarity < 60 or currUrl is None:
        return "No match found."

    print(f"Keyword '{search}' searched, found '{currKeyword}' - similarity: {currHighestSimilarity}")
    return currUrl
"""
