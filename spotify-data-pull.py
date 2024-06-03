import requests
import json
import re
import math
import csv
from itertools import chain, starmap

def get_api_token():
    """Retrieve the API token from Spotify."""
    print('retrieving API token')
    # open file with credentials to access Spotify API
    creds_file = open('.creds.json', 'r')
    creds = json.load(creds_file)
    CLIENT_ID = creds['CLIENT_ID']
    CLIENT_SECRET = creds['CLIENT_SECRET']
    AUTH_URL = 'https://accounts.spotify.com/api/token'

    # POST
    auth_response = requests.post(AUTH_URL, {
        'grant_type':'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })

    # Process token based on API response
    if auth_response.status_code == 200:
        auth_response_data = auth_response.json()

        access_token = auth_response_data['access_token']
        return access_token
    else:
        display_api_error_details(auth_response)
    return ''

def display_api_error_details(response):
    """Print an error message returned from the API.
    
    Keyword arguments
    response -- The response object returned from the API request
    """
    response_data = response.json()
    print('Error accessing url {url} with error {error}'.format(url=response.url, error=response_data['error']))
    print('Error details: {description}'.format(description=response_data['error_description']))

def get_my_playlists(BASE_URL, headers):
    """Return collection of playlists as json objects from the Spotify API.
    
    Keyword arguments
    BASE_URL -- The base url for all Spotify API requests
    headers -- API request headers including bearer token.
    """
    print('retrieving playlists')
    user_id = '1258359139'

    # GET request
    url = BASE_URL + 'users/' + user_id + '/playlists?limit=40'
    playlists = []
    while url:
        r = requests.get(url, headers=headers)
        r = r.json()
        url = r['next']
        playlist_data = r['items']
        for playlist in playlist_data:
            pl_obj = {}
            pl_obj['playlist_id'] = playlist['id']
            pl_obj['owner_id'] = playlist['owner']['id']
            pl_obj['owner_name'] = playlist['owner']['display_name']
            pl_obj['playlist_name'] = playlist['name']
            playlists.append(pl_obj)

    return playlists

def get_playlist_list(playlists):
    """Return playlist data as list (playlist_ids).
    
    Keyword arguments
    playlists: A list of JSON objects with raw playlist data.
    """
    print('creating playlist list')
    playlist_ids = []
    for playlist in playlists:
        pl_obj = {}
        pl_obj['playlist_id'] = playlist['id']
        pl_obj['owner_id'] = playlist['owner']['id']
        pl_obj['owner_name'] = playlist['owner']['display_name']
        pl_obj['playlist_name'] = playlist['name']
        playlist_ids.append(pl_obj)

    return playlist_ids

def create_playlist_table(playlist_data):
    """Using a list of playlist objects, build a table (nested list) for the playlist data
    """
    playlist_table = [['playlist_id','playlist_name','owner_id','owner_name']]
    for playlist in playlist_data:
        row = [playlist['playlist_id'],playlist['playlist_name'],playlist['owner_id'],playlist['owner_name']]
        playlist_table.append(row)
    return playlist_table

def get_playlist_tracks(playlist_id, BASE_URL, headers):
    """
    Get the tracks from a playlist.
    playlist_id: The ID of the playlist to get tracks from.
    """
    print('retrieving playlist tracks for playlist id: ',playlist_id)
    # define what fields I want from the API
    fields = 'items(added_at,track(artists,duration_ms,explicit,external_urls,href,id,name,popularity,preview_url,track,type))'
    r = requests.get(BASE_URL + 'playlists/' + playlist_id + '/tracks?fields={items}'.format(items=fields), headers=headers)

    if r.status_code == 200:
        json_track_data = r.json()
        return json_track_data['items']
    else:
        display_api_error_details(r)
    
    return {}

def create_tracklist_json(playlist_data, BASE_URL, headers):
    """
    Given a list of playlist ids, retrieve the tracks for each playlist and return them as a list
    """
    all_pl_tracks = []
    unique_tracks = []
    for playlist_obj in playlist_data:
        tracks =  get_playlist_tracks(playlist_obj['playlist_id'],BASE_URL,headers)

        for track in tracks:
            track['playlist_id'] = playlist_obj['playlist_id']
            all_pl_tracks.append(track)

            if track['track']['id'] not in unique_tracks:
               unique_tracks.append(track['track']['id'])
    print('UNIQUE TRACK LENGTH')
    print(len(unique_tracks))
    return all_pl_tracks

def get_artist_ids(all_pl_tracks):
    """ Build a list of unique artist ids based on the tracks retrieved"""
    artist_ids = []

    for track in all_pl_tracks:
        for artist in track['track']['artists']:
            if artist['id'] not in artist_ids:
                artist_ids.append(artist['id'])
    return artist_ids

def get_artists(all_pl_tracks, BASE_URL, headers):
    '''Retrieve artists from Spotify APIs
    '''
    artist_ids = get_artist_ids(all_pl_tracks)
    num_artist_ids = len(artist_ids)

    print('number of artists: ',num_artist_ids)
    max_artists = 50 # maximum retrieval count allowed
    num_api_calls = math.ceil(num_artist_ids / max_artists)

    artists_json = []
    for i in range(num_api_calls):
        start_index = i * 50
        end_index = (i + 1) * 50
        request_artist_ids = artist_ids[start_index:end_index]
        request_artist_ids = list(filter(None, request_artist_ids))
        artist_id_str = ','.join(request_artist_ids)
        print('retrieving artist data for start_idx: ',start_index, ' to ',end_index)
        r = requests.get(BASE_URL + 'artists?ids=' + artist_id_str, headers=headers)

        if r.status_code == 200:
            artist_resp_body = r.json()
            artist_data = artist_resp_body["artists"]
            for artist in artist_data:
                artists_json.append(artist)
        else:
            display_api_error_details(r)
    
    print('finished retrieving artist data')
    return artists_json

def get_artist_genres(json_artist_data):
    """Build a lookup of the artist id and corresponding genre list using
    the artist json data from the Spotify API.
    """
    artist_genres = []

    for artist in json_artist_data:
        artist_lookup = {'artist_id':artist['id'], 'genres':artist['genres']}
        artist_genres.append(artist_lookup)
    return artist_genres

def create_artist_genre_lookup(artist_genres_json):
    genre_list = []
    genre_list.append(['artist_id','genre'])
    for artist in artist_genres_json:
        for genre in artist['genres']:
            single_genre = [artist['artist_id'],genre]
            genre_list.append(single_genre)
    return genre_list

def create_artist_table(artists_json,field_list):
    artist_table = [field_list]
    for artist in artists_json:
        row = []
        for field in field_list:
            row.append(artist[field])
        artist_table.append(row)

    return artist_table
            
def create_tracklist_table(tracklist_json):
    track_table = [['track_id','playlist_id','track_name','added_at','popularity','duration_ms','explicit']]
    for track in tracklist_json:
        row = [track['track']['id']
            ,track['playlist_id']
            ,track['track']['name']
            ,track['added_at']
            ,track['track']['popularity']
            ,track['track']['duration_ms']
            ,track['track']['explicit']]
        track_table.append(row)
    return track_table

def create_track_artist_lookup_table(tracklist_json):
    track_artist_lookup = [['track_id','artist_id']]
    for track in tracklist_json:
        for artist in track['track']['artists']:
            row = [track['track']['id'],artist['id']]
            track_artist_lookup.append(row)
    return track_artist_lookup

def flatten_playlist_tracks_ids_json(playlist_track_ids):
    playlist_tracks = []
    playlist_tracks.append(['track_id','playlist_id'])
    for playlist in playlist_track_ids:
        for track in playlist['track_ids']:
            track_id = [playlist['playlist_id'],track]
            playlist_tracks.append(track_id)

    return playlist_tracks

def flatten_json_iterative_solution(dictionary):
    """Flatten a nested json file
    from: https://towardsdatascience.com/how-to-flatten-deeply-nested-json-objects-in-non-recursive-elegant-python-55f96533103d
    """

    def unpack(parent_key, parent_value):
        """Unpack one level of nesting in json file"""
        # Unpack one level only!!!
        
        if isinstance(parent_value, dict):
            for key, value in parent_value.items():
                temp1 = parent_key + '_' + key
                yield temp1, value
        elif isinstance(parent_value, list):
            i = 0 
            for value in parent_value:
                temp2 = parent_key + '_'+str(i) 
                i += 1
                yield temp2, value
        else:
            yield parent_key, parent_value 
            # Keep iterating until the termination condition is satisfied
    while True:
        # Keep unpacking the json file until all values are atomic elements (not dictionary or list)
        dictionary = dict(chain.from_iterable(starmap(unpack, dictionary.items())))
        # Terminate condition: not any value in the json file is dictionary or list
        if not any(isinstance(value, dict) for value in dictionary.values()) and \
            not any(isinstance(value, list) for value in dictionary.values()):
            break

    return dictionary   

def write_json_to_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.close() 
    print('wrote ', filename, ' to file')

def write_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in data:
            writer.writerow(row)
    print('wrote ', filename, ' to file')

def main():
    BASE_URL = 'https://api.spotify.com/v1/'
    access_token = get_api_token()

    if access_token != '':
        headers = {
            'Authorization': 'Bearer {token}'.format(token=access_token)
        }

        # process playlist data
        playlists = get_my_playlists(BASE_URL, headers)
        playlist_table = create_playlist_table(playlists)
        write_to_csv(playlist_table,'playlists.csv')

        # get playlist tracks
        all_pl_tracks = create_tracklist_json(playlists, BASE_URL, headers)
        artist_track_lookup_table = create_track_artist_lookup_table(all_pl_tracks)

        write_to_csv(artist_track_lookup_table,'artist_track_lookup.csv')

        # get artists from API
        artists_obj_list = get_artists(all_pl_tracks,BASE_URL, headers)
        
        artists_f = []
        for artist_obj in artists_obj_list:
            flat = flatten_json_iterative_solution(artist_obj)
            artists_f.append(flat)

        artist_table = create_artist_table(artists_f,['id','name','followers_total','popularity','external_urls_spotify'])
        write_to_csv(artist_table,'artists.csv')

        # get artist genres
        artist_genres = get_artist_genres(artists_obj_list)

        artist_genres_lookup = create_artist_genre_lookup(artist_genres)
        write_to_csv(artist_genres_lookup,'artist_genres.csv')

        track_table = create_tracklist_table(all_pl_tracks)
        write_to_csv(track_table,'tracks.csv')

    else:
        print('Failed to get access token from API. Exiting')
        exit()



main()