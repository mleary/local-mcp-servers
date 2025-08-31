# One time setup using yahoo_oauth.  Should allow for refresh tokens unless oauth file is deleted.

from yahoo_oauth import OAuth2
oauth = OAuth2(None, None, from_file='../oauth2.json')

if not oauth.token_is_valid():
    oauth.refresh_access_token()