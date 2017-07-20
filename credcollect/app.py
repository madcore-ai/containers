import yaml
from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_oauthlib.client import OAuth


app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
google_status = False
git_status = False
try:
    with open("/apps/gmail.yaml", 'r') as stream:
        try:
            read_data = yaml.load(stream)['app']
        except yaml.YAMLError as exc:
            print(exc)
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
        with open("/apps/github.yaml", 'r') as stream:
            try:
                read_data = yaml.load(stream)['app']
            except yaml.YAMLError as exc:
                print(exc)
        git = oauth.remote_app(
            'github',
            consumer_key=read_data['GITHUB_ID'],
            consumer_secret=read_data['GITHUB_SECRET'],
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

@app.route('/')
def index():
    if session.get('google_token',None) or session.get('github_token',None):
        return render_template('index.html',message="Successfully logged in",google_status=False,git_status=False)
    try:
        try:
            resp = google.authorized_response()
        except:
            resp = git.authorized_response()
        if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
            )
        try:
            session['github_token'] = (resp['access_token'], '')
            me = git.get('user')
            write_data = {'user': {'access_token':resp['access_token'],\
                     'madcore_guid':me.data['id'],'email':me.data['email']}}
            with open('/user/github/%s.yaml' %me.data['id'], 'w') as outfile:
                yaml.safe_dump(write_data, outfile, default_flow_style=False)
            return render_template('index.html',message="Successfully logged in",google_status=False,git_status=False)
        except:
            session['google_token'] = (resp['access_token'], '')
            me = google.get('userinfo')
            write_data = {'user': {'oauth2_refresh_token':resp['refresh_token'],\
                     'madcore_guid':me.data['id'],'email':me.data['email']}}
            with open('/user/gmail/%s.yaml' %me.data['id'], 'w') as outfile:
                yaml.safe_dump(write_data, outfile, default_flow_style=False)
            return render_template('index.html',message="Successfully logged in",google_status=False,git_status=False)
    except:
        return render_template('index.html',google_status=google_status,git_status=git_status)


@app.route('/login/google')
def login_google():
    return google.authorize(callback='https://social.ext.funcore.madcore.cloud')

@app.route('/login/github')
def login_github():
    return git.authorize(callback='https://social.ext.funcore.madcore.cloud')


@app.route('/logout')
def logout():
    session.pop('google_token', None)
    session.pop('github_token', None)
    return redirect(url_for('index'))

if google_status:
    @google.tokengetter
    def get_google_oauth_token():
        return session.get('google_token')
if git_status:
    @git.tokengetter
    def get_github_oauth_token():
        return session.get('github_token')


if __name__ == '__main__':
    app.run()