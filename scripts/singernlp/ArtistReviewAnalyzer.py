import gensim
import gensim.corpora as corpora
import gensim.models.ldamodel as lda
import itertools
import json
from nltk.corpus import stopwords
import numpy as np
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import spacy
import unidecode as ud


class ArtistReviewAnalyzer:
    """
    Analyzes artist reviews. Forms into useful data structures for NLP and topic modeling.
    """
    def __init__(self):
        # Basic data
        self.raw_dict = None
        self.artists_list = None
        self.all_tokens = None

        # NLP tools
        self.string_tokenizer = None
        self.lda_model = None
        self.bigrams = None
        self.lemmatized_text = None
        self.nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])  # Spacy tool

        # Vectorizers
        self.tfidf_vectorizer = None
        self.count_vectorizer = None
        self.tfidf_matrix = None
        self.count_matrix = None
        self.tokenized_reviews = None

        # Stop-Words for tokenization
        self.stop_words = stopwords.words('english')  # Basic stop words
        self.update_stopwords(['album', 'music', 'cd', 'track', 'song', 'sound'])

    # === INITIALIZATION FUNCTIONS
    def build(self, file_loc, more_stopwords=None, min_df=2, max_df=0.8):
        self.load_data(file_loc)
        if more_stopwords is not None:
            self.update_stopwords(more_stopwords)
        self.init_vectorizers(min_df=min_df, max_df=max_df)
        self.update_tokenized_corpus()
        self.update_matricies()
        return self

    def load_data(self, file_loc):
        """
        Loads reviews data (JSON file) into a dictionary.
        """
        with open(file_loc, 'r') as file:
            d = json.load(file)
            file.close()
        self.raw_dict = d  # Save raw dictionary
        self.artists_list = list(self.raw_dict.keys())  # Save artists list
        return self.raw_dict

    def update_stopwords(self, word_list):
        self.stop_words.extend(word_list)
        self.stop_words = list(set(self.super_tokenize(" ".join(self.stop_words))))
        return None

    def init_vectorizers(self, min_df=2, max_df=0.8):
        """ Create Count and Tfidf vectorizer objects. """
        self.build_count_vectorizer(min_df, max_df)
        self.build_tfidf_vectorizer(min_df, max_df)

    def update_tokenized_corpus(self):
        # Create necessary tokenizer functions, etc.
        self.tokenized_reviews = self.tokenize_documents(self.raw_dict)
        self.all_tokens = list(itertools.chain.from_iterable(self.tokenized_reviews))  # Update the all_tokens var

    def build_count_vectorizer(self, min_df, max_df):
        """ Creates and returns CountVectorizer object. Depends on stop_words. """
        self.count_vectorizer = \
            CountVectorizer(analyzer='word', stop_words=self.stop_words, min_df=min_df, max_df=max_df)
        return self.count_vectorizer

    def build_tfidf_vectorizer(self, min_df, max_df):
        """ Creates and returns TfidfVectorizer object. Depends on stop_words. """
        self.tfidf_vectorizer = \
            TfidfVectorizer(analyzer='word', stop_words=self.stop_words, min_df=min_df, max_df=max_df)
        return self.tfidf_vectorizer

    def update_matricies(self):
        self.get_count_matrix()
        self.get_tfidf_matrix()

    def get_count_matrix(self):
        """ Creates and returns TF matrix. Depends on tokenized corpus. """
        if self.count_matrix is None and self.count_vectorizer is not None:
            self.count_matrix = self.count_vectorizer.fit_transform(self.all_tokens)
        return self.count_matrix

    def get_tfidf_matrix(self):
        """ Creates and returns TFIDF matrix. Depends on tokenized corpus. """
        if self.tfidf_matrix is None and self.tfidf_vectorizer is not None:
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.all_tokens)
        return self.tfidf_matrix

    def build_lda_model(self, num_topics=20):
        id2word = corpora.Dictionary(self.tokenized_reviews)
        corpus = [id2word.doc2bow(w) for w in self.tokenized_reviews]
        self.lda_model = lda.LdaModel(corpus=corpus,
                                      id2word=id2word,
                                      num_topics=num_topics,
                                      update_every=1,
                                      chunksize=len(corpus),
                                      passes=20,
                                      alpha='auto',
                                      random_state=42)
        return self.lda_model

    # ===== HELPER FUNCTIONS
    def tokenize_documents(self, input_dict):
        """
        Builds a list of lemmatized tokens.
        returns {@list<string>} - list of all words used in a review for each artist
          or {@list<list<string>>} - list of token lists for reviews for each artist
        """
        tokenized_documents = []
        for a in input_dict:
            reviews_list = input_dict[a]
            tokenized_documents.append(self.super_tokenize(" ".join(reviews_list)))
        return tokenized_documents

    def super_tokenize(self, input_string, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
        """
        Creates a list of tokens that are lemmatized, unicode-friendly, and stopword-free.
        Takes in a string and returns a list of strings.
        """
        # Cleaned and lowercase-ized
        cleaned_bunch_of_words = ArtistReviewAnalyzer.clean(input_string)
        nlp = self.nlp(cleaned_bunch_of_words)
        return [token.lemma_ for token in nlp
                if (token.pos_ in allowed_postags and
                    token.lower_ not in self.stop_words and
                    token.lemma_ not in self.stop_words)]

    # === RETRIEVAL FUNCTIONS (on model)
    def print_lda_topics(self):
        topics = self.lda_model.print_topics()
        all_topics = []
        for _, s in topics:
            all_topics.append(re.findall(r'(?<=\")[a-z]+(?=\")', s))
        return all_topics

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

    def get_subset_most_frequent(self, start, end):
        subset = []
        feats = self.count_vectorizer.get_feature_names()
        w_counts = np.array(np.sum(self.get_count_matrix(), axis=0))[0]
        sorted_indices = np.argsort(w_counts)[::-1][start:end]
        for i in sorted_indices:
            subset.append(feats[i])
        return subset

    # === EXPORT/IMPORT FUNCTIONS
    def export_count_vectorizer(self, filename, access_type="xb"):
        if self.count_vectorizer is None:
            return None
        with open(filename, access_type) as f:
            pickle.dump(self.count_vectorizer, f)

    def import_count_vectorizer(self, filename):
        with open(filename, "rb") as f:
            d = pickle.load(f)
        self.count_vectorizer = d
        return self.count_vectorizer

    def export_tfidf_vectorizer(self, filename, access_type="xb"):
        if self.tfidf_vectorizer is None:
            return None
        with open(filename, access_type) as f:
            pickle.dump(self.tfidf_vectorizer, f)

    def import_tfidf_vectorizer(self, filename):
        with open(filename, "rb") as f:
            d = pickle.load(f)
        self.tfidf_vectorizer = d
        return self.tfidf_vectorizer

    def export_lda_model(self, filename, access_type="xb"):
        if self.lda_model is None:
            return None
        with open(filename, access_type) as f:
            pickle.dump(self.lda_model, f)

    def import_lda_model(self, filename):
        with open(filename, "rb") as f:
            d = pickle.load(f)
        self.lda_model = d
        return self.lda_model

    def export_all(self, directory, model_name, access_type):
        file_prefix = directory + model_name
        self.export_count_vectorizer(filename=file_prefix + "_count_vec.pk", access_type=access_type)
        self.export_tfidf_vectorizer(filename=file_prefix + "_tfidf_vec.pk", access_type=access_type)
        self.export_lda_model(filename=file_prefix + "_lda_model.pk", access_type=access_type)

    @staticmethod
    def clean(input_string, cap_code=-1):
        """
        Takes in string, returns a unicode-friendly and stripped version of the string.
        """
        cleaned_str = ud.unidecode(input_string).lower() if cap_code == -1 else ud.unidecode(input_string).upper()

        rpl = [(r'(^\s+)|(\s+$)|(\b\')|(\'\b)|(\b\")|(\"b)', ''),  # whitespace at beg/end of string
               (r'(\s+)|([\n|\r|\t|\0]+)', ' ')]
        for p, r in rpl:
            cleaned_str = re.sub(p, r, cleaned_str)
        return cleaned_str

