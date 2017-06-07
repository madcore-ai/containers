import yaml
from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_oauthlib.client import OAuth


app = Flask(__name__)

with open("apps/gmail.yaml", 'r') as stream:
    try:
        read_data = yaml.load(stream)['app']
    except yaml.YAMLError as exc:
        print(exc)
app.config['GOOGLE_ID'] = read_data['oauth2_client_id']
app.config['GOOGLE_SECRET'] = read_data['oauth2_client_secret']
app.debug = True
app.secret_key = 'development'
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


@app.route('/')
def index():
    try:
        resp = google.authorized_response()
        if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
            )
        session['google_token'] = (resp['access_token'], '')
        me = google.get('userinfo')
        write_data = {'user': {'oauth2_refresh_token':resp['refresh_token'],\
                 'madcore_guid':me.data['id'],'email':me.data['email']}}
        with open('user/gmail/%s.yaml' %me.data['id'], 'w') as outfile:
            yaml.safe_dump(write_data, outfile, default_flow_style=False)
        # return jsonify({"data": me.data})
    except:
        return render_template('index.html')


@app.route('/login')
def login():
    return google.authorize(callback='https://social.ext.funcore.madcore.cloud')


@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


if __name__ == '__main__':
    app.run()