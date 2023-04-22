from datetime import datetime
import json
import os
import sqlite3

from source import source


class db_tracking:

    def __init__(self, name):
        """
        db_tracking constructor
        """
        self.name = name
        self.interval_time = 20 * 60
        self.max_errors = 3
        # Make sure the database has the latest schema
        if os.path.exists(self.name + ".db"):
            self._update_schema()

    def _connect(self):
        """
        Connect to the database and returns a cursor ready for querying.
        If the file doesn't exist, it is auto-created.
        """
        db_file = self.name + ".db"
        con = sqlite3.connect(db_file)
        cur = con.cursor()
        return cur, con

    def _update_schema(self):
        """
        Make sure the database has the latest schema
        """
        cur, con = self._connect()

        # add "errors" column to sources table with default value 0
        columns = [i[1] for i in cur.execute('PRAGMA table_info(sources)')]
        if 'errors' not in columns:
            print("Adding new column errors to table sources...")
            cur.execute('ALTER TABLE sources ADD COLUMN errors')
            cur.execute('UPDATE sources SET errors = 0')
            con.commit()

    def initialize(self):
        """
        Creates the database and the empty schema with all tables
        """
        db_file = self.name + ".db"
        if os.path.exists(db_file):
            print(f"deleting {db_file}...")
            os.remove(db_file)
        print(f"Creating database {db_file}...")
        cur, con = self._connect()
        print(f"Creating sources table...")
        cur.execute("CREATE TABLE sources(id PRIMARY KEY, method, date, sent, prompt, tweets, errors)")
        con.commit()

    def is_sent(self, source):
        """
        Returns true if a given source has already been tracked as sent or has too many errors,
        otherwise return false
        """
        cur, con = self._connect()
        print(f"Checking if {source} was already sent...")
        res = cur.execute("SELECT sent, errors FROM sources WHERE id = ?", (source.id, ))
        (sent, errors) = res.fetchone()
        if sent == 1:
            print(f"{source} was already sent")
            return True
        elif errors >= self.max_errors:
            print(f"{source} has two many errors: {errors}")
            return True
        else:
            print(f"{source} is pending")
            return False

    def track_source(self, source):
        """
        Attempt to insert the row on the db, ignore if already exists
        """
        cur, con = self._connect()
        # print(f"Making sure source {source} is tracked...")
        cur.execute("INSERT OR IGNORE INTO sources (id, method, date, errors) VALUES (?, ?, ?, ?)", (source.id, source.method, source.date, 0))
        con.commit()

    def set_sent(self, source):
        """
        Track an already handled source into the database so it is not attempted to
        be sent again
        """
        source.sent = 1
        cur, con = self._connect()
        print(f"Setting source {source} as sent...")
        cur.execute("UPDATE sources SET sent = 1 WHERE id = ?", (source.id, ))
        con.commit()

    def add_error(self, source):
        """
        Add that an error was returned whe trying to track the given source
        """
        cur, con = self._connect()
        print(f"Adding a new error for {source}...")
        cur.execute("UPDATE sources SET errors = errors + 1 WHERE id = ?", (source.id, ))
        con.commit()

    def add_prompt(self, source, prompt):
        """
        Track an already handled source into the database so it is not attempted to
        be sent again
        """
        source.prompt = prompt
        cur, con = self._connect()
        print(f"Adding prompt for {source}...")
        cur.execute("UPDATE sources SET prompt = ? WHERE id = ?", (prompt, source.id))
        con.commit()

    def add_tweets(self, source, tweets):
        """
        Track an already handled source into the database so it is not attempted to
        be sent again
        """
        source.tweets = tweets
        cur, con = self._connect()
        print(f"Adding tweets for {source} as sent...")
        cur.execute("UPDATE sources SET tweets = ? WHERE id = ?", (json.dumps(source.tweets), source.id))
        con.commit()
