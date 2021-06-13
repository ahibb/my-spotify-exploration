import requests
import json

# open file containing the credentials to access Spotify API
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

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data['access_token']

headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

BASE_URL = 'https://api.spotify.com/v1/'

# album link https://open.spotify.com/album/3stadz88XVpHcXnVYMHc4J?si=-Wfsnr3nRvyCjL4ETMz8Ow&dl_branch=1
album_id = '3stadz88XVpHcXnVYMHc4J'
# actual GET request with proper header
r = requests.get(BASE_URL + 'albums/' + album_id +'/tracks', headers=headers)
r = r.json()
#tracks = r['items'][0]['name']
tracks = r['items']

for track in tracks:
    #print(track)
    #print('\n')
    pass
