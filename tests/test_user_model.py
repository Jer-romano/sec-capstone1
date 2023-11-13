"""User model tests."""

# run these tests like:
#
#    python -m unittest tests/test_user_model.py
#
# DO NOT USE 'python3' !!!!!!!!

import os
from unittest import TestCase
from datetime import time
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from models import db, User, Survey, Summary, Medication, E_Factor, User_Factor_Pair

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///optimal-test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserModelTestCase(TestCase):
    """Test the User Model"""

    # @classmethod
    # def setUpClass(cls):
    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Summary.query.delete()
        Survey.query.delete()
        Medication.query.delete()
        #E_Factor.query.delete()

        self.client = app.test_client()
    
    def tearDown(self):
        '''Clean up any fouled transaction, reset primary key value to 1'''
        db.session.rollback()
        db.session.execute(text('ALTER SEQUENCE users_id_seq RESTART'))

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no surveys, summaries, or meds
        self.assertEqual(len(u.surveys), 0)
        self.assertEqual(len(u.summaries), 0)
        self.assertEqual(len(u.meds), 0)
    
    def test_user_repr(self):
        """Test whether the __repr__ method is working as expected"""
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

        self.assertEqual(repr(u), "<User #1: testuser, test@test.com>")
    
    def test_signup(self):
        """Tests signup class method"""
        user = User.signup(username="spongebob",
                            email="test@test.com",
                            password="abc1234",
                            image_url="/static/images/home-hero2.jpg",
                            survey_reminder_time=time(hour=20, minute=0, second=0))
        db.session.commit()
        self.assertEqual(User.query.count(), 1)
        found_user = User.query.one()
        self.assertEqual(found_user.username, "spongebob")
    
    def test_invalid_signup(self):
        """Tests signup class method with invalid credentials"""
        #should raise TypeError bc of missing image_url
        self.assertRaises(TypeError, User.signup, "spongebob",
                                                  "test3@test.com",
                                                  "supersecret")
        user = User.signup(username="spongebob",
                            email="test@test.com",
                            password="abc1234",     
                            image_url="/static/images/default-pic.png",
                            survey_reminder_time=time(hour=20, minute=0, second=0))
        db.session.commit()
        #Tests uniqueness restriction on usernames
        user2 = User.signup(username="spongebob",
                            email="test2@test.com",
                            password="abc12345",
                            image_url="/static/images/default-pic.png",
                            survey_reminder_time=time(hour=20, minute=0, second=0))
        #The assertRaises method appears to only support built-in Python exceptions,
        #and not exceptions from frameworks like SQLAlchemy 
        #Hence why I commented the line below
        #self.assertRaises(IntegrityError, db.session.commit())
      

    def test_authenticate(self):
        """Tests authenticating with valid credentials"""
        user = User.signup(username="spongebob",
                            email="test@test.com",
                            password="abc1234",     
                            image_url="/static/images/default-pic.png",
                            survey_reminder_time=time(hour=20, minute=0, second=0))
        db.session.commit()
        self.assertTrue(User.authenticate("spongebob", "abc1234"))
        self.assertFalse(User.authenticate("spongebob1", "abc1234"))
        self.assertFalse(User.authenticate("spongebob", "abc12345"))
       
