from flask import Flask, url_for, render_template, session, redirect
from authlib.integrations.flask_client import OAuth
from pyoauth2 import Client
import requests

app = Flask(__name__)
app.secret_key = 'root'

# Oauth config

# Creating an instance of authlib

oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id='247455405941-19ecmncpddf3kj27mn49jdsp4uncb8hq.apps.googleusercontent.com',
    client_secret='rOUNx0Bhd8yC6-RenPy1JDtD',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)


fortytwo = oauth.register(
    name='fortytwo',
    client_id='e950453dc3fb64e3f37bd148d6dbdbcb04e4cd31b78133859082de9400e3c2a6',
    client_secret='758845c438dcd3cd55f9d5a221735c23c2dae39f9797214aa434436e02c4b5b0',
    access_token_url='https://api.intra.42.fr/oauth/token',
    access_token_params=None,
    authorize_url='https://api.intra.42.fr/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.intra.42.fr',
    userinfo_endpoint=None,  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'public'},
)

# openid is google id, profile (Username, lastname), and the user's email

@app.route('/')
def hello_world():
    # email = dict(session).get('email', None)
    # profile = dict(session).get('profile', None)
    # openid = dict(session).get('openid', None)
    email = dict(session).get('email', None)
    return f'{session.keys()}, {email}'

@app.route('/oauth/google')
def login_google():
    google = oauth.create_client('google')
    redirect_uri = url_for('gauthorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/oauth/42')
def login_42():
    fortytwo = oauth.create_client('fortytwo')
    redirect_uri = url_for('authorize', _external=True)
    return fortytwo.authorize_redirect(redirect_uri)

@app.route('/gauthorize')
def gauthorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    resp.raise_for_status()
    user_info = resp.json()
    # do something with the token and profile
    session['email'] = user_info['email']
    return f'{user_info}'

@app.route('/authorize')
def authorize():
    fortytwo = oauth.create_client('fortytwo')
    token = fortytwo.authorize_access_token()
    url = 'https://api.intra.42.fr/oauth/token/info'
    headers = {'Authorization': 'Bearer 0319b172a1e65fe8a626f16d9a85f205dd245bc0110dd9b21569219a29c616a2'}
    r = requests.get(url, headers=headers)
    # url = ("/%s/info" %(token))
    # resp = fortytwo.get("https://api.intra.42.fr/oauth/token/info", headers={"Authorization: Bearer 0319b172a1e65fe8a626f16d9a85f205dd245bc0110dd9b21569219a29c616a2"})
    # # resp.raise_for_status()
    user_info = r.json()
    # do something with the token and profile
    # session['email'] = user_info['email']
    for key, value in user_info.items():
        print (key, value)
    return f'{user_info}'


app.run(debug=True)
