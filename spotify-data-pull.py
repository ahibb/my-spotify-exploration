import requests
import json
import re

def get_api_token():
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
        api_error_message(auth_response)
    return ''

def api_error_message(response):
    response_data = response.json()
    print('Error accessing url {url} with error {error}'.format(url=response.url, error=response_data['error']))
    print('Error details: {description}'.format(description=response_data['error_description']))

def get_my_playlists(BASE_URL, headers):
    user_id = '1258359139'

    # GET request with proper header
    r = requests.get(BASE_URL + 'users/' + user_id + '/playlists?limit=40', headers=headers)
    r = r.json()
    playlists = r['items']

    return playlists

def process_playlists(playlists):
    playlist_ids = {}
    for playlist in playlists:
        pl_new_name = process_playlist_name(playlist['name'])


def process_playlist_name(pl_name):
    year = re.compile('[0-9]')
    year_text = year.findall(pl_name)
    
    pl_month = get_month_name(pl_name)
    pl_new_name = ''
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

def main():
    access_token = get_api_token()

    if access_token != '':
        headers = {
            'Authorization': 'Bearer {token}'.format(token=access_token)
        }
        BASE_URL = 'https://api.spotify.com/v1/'
        playlists = get_my_playlists(BASE_URL, headers)
        process_playlists(playlists)


main()