from nltk.stem.snowball import SpanishStemmer

stemmer = SpanishStemmer()


phrase = "dibujante"

for word in phrase.split():
    print(stemmer.stem(word))
