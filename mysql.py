import pymysql as pymysql

getMessagesByChannelSQL = "SELECT * FROM `messages` WHERE (channel_id=%s) ORDER BY timestamp DESC"
insertMessagesSQL = "INSERT INTO `messages`" \
                    "(`id`, `guild_id`, `channel_id`, `author_id`, `content`, `timestamp`, `author_username`, `author_discriminator`, `avatar`)" \
                    " VALUES " \
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
getLastMessageIdSQL = "SELECT id FROM `messages` WHERE (channel_id=%s) ORDER BY timestamp DESC LIMIT 1"
getFirstMessageIdSQL = "SELECT id FROM `messages` WHERE (channel_id=%s) ORDER BY timestamp ASC LIMIT 1"


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

    def getLastMessageId(self, channelId):
        with self.tumult.cursor() as tumult:
            tumult.execute(getLastMessageIdSQL, channelId)
            return tumult.fetchone()

    def getFirstMessageId(self, channelId):
        with self.tumult.cursor() as tumult:
            tumult.execute(getFirstMessageIdSQL, channelId)
            return tumult.fetchone()