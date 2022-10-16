"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(username="testuser1",
                                    email="test1@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

        #testuser1's message
        self.testmessage = Message(text="test message",
                                    timestamp="2022-08-09 12:34:00.000",
                                    user_id=1)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")


    def test_like_message(self):
        """Can the current user like a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2.id

        #like user 1's message as user 2
        resp = c.post("messages/1/like")
        #user 2's likes should not include the message
        user = User.query.get(2)
        self.assertIn(self.testmessage, user.likes)


    def test_like_own_message(self):
        """Does the current user fail to like it's own message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

        #try liking testuser1's message as testuser1
        resp = c.post("messages/1/like")
        #expect the message not to show up in testuser1's likes
        user = User.query.get(1)
        self.assertNotIn(self.testmessage, user.likes)


    def test_delete_own_message(self):
        """Can the user successfully delete it's own message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

        resp = c.post("messages/1/delete")
        #since message shouldn't exist anymore, querying it does not give a matching result to initial message
        msg = Message.query.get(1)
        self.assertNotEqual(msg, self.testmessage)
        #should redirect user to /users/{g.user.id}
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, "http://localhost/users/1")


    def test_delete_other_message(self):
        """Does a user fail to delete another user's message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2.id

        resp = c.post("messages/1/delete")

        #message should still exist
        msg = Message.query.get(1)
        self.assertEqual(msg, self.testmessage)
        #should redirect to /messages/{message_id}
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, "http://localhost/messages/1")
