import yaml
from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_oauthlib.client import OAuth
from account import *


@app.route('/')
def index():
    message,google_status,git_status = check_user()
    return render_template('index.html',message=message,google_status=google_status,git_status=git_status)



if __name__ == '__main__':
    app.run()