"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from flask_bcrypt import Bcrypt

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup(username="testuser1", email="test1@test.com", password="HASHED_PASSWORD", image_url=None)
        u1id = 1
        u1.id = u1id

        u2 = User.signup(username="testuser2", email="test2@test.com", password="MASHED_PASSWORD", image_url=None)
        u1id = 2
        u2.id = u2id

        db.session.commit()

        u1 = User.query.get(u1id)
        self.u1 = u1
        self.u1_id = u1id

        u2 = User.query.get(u2id)
        self.u2 = u2
        self.u2_id = u2id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)


    def test_repr_method(self):
        """Does user model's __repr__ method work?"""

        self.assertEqual(self.u1, "User #1: testuser, test@test.com")


    def test_is_following_user_method(self):
        """Does user is_following method work when user1 is following user2?"""

        self.assertEqual(len(self.u1.following), 0)
        self.assertFalse(u1.is_following(self.u2))

        self.u1.following.append(self.u2)
        self.assertEqual(len(self.u1.following), 1)
        self.assertTrue(self.u1.is_following(self.u2))


    def test_is_followed_by_user_method(self):
        """Does user is_followed_by method work when user1 is following user2?"""

        self.assertEqual(len(self.u2.followers), 0)
        self.assertFalse(self.u2.is_followed_by(self.u1))

        u2.following.append(self.u2)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertTrue(u2.is_followed_by(self.u1))


    def test_user_signup_valid(self):
        """Does User.signup successfully create new user with valid credentials?"""

        user = User.signup(username="testuser1", email="test@test.com", password="HASHED_PASSWORD")
        uid = 4
        user.id = uid

        test_hash = bcrypt.generate_password_hash("HASHED_PASSWORD").decode('UTF-8')

        test = User.query.get(uid)
        self.assertEqual(test.username, "testuser1")
        self.assertEqual(test.email, "test@test.com")
        self.assertNotEqual(test.password, "HASHED_PASSWORD")
        self.assertEqual(test.password, test_hash)


    def test_user_signup_invalid(self):
        """Does User.signup not work if invalid credentials are given?"""

        #expect duplicate username failure
        self.assertFalse(User.signup(username="testuser1", email="test@gmail.com", password="HASHED_PASSWORD"))
        #expect duplicate email failure
        self.assertFalse(User.signup(username="testuser4", email="test@test.com", password="HASHED_PASSWORD"))
        #expect missing email/password failure
        self.assertFalse(User.signup(username="testuser4", email="", password=""))


    def test_authenticate_user(self):
        """Does User.authenticate return a user when given a valid username and pw?"""

        #expect user object equal to u1 to be returned on success
        self.assertEqual(self.u1, User.authenticate(username="testuser1", password="HASHED_PASSWORD"))

    def test_authenticate_username_fail(self):
        """Does User.authenticate return false when given invalid username/pw?"""

        self.assertFalse(User.authenticate(username="testuser1", password="wrongpassword"))
