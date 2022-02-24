import psycopg2 as ps
import os


class SQLsubscriptions:

    def __init__(self):
        '''Connecting to database and saving the connection cursor'''
        self.connection = ps.connect(
            os.environ['DATABASE_URL'], sslmode='require')
        self.cursor = self.connection.cursor()

    def get_subscriptions(self, status=True):
        '''Getting all active bot subscribers'''
        self.cursor.execute(
            f'SELECT * FROM subscriptions WHERE status = {True}')
        result = self.cursor.fetchall()
        return result

    def subscriber_exists(self, user_id):
        '''Checking if the user already exists in database'''
        self.cursor.execute(
            f'SELECT user_id FROM subscriptions WHERE user_id = {user_id}')
        result = self.cursor.fetchone()
        return bool(result)

    def add_subscriber(self, user_id, status=True):
        '''Adding a new subscriber'''
        self.cursor.execute(
            'INSERT INTO subscriptions(user_id, status) VALUES (%s, %s)', (user_id, status))
        self.connection.commit()

    def update_subscribtion(self, user_id, status):
        '''Updating subscription status'''
        self.cursor.execute(
            'UPDATE subscriptions SET status= %s WHERE user_id= %s', (status, user_id))
        self.connection.commit()

    def update_last_seen(self, user_id, last_seen):
        '''Updating last seen atricle'''
        self.cursor.execute(
            "UPDATE subscriptions SET last_seen= %s WHERE user_id= %s", (last_seen, user_id))
        self.connection.commit()

    def get_current_article(self, user_id):
        '''Getting current article number'''
        self.cursor.execute(
            "SELECT current FROM subscriptions WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchall()
        return result

    def update_current(self, user_id, current):
        '''Updating current atricle'''
        self.cursor.execute(
            "UPDATE subscriptions SET current= %s WHERE user_id= %s", (current, user_id))
        self.connection.commit()

    def get_subscription_status(self, user_id):
        '''Getting subscription status'''
        self.cursor.execute(
            "SELECT status FROM subscriptions WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()
        return result[0]

    def close(self):
        '''Closing the database connection'''
        self.connection.close()
