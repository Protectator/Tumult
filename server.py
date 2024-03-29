#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of Tumult.
"""
import calendar
import os

import datetime
import utils

import re
from collections import Counter
import requests
import time
import random
import colorsys
from nltk.corpus import stopwords

from builtins import int

from mysql import MySQL
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, abort, current_app
from requests_oauthlib import OAuth2Session

from utils import getFrenchStopsWords, getEnglishStopsWords

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

@app.route("/server-info/<guildId>", defaults={'channelId': None})
@app.route("/server-info/<guildId>/<channelId>")
def serverInfo(guildId, channelId):
    # Auth and session
    token = session.get('oauth2_token')
    (user, usertoken) = get_user_cache(token, cache)
    check_auth(user, usertoken)

    channelId = channelId if (channelId != None) else guildId

    mysqldb = MySQL(current_app.config['DB_HOST'], current_app.config['DB_USER'], current_app.config['DB_PASS'])
    mysqldb.connect()
    messages = mysqldb.getMessages(channelId)
    nbMessages = len(messages)

    # API calls
    headers = {'authorization': usertoken}
    channel = requests.get(API_BASE_URL + '/channels/' + channelId, headers=headers).json()
    guild    = requests.get(API_BASE_URL + '/guilds/' + guildId, headers=headers).json()
    channels = requests.get(API_BASE_URL + '/guilds/' + guildId + '/channels', headers=headers).json()
    cache['guilds'][guildId] = guild

    guild = cache['guilds'][channel['guild_id']]
    data = {
        'guildId': guildId,
        'channelId': channelId,
        'channels': channels
    }

    channelinfos = {
        'nbmessages' : nbMessages,
        'nbchannels' : 0,
        'firstmessage' : mysqldb.getFirstMessage(channelId),
        'lastmessage' : mysqldb.getLastMessage(channelId)
    }

    # Compute things

    # Render
    return render_template("layout.html", contentTemplate="server-info.html", user=user, server=guild, data=data, channelinfos=channelinfos)


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

    nbMessagesStr = request.args.get('number')
    if nbMessagesStr is not None:
        nbMessagesLeft = int(request.args.get('number'))
    else:
        nbMessagesLeft = 100
    if nbMessagesLeft < 0:
        nbMessagesLeft = 100
    if nbMessagesLeft > 1000:
        nbMessagesLeft = 1000

    # API calls
    headers = {'authorization': usertoken}

    first = True

    while nbMessagesLeft > 0:
        if not first:
            time.sleep(1)
        first = False
        nbToTake = nbMessagesLeft
        if nbMessagesLeft > 100:
            nbToTake = 100

        lastMessageId = mysqldb.getLastMessage(channelId)
        if lastMessageId is None:
            channel = requests.get(API_BASE_URL + '/channels/' + channelId, headers=headers).json()
            params = {'around': int(channel['last_message_id']), 'limit': nbToTake}
        elif way == 'after':
            lastMessageId = mysqldb.getLastMessage(channelId)
            params = {'after': int(lastMessageId['id']), 'limit': nbToTake}
        elif way == 'before':
            firstMessageId = mysqldb.getFirstMessage(channelId)
            params = {'before': int(firstMessageId['id']), 'limit': nbToTake}
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

        nbMessagesLeft -= nbToTake

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

    # main logic
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
    contentMessages = {}
    days = {}
    dayMember = {}
    mostWord = {}

    for author in count:
        dayMember[author] = {}

    for i in range(1, len(messages)):
        # graph
        key = (messages[i]['author_id'],messages[i-1]['author_id'])
        if key in labels:
            labels[key] += 1
            contentMessages[key]+= (" \n " + messages[i]['content'])
        else:
            labels[key] = 1
            contentMessages[key] = messages[i]['content']
        # time
        timestamp = messages[i]['timestamp']
        d = datetime.date(timestamp.year, timestamp.month, timestamp.day)
        timeKey = calendar.timegm(d.timetuple())
        member = messages[i]['author_id']
        if (timeKey in dayMember[member]):
            dayMember[member][timeKey] += 1
        else:
            dayMember[member][timeKey] = 1
        if (timeKey in days):
            days[timeKey] += 1
        else:
            days[timeKey] = 1

    # --- WORD COUNT ---
    for contentMessage in contentMessages:
        msg = contentMessages[contentMessage]
        words = msg.split()
        filteredEN_words = [word for word in words if word not in getEnglishStopsWords()]
        filteredFR_words = [word for word in filteredEN_words if word not in getFrenchStopsWords()]

        word_counts = Counter(filteredFR_words)
        num_words = sum(word_counts.values())

        lst = [(value, key) for key, value in word_counts.items()]
        lst.sort(reverse=True)

        if len(lst) > 0:
            mostWord[contentMessage] = lst[0]
        else:
            mostWord[contentMessage] = ''



    dayList = {}
    for member in dayMember:
        dayList[member] = []
        daysSorted = sorted(dayMember[member])
        for day in daysSorted:
            dayList[member].append([day*1000, dayMember[member][day]])



    for label in labels:
        edge = {
            'from': label[0],
            'to': label[1],
            'arrows': 'to',
            'label' : mostWord[label][1] if (len(mostWord[label]) >= 2) else '',
            'value': labels[label]
        }
        edges.append(edge)


    # Render
    json = {
        'nodes': nodes,
        'edges': edges,
        'days': dayList
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
