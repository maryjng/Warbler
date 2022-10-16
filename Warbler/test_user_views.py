"""User View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        # User.query.delete()
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

        db.session.commit()

    def tearDown(self):
        db.session.rollback()


    def test_likes_view_logged_in(self):
        """Does user see their liked messages when logged in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

        resp = c.get("/users/1/likes")
        html = resp.get_data(as_text=True)

        #Check success
        self.assertEqual(resp.status_code, 200)
        self.assertIn("<h2>testuser's Liked Messages</h2>", html)


    def test_likes_view_logged_out(self):
        """Does user not see their liked messages when not logged in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
        resp = c.get("users/1/likes")

        #should redirect
        self.assertEqual(resp.status_code, 302)



    def test_followers_view_logged_in(self):
        """"Does user see their followers when logged in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

        resp = c.get("/users/1/followers")
        html = resp.get_data(as_text=True)

        #Check success
        self.assertEqual(resp.status_code, 200)


    def test_followers_view_logged_out(self):
        """Does user not see their followers when not logged in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

        resp = c.get("users/1/followers")

        #should redirect
        self.assertEqual(resp.status_code, 302)


    def test_logged_in_follow(self):
        """Does user 1 successfully follow user 2 when logged in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

        resp = c.post("users/follow/2")

        #check if user2.following now has user1
        user2 = User.query.get(2)
        self.assertIn(user2.following, self.testuser1)
    #
    # def test_logged_out_follow(self):
    #     """Does user fail to follow user 2 when not logged in?"""
    #
    #     resp = c.post("users/follow/2")
    #
    #     #user 1 shouldn't be in user2.following.
    #     user2 = User.query.get(2)
    #     self.assertNotIn(user2.following, 1)


    def test_success_unfollow(self):
        """Does user 1 successfully unfollow user 2 when logged in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

        c.post("users/follow/2")

        #submit unfollow
        resp = c.post("/users/stop-following/2")

        #confirm user2.following no longer has user 1
        user2 = User.query.get(2)
        self.assertNotIn(user2.following, 1)

    def test_delete_user(self):
        """Does user 1 successfully delete it's account when logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

        #should redirect to signup page
        resp = c.post("/users/delete")
        self.assertEqual(resp.status_code, 302)
        #query for user 1 should not return it
        user = User.query.get(1)
        self.assertNotEqual(user, self.testuser1)
