# Tumult

## 1. Contexte et objectifs du projet
**Tumult** was created to better understand the various interactions that one can have with the members of his **Discord** community. Discord is a freeware proprietary VoIP application designed for gaming communities. Discord runs on Microsoft Windows, macOS, Android, iOS, Linux, and in a web browser. As of May 2017, Discord has over 45 million users. Is like a teamspeak/skype fusion. **Tumult** shows statistics about comments Discord messages. (e.g. Who answers who, number of messages between people,...)

## 2. Données (sources, quantité, évtl. pré-traitement, description)
Datasource: your own discord account. **Tumult** will aggregate in real time a defined number of messages from various channels chosen by the user. The quantity can therefore vary depending on the number of channel, messages related to your account. These messages will then be stored in a mySQL database so you do not have to download them again. No pre-processing is done on the data.

A message has the following characteristics:
* id : id of the message
* guild_id : the id of the guild
* channel_id : id of the channel the message was sent in
* author_id : the author's id of this message 
* content : contents of the message
* timestamp : when this message was sent
* author_username : the user's username, not unique across the platform
* avatar : the user's avatar hash

## 3. Planification, répartition du travail

## 4. Fonctionnalités / cas d’utilisation

## 5. Techniques, algorithmes et outils utilisés

## 6. Conclusion




## Requirements

- [Python 3](https://www.python.org/)
- [pip3](https://pip.pypa.io/en/stable/installing/)

## Installing

In the root directory of the project, run

``pip3 install -r requirements.txt`` (or maybe ``pip install -r requirements.txt``)

## Usage

Run `tumult.py` with python 3, typically : `python3 tumult.py`
