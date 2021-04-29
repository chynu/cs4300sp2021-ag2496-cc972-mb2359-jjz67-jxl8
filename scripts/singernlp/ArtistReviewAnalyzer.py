from helper_functions import *

import json
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.corpus import stopwords
import gensim
import gensim.corpora as corpora
import spacy
import itertools
import numpy as np


class ArtistReviewAnalyzer:
    """
    Analyzes artist reviews. Forms into useful data structures for NLP and topic modeling.
    """
    def __init__(self):
        # Basic data
        self.file_loc = None
        self.raw = None
        self.artists_list = None
        self.all_tokens = None

        # Stop-Words for tokenization
        self.stop_words = stopwords.words('english')  # Basic stop words
        self.update_stopwords(['album', 'music', 'cd', 'track', 'song', 'sound'])

        # Vectorizers
        self.tfidf_vectorizer = None
        self.count_vectorizer = None
        self.tfidf_matrix = None
        self.count_matrix = None
        self.__tokenizer = None
        self.tokenized_reviews = None

        # NLP tools
        self.lda_model = None
        self.bigrams = None
        self.lemmatized_text = None
        self.nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])  # Spacy tool


    def load_data(self, file_loc):
        """
        Loads reviews data (JSON file) into a dictionary.
        """
        # Save file location
        self.file_loc = file_loc

        with open(file_loc, 'r') as file:
            d = json.load(file)
            file.close()
        self.raw = d  # Save raw dictionary

        self.artists_list = list(self.raw.keys())  # Save artists list

        self.build_count_vectorizer(2, 0.8)  # Build count vec so we have a tokenizer

        # Handling tokenized list of reviews
        self.tokenized_reviews = self.__build_reviews_list(do_tokenize=True)
        self.remove_stopwords_from_tokenized_list()
        self.set_all_tokens()  # Get tokenized corpus

        return self.raw

    def refresh(self):
        self.build_count_vectorizer(2, 0.8)
        self.tokenized_reviews = self.__build_reviews_list(do_tokenize=True)
        self.remove_stopwords_from_tokenized_list()
        self.set_all_tokens()

    def build_count_vectorizer(self, min_df, max_df):
        if self.count_vectorizer is not None:
            print("WARNING: Count vectorizer has already been built.")
            return self.count_vectorizer
        self.count_vectorizer = CountVectorizer(analyzer='word', stop_words=self.stop_words, min_df=min_df, max_df=max_df)
        self.__tokenizer = self.count_vectorizer.build_tokenizer()
        return self.count_vectorizer

    def get_count_matrix(self):
        if self.count_vectorizer is None:
            return None

        if self.count_matrix is None:
            # TODO: self.raw is not truly reflective of the data since we clean it.
            self.count_matrix = self.count_vectorizer.fit_transform(self.all_tokens)
        return self.count_matrix

    def build_tfidf_vectorizer(self, min_df, max_df):
        self.tfidf_vectorizer = TfidfVectorizer(analyzer='word', stop_words=self.stop_words, min_df=min_df, max_df=max_df)
        return self.tfidf_vectorizer

    def get_tfidf_matrix(self):
        if self.tfidf_vectorizer is None:
            return None

        if self.tfidf_matrix is None:
            # TODO: self.raw is not truly reflective of the data since we clean it.
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.all_tokens)
        return self.tfidf_matrix

    def tokenize(self, input_string):
        if self.__tokenizer is None:
            print("WARNING: Tokenizer not set.")
            return None
        return self.__tokenizer(input_string)

    def update_stopwords(self, word_list):
        self.stop_words.extend(word_list)
        return None

    def remove_stopwords_from_tokenized_list(self):
        self.tokenized_reviews = \
            [[w for w in artist_review if w not in self.stop_words] for artist_review in self.tokenized_reviews]

    def build_lda_model(self, num_topics=20):
        self.bigrams = self.make_bigrams()
        self.lemmatized_text = self.lemmatize()
        id2word = corpora.Dictionary(self.lemmatized_text)
        corpus = [id2word.doc2bow(w) for w in self.lemmatized_text]
        self.lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=id2word, num_topics=num_topics)
        return self.lda_model

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

    def set_all_tokens(self):
        self.all_tokens = list(itertools.chain.from_iterable(self.tokenized_reviews))
        return self.all_tokens

    def get_all_tokens(self):
        return self.all_tokens

    def get_n_most_frequent_tuples(self, n):
        top_n = []
        feats = self.count_vectorizer.get_feature_names()
        w_counts = np.array(np.sum(self.get_count_matrix(), axis=0))[0]
        sorted_indices = np.argsort(w_counts)[::-1][:n]
        for i in sorted_indices:
            top_n.append((feats[i], w_counts[i]))
        return top_n

    def get_n_most_frequent(self, n):
        top_n = []
        feats = self.count_vectorizer.get_feature_names()
        w_counts = np.array(np.sum(self.get_count_matrix(), axis=0))[0]
        sorted_indices = np.argsort(w_counts)[::-1][:n]
        for i in sorted_indices:
            top_n.append(feats[i])
        return top_n

    def get_n_least_frequent(self, n):
        top_n = []
        feats = self.count_vectorizer.get_feature_names()
        w_counts = np.array(np.sum(self.get_count_matrix(), axis=0))[0]
        sorted_indices = np.argsort(w_counts)[:n]
        for i in sorted_indices:
            top_n.append(feats[i])
        return top_n

    def __build_reviews_list(self, do_tokenize=False):
        """
        Builds a list of reviews for each artist.
        returns {@list<string>} - list of all words used in a review for each artist
          or {@list<list<string>>} - list of token lists for reviews for each artist
        """
        consolidated_reviews = []
        for a in self.artists_list:
            if do_tokenize:
                consolidated_reviews.append(self.tokenize(clean_str(" ".join(self.raw[a]))))
            else:
                consolidated_reviews.append(clean_str(" ".join(self.raw[a])))
        return consolidated_reviews
