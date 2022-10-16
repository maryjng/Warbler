""" Message model tests"""

import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup(username="testuser1", email="test1@test.com", password="HASHED_PASSWORD", image_url=None)
        u1id = 1
        u1.id = u1id

        db.session.commit()

        u1 = User.query.get(u1id)
        self.u1 = u1
        self.u1_id = u1id

        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="test message",
            timestamp="2022-08-09 12:34:00.000",
            user_id= self.u1_id
            )

        db.session.add(m)
        db.session.commit()

        #User 1 should now have one message
        self.assertEqual(len(self.u1.messages), 1)

        m_test = Message.query.get(1)

        #Check that message saved properly
        self.assertEqual(m_test.id, 1)
        self.assertEqual(m_test.text, "test message")
        self.assertEqual(m_test.timestamp, "2022-08-09 12:34:00.000" or datetime.datetime(2022, 8, 9, 12, 34))
        self.assertEqual(m_test.user_id, 1)
