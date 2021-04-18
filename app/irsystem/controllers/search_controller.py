from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import pandas as pd
import numpy as np

project_name = "Similar Singer"
net_id = "Alyssa Gao (ag2496), Celine Choo (cc972), Mahak Bindal (mb2359), Jerilyn Zheng (jjz67), Jasper Liang (jxl8)"

tf_idf = pd.read_csv('lyrics_data/tfidf_mat_uncompressed.csv')
artist_details = pd.read_csv('compiled-w-songs_new.csv')

# TODO: Remove the `sample_data` variable once we are able to dynamically retrieve data. This is here for demo purposes.
# sample_data = [
# 	{'artist_name': 'Amerie', 'description': 'Lorem ipsum', 'img_url': 'https://upload.wikimedia.org/wikipedia/en/d/dc/Amerie_-_All_I_Have_album.jpg'},
# 	{'artist_name': 'Christina Aguilera', 'description': 'Lorem ipsum', 'img_url': 'https://upload.wikimedia.org/wikipedia/en/0/07/Christinaaguilera-christinaaguilera.jpg'},
# 	{'artist_name': 'Rhianna', 'description': 'Lorem ipsum', 'img_url': 'https://upload.wikimedia.org/wikipedia/en/3/32/Rihanna_-_Anti.png'}]

def find_artist(artist_name, csv):
    col = 1 if (csv.values[0, 0] == 0) else 0    # checking which column contains the list of artists
    try:
        return np.argwhere(csv.values[:, col] == artist_name)[0][0]
    except:
        return -1

def get_artist_description(artist_name):
    try:
        followers = artist_details['followers'][find_artist(artist_name, artist_details)]
        return artist_name + " has " + str(followers) + " followers on Spotify."
    except:
        return "Couldn't find additional details on " + artist_name + ". "

def get_artist_photo(artist_name):
    try:
        return artist_details['Image URL'][find_artist(artist_name, artist_details)]
    except:
        return "https://www.pngitem.com/pimgs/m/148-1487614_spotify-logo-small-spotify-logo-transparent-hd-png.png"

def get_rec_artists(query, ling_desc, disliked_artist):
    rec_artists = []
    idx = find_artist(query, tf_idf)
    if (idx == -1):
        return []

    # TODO: replace with recommended artists retrieval
    i = 0
    while (i < 10):
        idx += 1
        rec_artist = tf_idf.values[idx % len(tf_idf)][0]
        if (rec_artist != disliked_artist):
            rec_artists.append(rec_artist)
            i += 1
    return rec_artists

def get_results(query, ling_desc, disliked_artist):
    data = []
    top_rec_artists = get_rec_artists(query, ling_desc, disliked_artist)
    if (top_rec_artists == []):
        return []
    for artist in top_rec_artists:
        data.append({'artist_name' : artist, 'description' : get_artist_description(artist), 'img_url' : get_artist_photo(artist)})
    return data    

@irsystem.route('/', methods=['GET'])
def search():
    query = request.args.get('search')
    ling_desc = request.args.get('ling_desc')
    disliked_artist = request.args.get('disliked_artist')
    data = get_results(query, ling_desc, disliked_artist)
    all_artist_names = [s.replace('\'', '').replace('\"', '') for s in artist_details.artists.unique()]

    if (not query):       # empty query
        output_message = ''
        return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data,\
                               artist_names=all_artist_names)
    elif (data == []):    # query returned no results
        output_message = ''
        return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data,\
                               artist_names=all_artist_names,\
                               query_info={"artist_name":query, "ling_desc":ling_desc, "disliked_artist":disliked_artist})
    else:
        output_message = "Based on your query, " + query + ", we recommend..."
        return render_template('search_results.html', name=project_name, netid=net_id, output_message=output_message, data=data,\
                               artist_names=all_artist_names,\
                               query_info={"artist_name":query, "ling_desc":ling_desc, "disliked_artist":disliked_artist})
