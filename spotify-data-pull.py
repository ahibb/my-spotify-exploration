import requests
import json
import re

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
    """Retrieve my playlists from the Spotify API (limit set to 40).
    
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
    playlist_ids = []
    for playlist in playlists:
        pl_obj = {}
        pl_new_name = create_playlist_name(playlist['name'])
        if pl_new_name:
            pl_obj['playlist_original_name'] = playlist['name']
            pl_obj['playlist_new_name'] = pl_new_name
            pl_obj['playlist_id'] = playlist['id']
            playlist_ids.append(pl_obj)
    
    return playlist_ids


def create_playlist_name(pl_name):
    year = re.compile('[0-9]')
    year_text = year.findall(pl_name)
    
    pl_new_name = ''
    pl_month = get_month_name(pl_name)
    if pl_month:
        pl_new_name = pl_month + ' ' +  ''.join(year_text)
    
    return pl_new_name


def get_month_name(pl_name):
    months = ["december","january","february","march","april",
            "may","june","july","august","september","october","november"]
    for month in months:
        if month in pl_name.lower():
            return month
    return ''

def get_playlist_tracks(playlist_id, BASE_URL, headers):
    #define what fields we want from the API
    fields = 'items(added_at,track(album(!available_markets,images),artists,duration_ms,explicit,external_urls,href,id,name,popularity,preview_url,track,type))'
    r = requests.get(BASE_URL + 'playlists/' + playlist_id + '/tracks?fields={items}'.format(items=fields), headers=headers)

    if r.status_code == 200:
        json_track_data = r.json()
        #print(json.dumps(json_track_data, sort_keys = False, indent=4))
        return json_track_data
    else:
        display_api_error_details(r)
    
    return {}

def create_tracklist_json(playlist_lookup):
    '''
    {
        playlist original name
        playlist new name
        playlist month
        playlist year
        playlist id
        tracks:[]
    }
    '''
    new_pl_obj = {}
    

def main():
    access_token = get_api_token()

    if access_token != '':
        headers = {
            'Authorization': 'Bearer {token}'.format(token=access_token)
        }
        BASE_URL = 'https://api.spotify.com/v1/'
        playlists = get_my_playlists(BASE_URL, headers)
        playlist_data = process_playlists(playlists)
        print(playlist_data)
        #tracklist_obj = create_tracklist_json(playlist_lookup)


main()