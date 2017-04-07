#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of Tumult.
"""
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

global repos

# Routes

@app.route("/")
def root():
    return render_template("layout.html", contentTemplate="repos.html", servers=app.config['REPOS'])

@app.route("/oauth")
def oauth():
    token = request.args.get('code')
    url = 'https://discordapp.com/api/users/@me/guilds'
    servers = requests.get(url, headers={"Authorization": "Bearer " + token})
    return render_template("layout.html", contentTemplate="index.html", servers=app.config['REPOS'])

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
    app.run(host='127.0.0.1', port='42424')
