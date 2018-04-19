import yaml
from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
google_status = False
git_status = False
try:
    with open("/opt/credscollect/apps.yaml", 'r') as stream:
        try:
            read_data = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    oauth = OAuth(app)
    try:
        app.config['GOOGLE_ID'] = read_data['oauth2_client_id']
        app.config['GOOGLE_SECRET'] = read_data['oauth2_client_secret']
        oauth = OAuth(app)
        google = oauth.remote_app(
            'google',
            consumer_key=app.config.get('GOOGLE_ID'),
            consumer_secret=app.config.get('GOOGLE_SECRET'),
            request_token_params={
                'scope': 'email',
                'access_type': 'offline'
            }
            ,
            base_url='https://www.googleapis.com/oauth2/v1/',
            request_token_url=None,
            access_token_method='POST',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            authorize_url='https://accounts.google.com/o/oauth2/auth',
        )
        google_status = True
    except:
        pass
    try:
        git = oauth.remote_app(
            'github',
            consumer_key=read_data['consumer_key'],
            consumer_secret=read_data['consumer_secret'],
            request_token_params={'scope': 'user:email'},
            base_url='https://api.github.com/',
            request_token_url=None,
            access_token_method='POST',
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize',
        )
        git_status = True
    except:
        pass

except:
    pass



def check_user():
    global google_status,git_status
    if session.get('google_token',None) or session.get('github_token',None):
        message="Successfully logged in"
        google_status=False
        git_status=False
        return message,google_status,git_status
    else:
        message = None
        return message,google_status,git_status


@app.route('/authorize/google/')
def google_data():
    global google_status,git_status
    resp = google.authorized_response()
    try:
        session['google_token'] = (resp['access_token'], '')
        me = google.get('userinfo')
        write_data = {'user': {'oauth2_refresh_token':resp['refresh_token'],\
                 'madcore_guid':me.data['id'],'email':me.data['email']}}
        with open('/opt/credcollect/users/github/%s.yaml' %me.data['id'], 'w') as outfile:
            yaml.safe_dump(write_data, outfile, default_flow_style=False)
        message="Successfully logged in"
    except:
        message = "File writing failed"
    google_status=False
    git_status=False
    return render_template('index.html', message=message, google_status=google_status,git_status=git_status)	

@app.route('/authorize/github/')
def github_data():
    global google_status,git_status
    resp = google.authorized_response()
    try:
        session['github_token'] = (resp['access_token'], '')
        me = git.get('user')
        write_data = {'user': {'access_token':resp['access_token'],\
                 'madcore_guid':me.data['id'],'email':me.data['email']}}
        with open('/opt/credcollect/users/gmail/%s.yaml' %me.data['id'], 'w') as outfile:
            yaml.safe_dump(write_data, outfile, default_flow_style=False)
        message="Successfully logged in"
    except:
        message = "File writing failed"
    google_status=False
    git_status=False
    return render_template('index.html', message=message, google_status=google_status,git_status=git_status)	




@app.route('/login/google')
def login_google():
    return google.authorize(callback='http://api.solve.zone/authorize/google/')

@app.route('/login/git')
def login_github():
    return git.authorize(callback='https://api.solve.zone/authorize/github/')


@app.route('/logout')
def logout():
    global google_status,git_status
    session.pop('google_token', None)
    session.pop('github_token', None)
    google_status = True
    git_status = True
    return redirect(url_for('index'))

if google_status:
    @google.tokengetter
    def get_google_oauth_token():
        return session.get('google_token')
if git_status:
    @git.tokengetter
    def get_github_oauth_token():
        return session.get('github_token')

