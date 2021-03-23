from pyoauth2 import Client

app = Flask(__name__)
app.secret_key = 'root'

# Oauth config

# Creating an instance of authlib

oauth = OAuth(app)