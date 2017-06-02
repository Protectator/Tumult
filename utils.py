import re

def filterMentionMessages(message):
    fil = re.compile('<@([0-9]+)>')
    return fil.search(message['content'])

def getMentionMessages(messages):
    return filter(filterMentionMessages, messages)

def getMentionId(message):
    fil = re.compile('<@([0-9]+)>')
    t = fil.match(message['content'])
    return t.groups(1)