#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of Tumult.
"""
import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from requests_oauthlib import OAuth2Session

OAUTH2_CLIENT_ID     = '299915176260403200'
OAUTH2_CLIENT_SECRET = 'du0WfmpyPjIZlDM-DqjM9eJdPL2Igcti'
OAUTH2_SCOPE         = ['identify', 'guilds', 'messages.read']
API_BASE_URL         = 'https://discordapp.com/api'
OAUTH2_REDIRECT_URI  = 'http://localhost:42424/oauth'

AUTHORIZATION_URL    = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL            = API_BASE_URL + '/oauth2/token'

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=OAUTH2_SCOPE,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET

# Routes

@app.route("/")
def root():
    discord = make_session()
    authorization_url, state = discord.authorization_url(AUTHORIZATION_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)


@app.route("/oauth")
def oauth():
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url.strip(),
    )
    session['oauth2_token'] = token
    return redirect(url_for('.me'))


@app.route("/me")
def me():
    try:
        discord = make_session(token=session.get('oauth2_token'))
        user = discord.get(API_BASE_URL + '/users/@me').json()
        guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
        return render_template("layout.html", contentTemplate="servers.html", user=user, servers=guilds)
    except Exception as e:
        return unauthorized(e)


@app.errorhandler(403)
def unauthorized(e):
    return render_template("layout.html", content="Error 403"), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template("layout.html", content="Error 404"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("layout.html", content="Error 500"), 500

def run():
    app.run(host='127.0.0.1', port=42424)
