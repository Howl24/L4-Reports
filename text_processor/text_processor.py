from nltk.corpus import stopwords
import codecs
import string
import re

from nltk.stem.snowball import SpanishStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

punctuations = '¡!"#$%&\'()*+,-⁻./:;<=>?[\\]^_`{|}~• ' #@ not included (@risk)
spanish_stemmer = SpanishStemmer()
stop_spanish = stopwords.words('spanish')
stop_english = stopwords.words('english')
special_characters_spanish = '[^a-zA-Z0-9áéíóúñ ]'


MIN_DF = 5

def preprocess(text):
  text = text.lower()
  text = re.sub(special_characters_spanish,' ', text) #remove punctuations
  text = remove_whitespaces(text)
  return text


def remove_numbers(text):
  return ''.join([char for char in text if not char.isdigit()])


def remove_punctuation(text):
  regex = re.compile('[%s]' % re.escape(string.punctuation))
  return regex.sub(' ',text)


def remove_whitespaces(text):
  return ' '.join(text.split())


def remove_stopwords(text):
  words = []
  for word in text.split():
    if word not in stop_spanish:
      words.append(word)

  new_text = ' '.join(words)
  return new_text


def stem(text):
  stem_words = []
  for word in text.split():
    word = spanish_stemmer.stem(word)
    stem_words.append(word)

  stem_text = ' '.join(stem_words)
  return stem_text


def process_text(text):
    """ Processing text:
        - Lower case
        - Remove whitespaces
    """

    text = text.lower()
    text = remove_whitespaces(text)
    return text

def get_terms(texts, configuration):
    """ Get terms according to the configuration options
        configuration:

    """

    vectorizer = CountVectorizer(stop_words=stop_spanish,
                                 ngram_range=configuration.ngrams)

    analyze = vectorizer.build_analyzer()

    all_terms = set()
    for text in texts:
        text_terms = analyze(text)
        for term in text_terms:
            all_terms.add(term)

    return all_terms


def build_vectorizer(configuration):
    vectorizer = TfidfVectorizer(stop_words=stop_spanish,
                                 ngram_range=configuration.ngrams,
                                 min_df=configuration.dfs[0])

    return vectorizer
