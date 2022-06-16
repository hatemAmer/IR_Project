from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from dateutil.parser import parse
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
import datefinder

stop_words = set(stopwords.words('english'))
punc = ['.', ',']


def tokenize(text):
    tokens = word_tokenize(text)
    filtered_tokens = [w for w in tokens if not w.lower() in stop_words and not w in punc]
    # print(filtered_tokens)
    lemmitized_tokens = lemmitize_tokens(filtered_tokens)
    stemmed_token = stem_tokens(lemmitized_tokens)
    return stemmed_token, extract_dates(text)

def stem_tokens(tokens):
    newToken = []
    ps = PorterStemmer()
    for w in tokens :
        if (ps.stem(w) != w):
            newToken.append(ps.stem(w))
        elif(WordNetLemmatizer().lemmatize(w, 'v') != w):
            newToken.append(WordNetLemmatizer().lemmatize(w, 'v'))
        elif(WordNetLemmatizer().lemmatize(w, 'a') != w):
            newToken.append(WordNetLemmatizer().lemmatize(w, 'a'))
        elif(WordNetLemmatizer().lemmatize(w, 'n') != w): 
            newToken.append(WordNetLemmatizer().lemmatize(w, 'n'))
        else :
            newToken.append(w)
    return newToken 

def lemmitize_tokens(tokens):
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(w) for w in tokens]

def extract_dates(lowerText):
    dates = []
    matches = datefinder.find_dates(lowerText)
    for match in matches:
       print(match)
       dates.append(str(match))
    return dates

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False