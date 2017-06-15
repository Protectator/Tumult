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
**05.05**
* Technology selection
* Design Choices
* Start programming

**12.05**
* Web application logic
* Creation of various roads
* Creating the database structure

**19.05**
* Implementation of the communication mechanism (OAuth2) with Discord
* Creating the message retrieval mechanism
* Creating algorithms for message analysis

**26.05**
* Implementation of graphs and visualization of results
* Bug fix
 
**02.06**
* Documentation
* Bug fix

We have both worked on the application developpement. Vincent create the network part (logic and vizalisation) and Kewin the OAuth2 authentification and graph part. 

## 4. Fonctionnalités / cas d’utilisation
The user can:
* Connect its account Discord to the application 
* get back a number of message defines in a specific channel.
* visualize (table, network, graph) the interactions between the diverse members of his channels.


## 5. Techniques, algorithmes et outils utilisés
We have created an algorithm allowing us to retrieve the responses of the various messages in order to know who communicates with whom.

We also implemented a word count algorithm to know the most used word for each conversation. This word count remove two specific list of stop word for the english and french languages.

Regarding the tool, we used a mySQL database to store messages. GitHub for the versionning of the project. Python as programmation language. Flask as web framework for our application. Jinja2 as template engine for our web pages. The discord API in order to interact with Discord. Viz.js for rendering the network and graph.

## 6. Conclusion
This project was very interesting. He gave us the opportunity to use the Discord API with which we were not familiar. For Vincent it was also an opportunity to use the Flask framework for the first time. We had to face some difficulty like not being able to retrieve all the messages at once. But we were able to set up a mechanism to bypass this problem. We are satisfied with our result.



## Requirements

- [Python 3](https://www.python.org/)
- [pip3](https://pip.pypa.io/en/stable/installing/)

## Installing

In the root directory of the project, run

``pip3 install -r requirements.txt`` (or maybe ``pip install -r requirements.txt``)

## Usage

Run `tumult.py` with python 3, typically : `python3 tumult.py`
