import requests
import json


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

    if auth_response.status_code == 200:
        auth_response_data = auth_response.json()

        access_token = auth_response_data['access_token']
        return access_token
    else:
        api_error_message(auth_response)
    return ''

def api_error_message(response):
    response_data = response.json()
    print("Error accessing url {url} with error {error}".format(url=response.url, error=response_data['error']))
    print("Error details: {description}".format(description=response_data['error_description']))

def get_my_playlists(BASE_URL, headers):
    # album link https://open.spotify.com/album/3stadz88XVpHcXnVYMHc4J?si=-Wfsnr3nRvyCjL4ETMz8Ow&dl_branch=1
    album_id = '3stadz88XVpHcXnVYMHc4J'
    user_id = '1258359139'

    # GET request with proper header
    # r = requests.get(BASE_URL + 'albums/' + album_id +'/tracks', headers=headers)
    r = requests.get(BASE_URL + 'users/' + user_id + '/playlists', headers=headers)
    r = r.json()
    #tracks = r['items'][0]['name']
    playlists = r['items']

    for playlist in playlists:
        print(playlist)
        print('\n')


def main():
    access_token = get_api_token()

    if access_token != '':
        headers = {
            'Authorization': 'Bearer {token}'.format(token=access_token)
        }
        BASE_URL = 'https://api.spotify.com/v1/'
        get_my_playlists(BASE_URL, headers)


main()