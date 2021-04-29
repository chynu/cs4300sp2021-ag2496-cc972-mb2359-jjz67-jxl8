from helper_functions import *

import json
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.corpus import stopwords
import gensim
import gensim.corpora as corpora
import spacy


class ArtistReviewAnalyzer:
    def __init__(self, fileloc, min_df=2, max_df=0.8):
        self.raw = ArtistReviewAnalyzer.load_json(fileloc)
        self.artists_list = list(self.raw.keys())
        # self.tfidf_vectorizer = TfidfVectorizer(analyzer='word', stop_words={'english'}, min_df=min_df, max_df=max_df)
        self.count_vectorizer = CountVectorizer(analyzer='word', stop_words={'english'}, min_df=min_df, max_df=max_df)
        self.__tokenizer = self.count_vectorizer.build_tokenizer()

        self.nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])  # Spacy tool

        self.tokenized_reviews = self.build_reviews_list(do_tokenize=True)  # List of lists of strings
        self.stop_words = self.build_stopwords()  # Stop words
        self.remove_stopwords()


        self.bigrams = None
        self.lemmatized_text = None
        self.lda_model = self.make_lda_model(num_topics=20)

        # self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.raw_reviews)
        # self.count_matrix = self.count_vectorizer.fit_transform(self.raw_reviews)
        # self.raw_reviews = self.build_reviews_list()  # List of strings

    def build_stopwords(self):
        sw = stopwords.words('english')
        sw.extend(['album', 'music', 'cd', 'track', 'song', 'sound'])
        return sw

    def update_stopwords(self, word_list):
        self.stop_words.extend(word_list)
        return None

    def remove_stopwords(self):
        self.tokenized_reviews = [[w for w in artist_review if w not in self.stop_words] for artist_review in self.tokenized_reviews]

    def make_bigrams(self):
        bg = gensim.models.Phrases(self.tokenized_reviews, min_count=5, threshold=100)
        bg_mod = gensim.models.phrases.Phraser(bg)
        return [bg_mod[d] for d in self.tokenized_reviews]

    def lemmatize(self, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
        texts_out = []
        for review_words in self.tokenized_reviews:
            joined_words = self.nlp(" ".join(review_words))
            texts_out.append([token.lemma_ for token in joined_words if token.pos_ in allowed_postags])
        return texts_out

    def make_lda_model(self, num_topics):
        self.bigrams = self.make_bigrams()
        self.lemmatized_text = self.lemmatize()
        id2word = corpora.Dictionary(self.lemmatized_text)
        corpus = [id2word.doc2bow(w) for w in self.lemmatized_text]
        return gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=id2word, num_topics=num_topics)

    def tokenize(self, input_string):
        return self.__tokenizer(input_string)

    def build_reviews_list(self, do_tokenize=False):
        consolidated_reviews = []
        for a in self.artists_list:
            if do_tokenize:
                consolidated_reviews.append(self.tokenize(clean_str(" ".join(self.raw[a]))))
            else:
                consolidated_reviews.append(clean_str(" ".join(self.raw[a])))
        return consolidated_reviews

    def get_all_words(self, do_tokenize=False):
        return self.tokenize(" ".join(self.raw_reviews)) if do_tokenize else " ".join(self.raw_reviews)

    @staticmethod
    def load_json(fileloc):
        with open(fileloc, 'r') as file:
            d = json.load(file)
            file.close()
        return d
