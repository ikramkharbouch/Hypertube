from flask import Flask, url_for, render_template, session, redirect
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = 'root'

# Oauth config

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

# openid is google id, profile (Username, lastname), and the user's email

@app.route('/')
def hello_world():
    # email = dict(session).get('email', None)
    # profile = dict(session).get('profile', None)
    # openid = dict(session).get('openid', None)
    email = dict(session).get('email', None)
    return f'{session.keys()}, {email}'

@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    resp.raise_for_status()
    user_info = resp.json()
    # do something with the token and profile
    session['email'] = user_info['email']
    session['_google_authlib_state_'] = user_info['_google_authlib_state_']
    return redirect('/')


app.run(debug=True)
