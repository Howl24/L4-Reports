from nltk.corpus import stopwords

class Const:
	DONE = True
	FAIL = False
	EMPTY = None
	STOP_WORDS = stopwords.words('english') + stopwords.words('spanish')

def clear_spaces(text):
	text = " ".join(text.split())
	return text
	


