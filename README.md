# Tumult

# 0. Running the project 

## Requirements

- [Python 3](https://www.python.org/)
- [pip3](https://pip.pypa.io/en/stable/installing/)

## Installing

In the root directory of the project, run

``pip3 install -r requirements.txt`` (or maybe ``pip install -r requirements.txt``)

## Usage

Run `tumult.py` with python 3, typically : `python3 tumult.py`

## 1. Project context and objectives
**Tumult** was created to better understand the various interactions that one can have with the members of his **Discord** community. Discord is a freeware proprietary VoIP application designed for gaming communities. Discord runs on Microsoft Windows, macOS, Android, iOS, Linux, and in a web browser. As of May 2017, Discord has over 45 million users. Is like a teamspeak/skype fusion. **Tumult** shows statistics about Discord messages in servers and channels you're in. (e.g. Who answers who, number of messages between people,...)

## 2. Data
### Source
The Discord servers of the user, and the servers he're into. After asking to connect to the user's account, **Tumult** will allow him to aggreagate in real time messages from channels. Tumult communicates with the Discord API in two ways :
- Using the usual token recieved from the Discord's OAuth connection window : This lets Tumult know your account, avatar etc. However, by using the API that way, Tumult wouldn't be able to read messages from channels, and thus be unable to function entirely.
- Using a usertoken provided by the user : Complementary to the OAuth token, Tumult requires a usertoken in order to read messages from the user's servers and channels. It could also have been possible to register Tumult as a "Bot account" at Discord API, but this would have meant that Tumult only works on the servers the user *administrates*, which  reduces the target population by a lot.

### Quantity
The quantity can therefore vary depending on the number of channel, messages related to your account. These messages will then be stored in a mySQL database so that the download and API calls only happens once. Not much pre-processing is done on the data here : Mainly separating the different fields into different columns of the MySQL table.

### Description
The API gives us lists of between 50 and 100 messages. Each message is stored in the database with all relevant information for later use.

A message has the following characteristics:
* id : id of the message
* guild_id : the id of the guild
* channel_id : id of the channel the message was sent in
* author_id : the author's id of this message 
* content : contents of the message
* timestamp : when this message was sent
* author_username : the user's username, not unique across the platform
* avatar : the user's avatar hash

## 3. Planning and distribution of work

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
* Last part of the implementation of visualizations
* Bug fix
 
**09.06**
* Documentation
* Bugs fix

We both worked on the application developement. Vincent worked on  the network part and Kewin worked on the OAuth2 authentification and time graph part. 

## 4. Features / Use cases
After asking to connect to your account, **Tumult** will show the user an interface to choose the server he wants informations from. Once selected, he can ask to aggregate in real time a defined number of messages from a channels of the server.
**Tumult** :
* Shows a list of servers the user participates to
* Lists visible channels of these servers
* Produces visualisations about any channel :
  - A table showing who answered to who's messages
  - A time graph showing the general activity of the channel and everyone's contribution.
  - A network graph showing the most frequent flow of conversations between participants, and the most used word by them.
  
The main use case for this application is to visualize and better understand the interactions and discussions that happen between the members of any server.

## 5. Techniques, algorithms and tools

### Algorithms

We have implemented an algorithm that allows us to retrieve the responses of the various messages in order to know who communicates with who. The algorithm is simple : If user X sends a message after user Y, we consider that this message is an answer from Y to X, and thus X sent this message to Y. This will be then represented by an arrow on the network graph going from X to Y.

We also implemented a word count algorithm to looks for the most used word in each conversation. This word count removes words contained in two list of stop words, once for the english and one for the french languages.

Most of the computing happens on the server part. It aggregates data from the database, and performs the tasks to produce a json containing the data necessary for the table, the time graph and the network graph to show on the base.

### Tools & technologies

On a general note, we used git + GitHub to manage versioning of the project.

#### Backend

The backend is mainly composed by the database management system which is **MySQL**, and the application's logiuc which we wrote in **Python 3**. More precisely, we used the following tools :

- Flask : Framework for developing web servers in Python rapidly.
- Jinja2 : Templating engine for creating models of HTML pages.
- MySQL : Database Management System. Used to store messages from the API.

#### Frontend

The frontend part is composed of a few popular libs :

- Bootstrap 4 : Collection of CSS styles and some JS scripts to style the page
- Vis.JS : Libary to draw network graphs.
- HighStock : Library to draw highly customizable time graphs.

## 6. Conclusion

This project was very interesting. He gave us the opportunity to use the Discord API with which we were not familiar. For Vincent it was also an opportunity to use the Flask framework for the first time. We had to face some difficulty like not being able to retrieve all the messages at once. But we were able to set up a mechanism to bypass this problem. We are satisfied with our result.
