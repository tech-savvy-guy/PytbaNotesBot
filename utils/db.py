import sqlite3
import logging

class Db:
    def __init__(self, name) -> None:
        self.name = name
        self.logger = logging.getLogger('LOGGER-SQLITE3')
        self.logger.setLevel(logging.INFO)

    def __conn(self):
        self.conn = sqlite3.connect(self.name)
        self.cur = self.conn.cursor()
    def __close(self):
        self.conn.close()

    def query(self, text, *args, commit = False):
        self.__conn()
        self.cur.execute(text, args)
        if commit:
            self.conn.commit()
        self.__close()
    
    def select(self, text, *args):
        self.__conn()
        self.cur.execute(text, args)
        a = self.cur.fetchall()
        self.__close()
        return a

