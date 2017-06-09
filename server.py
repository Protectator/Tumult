#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of Tumult.
"""
import os

import datetime
import requests
import time
import random
import colorsys

from builtins import int

from mysql import MySQL
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, abort, current_app
from requests_oauthlib import OAuth2Session

OAUTH2_CLIENT_ID = '299915176260403200'
OAUTH2_CLIENT_SECRET = 'du0WfmpyPjIZlDM-DqjM9eJdPL2Igcti'
OAUTH2_SCOPE = ['identify', 'guilds']
API_BASE_URL = 'https://discordapp.com/api'
OAUTH2_REDIRECT_URI = 'http://localhost:42424/auth'

AUTHORIZATION_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

cache = {}
cache['user'] = {}
cache['usertoken'] = {}
cache['guilds'] = {}

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

@app.route("/") # Index
def root():
    token = session.get('oauth2_token')
    (user, usertoken) = get_user_cache(token, cache)
    return render_template("layout.html", contentTemplate="index.html", user=user)


@app.route("/discordauth") # Redirection to Discord authorization page
def discordauth():
    discord = make_session()
    authorization_url, state = discord.authorization_url(AUTHORIZATION_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)


@app.route("/auth") # Callback from Discord auth
def auth():
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url.strip(),
    )
    session['oauth2_token'] = token
    cache['user'][token['access_token']] = discord.get(API_BASE_URL + '/users/@me').json()
    return render_template("layout.html", contentTemplate="usertoken.html")


@app.route("/usertoken", methods=['POST'])
def usertoken():
    try:
        token = session.get('oauth2_token')
        usertoken = request.form['usertoken'].strip('"')
        cache['usertoken'][token['access_token']] = usertoken
        return redirect('/me')
    except Exception as e:
        return unauthorized(e)


@app.route("/me")
def me():
    # Auth and session
    token = session.get('oauth2_token')
    (user, usertoken) = get_user_cache(token, cache)
    check_auth(user, usertoken)

    # API calls
    discord = make_session(token=token)
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()

    # Render
    return render_template("layout.html", contentTemplate="servers.html", user=user, servers=guilds)


@app.route("/server/<guildId>")
def server(guildId):
    # Auth and session
    token = session.get('oauth2_token')
    (user, usertoken) = get_user_cache(token, cache)
    check_auth(user, usertoken)

    # API calls
    headers = {'authorization': usertoken}
    guild    = requests.get(API_BASE_URL + '/guilds/' + guildId, headers=headers).json()
    channels = requests.get(API_BASE_URL + '/guilds/' + guildId + '/channels', headers=headers).json()

    # Cache
    cache['guilds'][guildId] = guild

    # Render
    return render_template("layout.html", contentTemplate="server.html", user=user, server=guild, channels=channels)


@app.route("/channel/<channelId>")
def channel(channelId):
    # Auth and session
    token = session.get('oauth2_token')
    (user, usertoken) = get_user_cache(token, cache)
    check_auth(user, usertoken)

    # API calls
    headers = {'authorization': usertoken}
    channel = requests.get(API_BASE_URL + '/channels/' + channelId, headers=headers).json()
    params = {'around': channel['last_message_id']}
    messages = requests.get(API_BASE_URL + '/channels/' + channelId + '/messages', headers=headers, params=params).json()

    # Cache
    guild = cache['guilds'][channel['guild_id']]

    # Render
    return render_template("layout.html", contentTemplate="channel.html", user=user, channel=channel, server=guild, messages=messages)

@app.route("/server-info/<guildId>")
def serverInfo(guildId):
    # Auth and session
    token = session.get('oauth2_token')
    (user, usertoken) = get_user_cache(token, cache)
    check_auth(user, usertoken)

    mysqldb = MySQL(current_app.config['DB_HOST'], current_app.config['DB_USER'], current_app.config['DB_PASS'])
    mysqldb.connect()
    messages = mysqldb.getMessages(guildId)
    nbMessages = len(messages)

    # API calls
    headers = {'authorization': usertoken}
    channel = requests.get(API_BASE_URL + '/channels/' + guildId, headers=headers).json()
    guild    = requests.get(API_BASE_URL + '/guilds/' + guildId, headers=headers).json()
    channels = requests.get(API_BASE_URL + '/guilds/' + guildId + '/channels', headers=headers).json()
    cache['guilds'][guildId] = guild

    guild = cache['guilds'][channel['guild_id']]
    data = {
        'guildId': guildId,
        'channels': channels
    }

    serverinfos = {
        'nbmessages' : nbMessages,
        'nbchannels' : 0,
        'firstmessage' : mysqldb.getFirstMessage(guildId),
        'lastmessage' : mysqldb.getLastMessage(guildId)
    }

    # Compute things

    # Render
    return render_template("layout.html", contentTemplate="server-info.html", user=user, server=guild, data=data, serverinfos=serverinfos)


@app.route("/api/compute/<guildId>")
def compute(guildId):
    # Auth and session
    token = session.get('oauth2_token')
    (user, usertoken) = get_user_cache(token, cache)

    # Logic
    way = request.args.get('time')
    channelId = request.args.get('channelId')
    mysqldb = MySQL(current_app.config['DB_HOST'], current_app.config['DB_USER'], current_app.config['DB_PASS'])
    mysqldb.connect()
    params = {}

    # API calls
    headers = {'authorization': usertoken}

    lastMessageId = mysqldb.getLastMessage(channelId)
    if lastMessageId is None:
        channel = requests.get(API_BASE_URL + '/channels/' + channelId, headers=headers).json()
        params = {'around': int(channel['last_message_id']), 'limit': 100}
    elif way == 'after':
        lastMessageId = mysqldb.getLastMessage(channelId)
        params = {'after': int(lastMessageId['id']), 'limit': 100}
    elif way == 'before':
        firstMessageId = mysqldb.getFirstMessage(channelId)
        params = {'before': int(firstMessageId['id']), 'limit': 100}
    else:
        abort(412, "Incorrect 'time' parameter.")
        return

    messages = requests.get(API_BASE_URL + '/channels/' + channelId + '/messages', headers=headers, params=params).json()

    def take8(l): return [l[0], l[1][:8]]

    toInsert = [(str(message['id']),
                 str(guildId),
                 str(channelId),
                 str(message['author']['id']),
                 str(message['content']),
                 str(' '.join(take8(message['timestamp'].split('T')))),
                 str(message['author']['username']),
                 message['author']['discriminator'],
                 str(message['author']['avatar'])) for message in messages]
    # DB Fill
    returnValue = mysqldb.insertMessages(toInsert)

    content = "From DB : " + str(returnValue) + "<br>Got messages : <pre>" + str(messages) + "</pre>"

    # Render
    json = {
        'result': 'ok',
        'message': 'Successfully inserted messages'
    }

    return jsonify(json)


@app.route("/api/graph/<channelId>")
def graph(channelId):
    # Logic
    mysqldb = MySQL(current_app.config['DB_HOST'], current_app.config['DB_USER'], current_app.config['DB_PASS'])
    mysqldb.connect()
    messages = mysqldb.getMessages(channelId)

    count = {}
    label = {}
    for message in messages:
        if message['author_id'] in count:
            count[message['author_id']]  += 1
        else:
            count[message['author_id']] = 1
            label[message['author_id']] = message['author_username']

    nodes = []


    authors = len(count)
    i = 0
    for author in count:
        color = colorsys.hsv_to_rgb(1/authors*i,1,1)
        node = {
            'id': author,
            'label': label[author],
            'color': ('#%02X%02X%02X' % (int(color[0]*255), int(color[1]*255), int(color[2]*255))),
            'value': count[author]
        }
        nodes.append(node)
        i+=1

    #[{from: 1, to: 3, value: 3},..]
    edges = []
    labels = {}
    for i in range(1, len(messages)):
        key = (messages[i]['author_id'],messages[i-1]['author_id'])
        if key in labels:
            labels[key] += 1
        else:
            labels[key] = 1

    for label in labels:
        edge = {
            'from': label[0],
            'to': label[1],
            'arrows': 'to',
            'value': labels[label]
        }
        edges.append(edge)


    # Render
    json = {
        'nodes': nodes,
        'edges': edges
    }

    return jsonify(json)


@app.errorhandler(401)
def unauthorized(e):
    return render_template("layout.html", content="Error 401", warningMessage=e.description), 401


@app.errorhandler(403)
def forbidden(e):
    return render_template("layout.html", content="Error 403"), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template("layout.html", content="Error 404"), 404


@app.errorhandler(412)
def page_not_found(e):
    return render_template("layout.html", content="Error 412", warningMessage=e.description), 412


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("layout.html", content="Error 500"), 500


@app.context_processor
def utility_processor():
    def serverimg(server, hash):
        if hash:
            return 'https://cdn.discordapp.com/icons/' + server + '/' + hash + '.png'
        else:
            return '/static/discord_logo.png'

    def avatarimg(id, avatar):
        if avatar:
            return 'https://cdn.discordapp.com/avatars/' + id + '/' + avatar + '.png'
        else:
            return 'https://cdn.discordapp.com/avatars/147045937754144768'

    return dict(serverimg=serverimg, avatarimg=avatarimg)


def get_user_cache(token, cache):
    if token:
        if token['access_token'] in cache['user']:
            session_token = cache['user'][token['access_token']]
            if token['access_token'] in cache['usertoken']:
                return (session_token, cache['usertoken'][token['access_token']])
            return (session_token, None)
        else:
            return (None, None)
    else:
        return (None, None)


def check_auth(user, usertoken):
    if user is None:
        abort(401, "Missing user")
    if usertoken is None:
        abort(401, "Missing user token")


def run():
    app.config['DB_HOST'] = 'localhost'
    app.config['DB_USER'] = 'tumult'
    app.config['DB_PASS'] = 'tumult-tumult'

    app.run(host='127.0.0.1', port=42424)
