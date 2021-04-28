from . import *
from .helper_functions import *

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class ArtistReviewLoader:
    def __init__(self, review_count_threshold=30):
        """
        Initializing a ArtistReviewLoader object will immediately load in all of the artist information,
        the reviews, and any subsequent data structures.
        """
        print("================ INITIALIZING...!")
        # List of all relevant artists
        self.ALL_ARTISTS = ArtistReviewLoader.get_combined_artists()

        # Artist to index mapping
        self.ARTIST_TO_INDEX = {a: i for i, a in enumerate(self.ALL_ARTISTS)}

        # Pandas DataFrame of all reviews
        self.reviews_df = pd.concat([self.get_pf_reviews_df(), self.get_mard_reviews_df()]).drop(columns=["score"])

        # Dictionary of artist(str) -> reviews(list(str))
        self.artist_to_reviews = ArtistReviewLoader.process_reviews(self.ALL_ARTISTS, self.reviews_df, review_count_threshold)

        # TFIDF Vectorizer of all artists and their reviews
        self.tfidf = ArtistReviewLoader.make_tfidf(self.artist_to_reviews, self.ALL_ARTISTS)
        print("================ COMPLETE...!")

    def get_artist_index(self, artist_name):
        return self.ARTIST_TO_INDEX[artist_name]

    def get_reviews_df(self):
        return self.reviews_df

    def get_artist_to_reviews_dict(self):
        return self.artist_to_reviews

    def get_reviews_for_artist(self, artist_name):
        return self.artist_to_reviews[artist_name]

    def get_review_counts(self):
        return np.array([len(self.artist_to_reviews[a]) for a in self.artist_to_reviews])

    def get_tfidf_matrix(self):
        return self.tfidf

    @staticmethod
    def load_mard():
        """
        Static method for loading MARD dataset. Returns a list of artists.
        """
        metadata = read_mard_json(MARD_MD_FILELOC)
        artists = set([])
        for row in metadata:
            if 'artist' in row:
                artists.add(clean_str(row['artist'], cap_code=1))

        return sorted(list(artists))

    @staticmethod
    def load_pf():
        """
        Static method for loading Pitchfork dataset. Returns a list of artists.
        """
        all_pf_tables = ['artists', 'content', 'genres', 'labels', 'reviews', 'years']
        pitchfork_db = {}

        for table in all_pf_tables:
            pitchfork_db[table] = run_query_on_sqlite_db("SELECT * FROM " + table, PF_RV_FILELOC)
        return sorted([clean_str(a, cap_code=1) for a in pd.unique(pitchfork_db['artists']['artist'])])

    @staticmethod
    def load_kaggle():
        """
        Static method for loading artists from Kaggle dataset.
        """
        kaggle_tfidf = pd.read_csv(KAGGLE_FILELOC)
        return sorted([clean_str(s, cap_code=1) for s in kaggle_tfidf.values[:, 0]])

    @staticmethod
    def get_combined_artists():
        """
        Returns a list of artists that exist in Kaggle but also have reviews.
        """
        mard_artists = set(ArtistReviewLoader.load_mard())
        pitchfork_artists = set(ArtistReviewLoader.load_pf())
        kaggle_artists = set(ArtistReviewLoader.load_kaggle())
        return kaggle_artists.intersection(pitchfork_artists.union(mard_artists))

    @staticmethod
    def process_reviews(input_artist_list, input_dataframe, max_reviews):
        """
        Maps artist name to a list of reviews written about that artist.
        """
        artist_to_review_dict = {}

        # Initialize dictionary of all artists
        for artist in input_artist_list:
            artist_to_review_dict[artist] = []

        # Iterate through DataFrame to sanitize strings
        # and add reviews to dict
        for i, row in input_dataframe.iterrows():
            if type(row['artist']) != str or len(row['artist']) == 0:
                continue
            temp_artist = clean_str(row['artist'], cap_code=1)
            if temp_artist in artist_to_review_dict and len(artist_to_review_dict[temp_artist]) <= max_reviews:
                temp_review_string = ""
                if type(row['title']) == str and len(row['title']) > 0:
                    temp_review_string += clean_str(row['title'])
                if type(row['content']) == str and len(row['content']) > 0:
                    temp_review_string += clean_str(row['content']) \
                        if len(temp_review_string) == 0 else " - " + clean_str(row['content'])

                artist_to_review_dict[temp_artist].append(temp_review_string)

        return artist_to_review_dict

    @staticmethod
    def get_pf_reviews_df():
        """
        Helper Function:
        Returns Pandas DataFrame of PitchFork reviews. Required columns in DF: artist, title, content.
        """
        return run_query_on_sqlite_db(
            """
            SELECT reviews.title, reviews.artist, reviews.score, content.content
              FROM content
              LEFT JOIN reviews
              ON content.reviewid = reviews.reviewid
            """, PF_RV_FILELOC)

    @staticmethod
    def get_mard_reviews_df():
        """
        Helper Function:
        Returns Pandas DataFrame of MARD reviews. Required columns in DF: artist, title, content.
        """
        mard_md_df = read_mard_json_as_df(MARD_MD_FILELOC)
        mard_rev_df = read_mard_json_as_df(MARD_RV_FILELOC)

        # Left join on metadata table
        df = mard_md_df.merge(mard_rev_df, on='amazon-id', how='left')

        drop_cols = ['artist-mbid', 'amazon-id', 'label', 'artist_url', 'first-release-year', 'songs', 'salesRank',
                     'related', 'brand', 'reviewerID', 'reviewerName', 'helpful', 'unixReviewTime', 'overall',
                     'reviewTime', 'summary']
        return df.rename(columns={'reviewText':'content'}).drop(columns=drop_cols)


    @staticmethod
    def make_tfidf(input_artist_to_reviews, input_all_artists):
        """
        Returns TFIDF Vectorizer matrix where each document is an artist and the terms are words in the reviews.
        """
        vectorizer = TfidfVectorizer(analyzer='word', stop_words={'english'})
        consolidated_reviews = []
        for a in input_all_artists:
            consolidated_reviews.append(" ".join(input_artist_to_reviews[a]))
        return vectorizer.fit_transform(consolidated_reviews)
