from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import pandas as pd
import numpy as np

project_name = "Similar Singer"
net_id = "Alyssa Gao (ag2496), Celine Choo (cc972), Mahak Bindal (mb2359), Jerilyn Zheng (jjz67), Jasper Liang (jxl8)"

tf_idf = pd.read_csv('lyrics_data/tfidf_mat_uncompressed.csv')

# TODO: Remove the `sample_data` variable once we are able to dynamically retrieve data. This is here for demo purposes.
# sample_data = [
# 	{'artist_name': 'Amerie', 'description': 'Lorem ipsum', 'img_url': 'https://upload.wikimedia.org/wikipedia/en/d/dc/Amerie_-_All_I_Have_album.jpg'},
# 	{'artist_name': 'Christina Aguilera', 'description': 'Lorem ipsum', 'img_url': 'https://upload.wikimedia.org/wikipedia/en/0/07/Christinaaguilera-christinaaguilera.jpg'},
# 	{'artist_name': 'Rhianna', 'description': 'Lorem ipsum', 'img_url': 'https://upload.wikimedia.org/wikipedia/en/3/32/Rihanna_-_Anti.png'}]

def get_artist_description(artist_name):
    artist_description = "The artist's name is " + artist_name + ". Nice!"   # TODO: replace with description retrieval
    return artist_description

def get_artist_photo(artist_name):
    # TODO: replace with url retrieval
    artist_photo = "https://www.pngitem.com/pimgs/m/148-1487614_spotify-logo-small-spotify-logo-transparent-hd-png.png" 
    return artist_photo

def find_artist(artist_name, tf_idf=tf_idf):
    try:
        return np.argwhere(tf_idf.values[:, 0] == artist_name)[0][0]
    except:
        return -1

def get_rec_artists(query, ling_desc, disliked_artist):
    rec_artists = []
    idx = find_artist(query)
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
    if ((not query) or (data == [])):
        output_message = ''
        return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)
    else:
        output_message = "Based on your query, " + query + ", we recommend..."
        return render_template('search_results.html', name=project_name, netid=net_id, output_message=output_message, data=data)
