from datetime import datetime
import json
import os
import sqlite3

from source import source


class db_tracking:

    def __init__(self, name):
        self.name = name
        self.interval_time = 20 * 60

    def initialize(self):
        db_file = self.name + ".db"
        if os.path.exists(db_file):
            print(f"deleting {db_file}...")
            os.remove(db_file)
        print(f"Creating database {db_file}...")
        con = sqlite3.connect(db_file)
        cur = con.cursor()
        print(f"Creating sources table...")
        cur.execute("CREATE TABLE sources(id PRIMARY KEY, method, date, sent, prompt, tweets)")
        con.commit()

    def is_sent(self, source):
        """
        Returns true if a given source has already been tracked as sent,
        otherwise return false
        """
        con = sqlite3.connect(self.name + ".db")
        cur = con.cursor()
        print(f"Checking if {source} was already sent...")
        res = cur.execute("SELECT sent FROM sources WHERE id = ?", (source.id, ))
        (sent, ) = res.fetchone()
        if sent == 1:
            print(f"{source} was already sent")
        else:
            print(f"{source} is pending")
        return sent == 1

    def track_source(self, source):
        """
        Attempt to insert the row on the db, ignore if already exists
        """
        con = sqlite3.connect(self.name + ".db")
        cur = con.cursor()
        # print(f"Making sure source {source} is tracked...")
        cur.execute("INSERT OR IGNORE INTO sources (id, method, date) VALUES (?, ?, ?)", (source.id, source.method, source.date))
        con.commit()

    def set_sent(self, source):
        """
        Track an already handled source into the database so it is not attempted to
        be sent again
        """
        source.sent = 1
        con = sqlite3.connect(self.name + ".db")
        cur = con.cursor()
        print(f"Setting source {source} as sent...")
        cur.execute("UPDATE sources SET sent = 1 WHERE id = ?", (source.id, ))
        con.commit()

    def add_prompt(self, source, prompt):
        """
        Track an already handled source into the database so it is not attempted to
        be sent again
        """
        source.prompt = prompt
        con = sqlite3.connect(self.name + ".db")
        cur = con.cursor()
        print(f"Adding prompt for {source}...")
        cur.execute("UPDATE sources SET prompt = ? WHERE id = ?", (prompt, source.id))
        con.commit()

    def add_tweets(self, source, tweets):
        """
        Track an already handled source into the database so it is not attempted to
        be sent again
        """
        source.tweets = tweets
        con = sqlite3.connect(self.name + ".db")
        cur = con.cursor()
        print(f"Adding tweets for {source} as sent...")
        cur.execute("UPDATE sources SET tweets = ? WHERE id = ?", (json.dumps(source.tweets), source.id))
        con.commit()
