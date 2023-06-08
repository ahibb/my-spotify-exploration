import requests
import json
import re
import math

def get_api_token():
    """Retrieve the API token from Spotify."""
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
    """Return collection of playlists as json objects retrieved from the Spotify API.
    
    Keyword arguments
    BASE_URL -- The base url for all Spotify API requests
    headers -- API request headers including bearer token.
    """
    user_id = '1258359139'

    # GET request
    r = requests.get(BASE_URL + 'users/' + user_id + '/playlists?limit=40', headers=headers)
    r = r.json()
    playlists = r['items']

    return playlists

def process_playlists(playlists):
    """Return playlist data as json object (playlist_ids) including cleaned playlist name.
    
    Keyword arguments
    playlists: A list of JSON objects with raw playlist data.
    """
    playlist_ids = []
    for playlist in playlists:
        pl_obj = {}
        pl_obj['playlist_id'] = playlist['id']
        pl_obj['owner_id'] = playlist['owner']['id']
        pl_obj['owner_name'] = playlist['owner']['display_name']
        playlist_ids.append(pl_obj)
    
    return playlist_ids


def get_playlist_tracks(playlist_id, BASE_URL, headers):
    # define what fields I want from the API
    # fields = 'items(added_at,track(album(!available_markets,images),artists,duration_ms,explicit,external_urls,href,id,name,popularity,preview_url,track,type))'
    fields = 'items(added_at,track(artists,duration_ms,explicit,external_urls,href,id,name,popularity,preview_url,track,type))'
    r = requests.get(BASE_URL + 'playlists/' + playlist_id + '/tracks?fields={items}'.format(items=fields), headers=headers)

    if r.status_code == 200:
        json_track_data = r.json()
        return json_track_data['items']
    else:
        display_api_error_details(r)
    
    return {}

def create_tracklist_json(playlist_data, BASE_URL, headers):
    all_pl_tracks = []
    playlist_track_ids = []
    for playlist_obj in playlist_data:
        playlist_id = playlist_obj['playlist_id']
        tracks =  get_playlist_tracks(playlist_obj['playlist_id'],BASE_URL,headers)

        track_ids = []
        for track in tracks:
            track['playlist_id'] = playlist_obj['playlist_id']
            all_pl_tracks.append(track)
            track_ids.append(track['track']['id'])
        track_lookup =  {'playlist_id':playlist_obj['playlist_id'],'track_ids':track_ids}
        playlist_track_ids.append(track_lookup)

    return all_pl_tracks, playlist_track_ids

def get_artist_genres(all_pl_tracks, BASE_URL, headers):
    artist_ids = get_artist_ids(all_pl_tracks)
    num_artist_ids = len(artist_ids)
    max_artists = 50
    num_api_calls = math.ceil(num_artist_ids / max_artists)

    artist_genres = []

    for i in range(num_api_calls):
        start_index = i * 50
        end_index = (i + 1) * 50
        request_artist_ids = artist_ids[start_index:end_index]
        artist_id_str = ','.join(request_artist_ids)
        r = requests.get(BASE_URL + 'artists?ids=' + artist_id_str, headers=headers)

        if r.status_code == 200:
            json_artist_data = r.json()
            for artist in json_artist_data['artists']:
                artist_lookup = {'artist_id':artist['id'], 'genres':artist['genres']}
                artist_genres.append(artist_lookup)
        else:
            display_api_error_details(r)

    return artist_genres

def get_artist_ids(all_pl_tracks):
    artist_ids = []

    for track in all_pl_tracks:
        for artist in track['track']['artists']:
            if artist['id'] not in artist_ids:
                artist_ids.append(artist['id'])
    return artist_ids
    
def write_data_to_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.close() 

def flatten_artist_genre_json(artist_genres_json):
    genre_list = []
    for artist in artist_genres_json:
        for genre in artist['genres']:
            single_genre = [artist['artist_id'],genre]
            genre_list.append(single_genre)

    return genre_list

def main():
    access_token = get_api_token()

    if access_token != '':
        headers = {
            'Authorization': 'Bearer {token}'.format(token=access_token)
        }
        BASE_URL = 'https://api.spotify.com/v1/'
        playlists = get_my_playlists(BASE_URL, headers)
        playlist_data = process_playlists(playlists)
        all_pl_tracks, playlist_track_ids = create_tracklist_json(playlist_data, BASE_URL, headers)
        artist_genres= get_artist_genres(all_pl_tracks,BASE_URL, headers)

        artist_genres_f = flatten_artist_genre_json(artist_genres)
        print(artist_genres_f)
        #write_data_to_file(all_pl_tracks,'playlist_data.json')
        #write_data_to_file(artist_genres,'artist_genre_lookup.json')
        #write_data_to_file(playlist_track_ids,'playlist_track_lookup.json')

        # TODO Create json object for unique tracks with playlist references
        # TODO Create json data to track tracks and all added at dates
        #TODO update to pull data from Spotify and dump data to file
        # TODO update to read data from file dump



main()