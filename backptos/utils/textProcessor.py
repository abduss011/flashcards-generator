import re
from typing import List,Dict

def processText(text : str) -> str :
    if not text or not text.strip() : 
        raise ValueError("Text cannot be empty")
    text = basicCleaning(text)
    text = normalize(text)
    text = removeNoise(text)
    text = fixErrors(text)

    return text

def basicCleaning(text : str) -> str: 
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = text.replace('\t', ' ')

    return text

def normalize(text : str) -> str: 
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    return text.strip()

def removeNoise(text : str) -> str:
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text) #URL brutally mogs
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text) #emails sub5
    text = re.sub(r'(?:Страница|Page)\s+\d+', '', text, flags=re.IGNORECASE) #page sub3

    return text

def fixErrors(text : str) -> str:
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])([А-Яа-яA-Za-z])', r'\1 \2', text)
    text = text.replace('«', '"').replace('»', '"')

    return text

def analyzeText(text : str) -> Dict[str,any] : 
    words = text.split()
    sentences = splitIntoSentences(text)

    return {
        'charCount' : len(text),
        'wordCount' : len(words) ,
        'sentenceCount' : len(sentences),
        'avgWordLen' : sum(len(w) for w in words) / len(words) if words else 0,
        'avgSentenceLen' : len(words) / len(sentences) if sentences else 0,
        'paragraphs' : len(text.split('\n\n'))
    }

def splitIntoSentences(text : str) -> List[str] : 
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences

def splitIntoParagraphs(text : str) -> List[str] : 
    paragraphs = text.split('\n\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    return paragraphs

def extractKeyPhrases(text : str , topN : int = 10) -> List[str] : 
    stopWords = {
        'это', 'быть', 'в', 'на', 'с', 'по', 'для', 'от', 'к', 'и',
        'а', 'но', 'или', 'что', 'как', 'так', 'вот', 'же', 'то',
        'the', 'is', 'in', 'on', 'at', 'for', 'and', 'or', 'but', 'a'
    }
    words = re.findall(r'\b[а-яёА-ЯЁa-zA-Z]{4,}\b', text.lower())
    filteredWords = [w for w in words if w not in stopWords]

    from collections import Counter
    wordFreq = Counter(filteredWords)

    return [word for word, _ in wordFreq.most_common(topN)]

def summarizeText(text : str , maxLen : int = 500) -> str : 
    sentences = splitIntoSentences(text)

    summary = ""
    for sentence in sentences: 
        if len(summary) + len(sentence) <= maxLen : 
            summary += sentence + ". "
        else : 
            break

    return summary.strip()


def validateTextForCards(text : str) -> tuple[bool,str]: 
    if not text or not text.strip() :
        return False , "Text is empty"
    if len(text.strip()) < 50 : 
        return False , "Text is too short (minimum 50 symbols)"
    
    wordCount = len(text.split())
    if wordCount < 10 :
        return False , "Text does not have enough words"
    
    sentences = splitIntoSentences(text)
    if len(sentences) < 2 : 
        return False , "Text must contain minimum 2 sentences"
    
    return True ,  ""