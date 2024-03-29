import pymysql as pymysql

getMessagesByChannelSQL = "SELECT * FROM `messages` WHERE (channel_id=%s) ORDER BY timestamp DESC"
insertMessagesSQL = "INSERT INTO `messages`" \
                    "(`id`, `guild_id`, `channel_id`, `author_id`, `content`, `timestamp`, `author_username`, `author_discriminator`, `avatar`)" \
                    " VALUES " \
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
getLastMessageSQL = "SELECT * FROM `messages` WHERE (channel_id=%s) ORDER BY timestamp DESC LIMIT 1"
getFirstMessageSQL = "SELECT * FROM `messages` WHERE (channel_id=%s) ORDER BY timestamp ASC LIMIT 1"

getChannelUserSQL = "SELECT DISTINCT author_id FROM tumult.messages WHERE (channel_id=%s);"


class MySQL:
    def __init__(self, host, user, password, dbname='tumult'):
        self.host = host
        self.user = user
        self.password = password
        self.dbname = dbname
        self.typeName = {}

    def connect(self):
        self.tumult = pymysql.connect(host=self.host,
                                    user=self.user,
                                    password=self.password,
                                    db=self.dbname,
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)

    def getMessages(self, channelId):
        with self.tumult.cursor() as tumult:
            tumult.execute(getMessagesByChannelSQL, channelId)
            return tumult.fetchall()

    def insertMessages(self, messages):
        with self.tumult.cursor() as tumult:
            tumult.executemany(insertMessagesSQL, messages)
        self.tumult.commit()

    def getLastMessage(self, channelId):
        with self.tumult.cursor() as tumult:
            tumult.execute(getLastMessageSQL, channelId)
            return tumult.fetchone()

    def getFirstMessage(self, channelId):
        with self.tumult.cursor() as tumult:
            tumult.execute(getFirstMessageSQL, channelId)
            return tumult.fetchone()

    def getChannelUsers(self, channelId):
        with self.tumult.cursor() as tumult:
            tumult.execute(getChannelUserSQL, channelId)
            return tumult.fetchone()