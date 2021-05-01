import json

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib import auth
from django.contrib.auth.models import Group, Permission

from loan.models import CustomerProfile, Loan

client = Client()


class TestMixin(TestCase):

    @classmethod
    def create_and_login_new_user(
        cls, login=True, username='newuser',
        email='user@example.com', role="admin"
    ):
        """
        Create a new user and login
        :param login: Boolean to specify if the user must be logged in or not
        """
        User = get_user_model()

        user = User.objects.create(email=email, username=username)
        user.set_password("password")

        if role == "admin":
            user.is_superuser = True
            user.is_staff = True
        elif role == "agent":
            user.is_agent = True
            user.is_staff = True
        elif role == "customer":
            user.is_customer = True

        user.is_active = True
        user.save()

        if login:
            cls.login(user=user)

        return user

    @classmethod
    def login(cls, username=None, user=None):
        User = get_user_model()
        if username:
            user = User.objects.filter(username=username).first()
        if user:
            client.force_login(user)
            user = auth.get_user(client)
            assert user.is_authenticated

    def logout(self):
        """
        Helper method to logout user
        """
        response = client.get('/accounts/logout/')
        self.assertEqual(response.status_code, 302)
        return response


class TestLoan(TestMixin):

    @classmethod
    def setUpClass(cls):
        super(TestLoan, cls).setUpClass()

        cls.test_user1 = cls.create_and_login_new_user(
            username="testuser1", login=False, email='user1@example.com',
            role="customer"
        )
        cls.test_user2 = cls.create_and_login_new_user(
            username="testuser2", login=False, email='user2@example.com',
            role="customer"
        )

        cls.agent_user = cls.create_and_login_new_user(
            username="agent", login=False, email='agent@example.com',
            role="agent"
        )

        cls.admin_user = cls.create_and_login_new_user(
            username="admin", login=False, email='admin@example.com',
            role="admin"
        )

        cls.customer1 = CustomerProfile.objects.create(
            user=cls.test_user1,
            phone=92333333,
            street_address="spring creek",
            zip_code=2301,
            city="noida",
            country="IN",
        )

        cls.customer2 = CustomerProfile.objects.create(
            user=cls.test_user2,
            phone=92333333,
            street_address="springhurst",
            zip_code="lm5632",
            city="noida",
            country="IN",
        )

        cls.loan_customer1 = Loan.objects.create(
            loan_type="home", amount=1000, tenure=5, interest_rate=8,
            customer=cls.customer1
        )

        cls.loan_customer2 = Loan.objects.create(
            loan_type="personal", amount=2000, tenure=5, interest_rate=8,
            customer=cls.customer2
        )

    def test_0010_test_loan_view_api(self):
        """
        Checks view api for loan
        """

        # Check api without login
        response = client.get('/api/loan-requests/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided."
        )

        response = client.get('/api/loan-requests/%d/' % self.loan_customer1.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided."
        )

        # Check with login

        # 1. Login as customer
        self.login(username="testuser1")

        # Customer can only see his own loan requests
        response = client.get('/api/loan-requests/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["loan_requests"]), 1)
        self.assertEqual(
            response.data["loan_requests"][0].id, self.loan_customer1.id
        )

        # Customer can only retrieve his own loan request
        response = client.get('/api/loan-requests/%d/' % self.loan_customer1.id)
        self.assertEqual(response.status_code, 200)

        # Customer can not access loan request that belong to someone else
        response = client.get('/api/loan-requests/%d/' % self.loan_customer2.id)
        self.assertEqual(response.status_code, 404)

        self.logout()

        # 2. Login as a agent
        self.login(username="agent")

        # Agent can see all the loan requests of customers
        response = client.get('/api/loan-requests/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["loan_requests"]), 2)
        self.assertEqual(
            response.data["loan_requests"][0].id, self.loan_customer1.id
        )
        self.assertEqual(
            response.data["loan_requests"][1].id, self.loan_customer2.id
        )

        response = client.get('/api/loan-requests/%d/' % self.loan_customer1.id)
        self.assertEqual(response.status_code, 200)

        response = client.get('/api/loan-requests/%d/' % self.loan_customer2.id)
        self.assertEqual(response.status_code, 200)

        self.logout()

        # 3. Login as a admin
        self.login(username="admin")

        # Admin can see all the loan requests of customers
        response = client.get('/api/loan-requests/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["loan_requests"]), 2)
        self.assertEqual(
            response.data["loan_requests"][0].id, self.loan_customer1.id
        )
        self.assertEqual(
            response.data["loan_requests"][1].id, self.loan_customer2.id
        )

        response = client.get('/api/loan-requests/%d/' % self.loan_customer1.id)
        self.assertEqual(response.status_code, 200)

        response = client.get('/api/loan-requests/%d/' % self.loan_customer2.id)
        self.assertEqual(response.status_code, 200)


    def test_0020_test_create_loan_api(self):
        """
        Check api for submitting loan request
        """

        # Check api without login
        response = client.post(
            '/api/loan-requests/', content_type='application/json',
            data=json.dumps({
                "loan_type": "home", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer1.id
            })
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided."
        )

        # Check with login

        # 1. Login as customer
        self.login(username="testuser1")

        # Customer can only create his own loan request
        response = client.post(
            '/api/loan-requests/', content_type='application/json',
            data=json.dumps({
                "loan_type": "home", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer1.id
            })
        )
       
        self.assertEqual(response.status_code, 302)

        # Customer can not create loan for another customer
        response = client.post(
            '/api/loan-requests/', content_type='application/json',
            data=json.dumps({
                "loan_type": "home", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer2.id
            })
        )
        self.assertEqual(response.status_code, 403)

        self.logout()

        # 2. Login as a agent
        self.login(username="agent")

        # Agent can create loan request for all the customers
        response = client.post(
            '/api/loan-requests/', content_type='application/json',
            data=json.dumps({
                "loan_type": "home", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer1.id
            })
        )
        self.assertEqual(response.status_code, 302)

        response = client.post(
            '/api/loan-requests/', content_type='application/json',
            data=json.dumps({
                "loan_type": "home", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer2.id
            })
        )
        self.assertEqual(response.status_code, 302)

        self.logout()

        # 3. Login as a admin
        self.login(username="admin")

        # Admin can not create loan requests
        response = client.post(
            '/api/loan-requests/', content_type='application/json',
            data=json.dumps({
                "loan_type": "home", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer1.id
            })
        )
        self.assertEqual(response.status_code, 403)

        response = client.post(
            '/api/loan-requests/', content_type='application/json',
            data=json.dumps({
                "loan_type": "home", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer2.id
            })
        )
        self.assertEqual(response.status_code, 403)

    def test_0030_test_edit_loan_api(self):
        """
        Check api for editing loan request
        """

        # Check api without login
        response = client.post(
            '/api/loan-requests/%d/edit/' % self.loan_customer1.id,
            content_type='application/json',
            data=json.dumps({
                "loan_type": "car", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer1.id
            })
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided."
        )

        # Check with login

        # 1. Login as a customer
        self.login(username="testuser1")

        # Customer can not edit any loan request
        response = client.post(
            '/api/loan-requests/%d/edit/' % self.loan_customer1.id,
            content_type='application/json',
            data=json.dumps({
                "loan_type": "car", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer1.id
            })
        )
        self.assertEqual(response.status_code, 403)

        # Customer can not edit loan request for another customer
        response = client.post(
            '/api/loan-requests/%d/edit/' % self.loan_customer1.id,
            content_type='application/json',
            data=json.dumps({
                "loan_type": "car", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer2.id
            })
        )
        self.assertEqual(response.status_code, 403)

        self.logout()

        # 2. Login as a agent
        self.login(username="agent")

        # Agent can edit loan request for all the customers
        response = client.post(
            '/api/loan-requests/%d/edit/' % self.loan_customer1.id,
            content_type='application/json',
            data=json.dumps({
                "loan_type": "car", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer2.id
            })
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Loan.objects.get(id=self.loan_customer1.id).loan_type, "car"
        )

        response = client.post(
            '/api/loan-requests/%d/edit/' % self.loan_customer2.id,
            content_type='application/json',
            data=json.dumps({
                "loan_type": "personal", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer2.id
            })
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Loan.objects.get(id=self.loan_customer2.id).loan_type, "personal"
        )

        # Agent can not edit loan request once its approved
        self.loan_customer1.status = "approved"
        self.loan_customer1.save()

        response = client.post(
            '/api/loan-requests/%d/edit/' % self.loan_customer1.id,
            content_type='application/json',
            data=json.dumps({
                "loan_type": "car", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer2.id
            })
        )
        self.assertEqual(response.status_code, 403)

        self.logout()

        # 3. Login as a admin
        self.login(username="admin")

        # Admin can not edit loan requests
        response = client.post(
            '/api/loan-requests/%d/edit/' % self.loan_customer1.id,
            content_type='application/json',
            data=json.dumps({
                "loan_type": "car", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer1.id
            })
        )
        self.assertEqual(response.status_code, 403)

        response = client.post(
            '/api/loan-requests/%d/edit/' % self.loan_customer2.id,
            content_type='application/json',
            data=json.dumps({
                "loan_type": "car", "amount": 1000, "tenure": 5,
                "interest_rate": 8, "customer": self.customer2.id
            })
        )
        self.assertEqual(response.status_code, 403)

    def test_0040_test_delete_loan_api(self):
        """
        Check api for editing loan request
        """
        # Check api without login
        response = client.delete(
            '/api/loan-requests/%d/' % self.loan_customer1.id,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided."
        )

        # Check with login

        # 1. Login as a customer
        self.login(username="testuser1")

        # Customer can not delete any loan request
        response = client.delete(
            '/api/loan-requests/%d/' % self.loan_customer1.id,
        )
        self.assertEqual(response.status_code, 403)

        response = client.delete(
            '/api/loan-requests/%d/' % self.loan_customer2.id,
        )
        self.assertEqual(response.status_code, 404)

        self.logout()

        # 2. Login as a agent
        self.login(username="agent")

        # Agent can not delete any loan request
        response = client.delete(
            '/api/loan-requests/%d/' % self.loan_customer1.id,
        )
        self.assertEqual(response.status_code, 403)

        response = client.delete(
            '/api/loan-requests/%d/' % self.loan_customer2.id,
        )
        self.assertEqual(response.status_code, 403)

        self.logout()

        # 3. Login as a admin
        self.login(username="admin")

        self.assertEqual(Loan.objects.all().count(), 2)

        # Admin can delete any loan requests
        response = client.delete(
            '/api/loan-requests/%d/' % self.loan_customer1.id,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Loan.objects.all().count(), 1)

        response = client.delete(
            '/api/loan-requests/%d/' % self.loan_customer2.id,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Loan.objects.all().count(), 0)

    def test_0050_test_customer_view_api(self):
        """
        Checks view api for customer
        """

        # Check api without login
        response = client.get('/api/customers/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided."
        )

        response = client.get('/api/customers/%d/' % self.customer1.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided."
        )

        # Check with login

        # 1. Login as customer
        self.login(username="testuser1")

        # Customer can only see his own profile
        response = client.get('/api/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["customers"]), 1)
        self.assertEqual(
            response.data["customers"][0].id, self.customer1.id
        )

        response = client.get('/api/customers/%d/' % self.customer1.id)
        self.assertEqual(response.status_code, 200)

        # Customer can not access any other customer profile
        response = client.get('/api/customers/%d/' % self.customer2.id)
        self.assertEqual(response.status_code, 404)

        self.logout()

        # 2. Login as a agent
        self.login(username="agent")

        # Agent can see all the customers
        response = client.get('/api/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["customers"]), 2)
        self.assertEqual(
            response.data["customers"][0].id, self.customer1.id
        )
        self.assertEqual(
            response.data["customers"][1].id, self.customer2.id
        )

        response = client.get('/api/customers/%d/' % self.customer1.id)
        self.assertEqual(response.status_code, 200)

        response = client.get('/api/customers/%d/' % self.customer2.id)
        self.assertEqual(response.status_code, 200)

        self.logout()

        # 3. Login as a admin
        self.login(username="admin")

        # Admin can see all the customers
        response = client.get('/api/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["customers"]), 2)
        self.assertEqual(
            response.data["customers"][0].id, self.customer1.id
        )
        self.assertEqual(
            response.data["customers"][1].id, self.customer2.id
        )

        response = client.get('/api/customers/%d/' % self.customer1.id)
        self.assertEqual(response.status_code, 200)

        response = client.get('/api/customers/%d/' % self.customer2.id)
        self.assertEqual(response.status_code, 200)

    def test_0060_test_edit_customers_api(self):
        """
        Check api for editing customers
        """

        # Check api without login
        response = client.post(
            '/api/customers/%d/edit/' % self.customer1.id,
            content_type='application/json',
            data=json.dumps({
                "user": self.test_user1.id, "phone": 92333333,
                "street_address": "spring creek", "zip_code": 2301,
                "city": "noida", "country": "IN",
            })
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided."
        )

        # Check with login

        # 1. Login as a customer
        self.login(username="testuser1")

        # Customer can not edit any customer
        response = client.post(
            '/api/customers/%d/edit/' % self.customer1.id,
            content_type='application/json',
            data=json.dumps({
                "user": self.test_user1.id, "phone": 92333333,
                "street_address": "spring creek", "zip_code": 2301,
                "city": "noida", "country": "IN",
            })
        )
        self.assertEqual(response.status_code, 403)

        response = client.post(
            '/api/customers/%d/edit/' % self.customer2.id,
            content_type='application/json',
            data=json.dumps({
                "user": self.test_user2.id, "phone": 92333333,
                "street_address": "spring creek", "zip_code": 2301,
                "city": "noida", "country": "IN",
            })
        )
        self.assertEqual(response.status_code, 403)

        self.logout()

        # 2. Login as a agent
        self.login(username="agent")

        # Agent can edit all the customers
        response = client.post(
            '/api/customers/%d/edit/' % self.customer1.id,
            content_type='application/json',
            data=json.dumps({
                "user": self.test_user1.id, "phone": 123456789,
                "street_address": "spring creek", "zip_code": 2301,
                "city": "noida", "country": "IN",
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            CustomerProfile.objects.get(id=self.customer1.id).phone, '123456789'
        )

        response = client.post(
            '/api/customers/%d/edit/' % self.customer2.id,
            content_type='application/json',
            data=json.dumps({
                "user": self.test_user2.id, "phone": 92333333,
                "street_address": "spring creek", "zip_code": 5555,
                "city": "noida", "country": "IN",
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            CustomerProfile.objects.get(id=self.customer2.id).zip_code, '5555'
        )

        self.logout()

        # 3. Login as a admin
        self.login(username="admin")

        # Admin can edit all the customers
        response = client.post(
            '/api/customers/%d/edit/' % self.customer1.id,
            content_type='application/json',
            data=json.dumps({
                "user": self.test_user1.id, "phone": 903338883,
                "street_address": "spring creek", "zip_code": 2301,
                "city": "noida", "country": "IN",
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            CustomerProfile.objects.get(id=self.customer1.id).phone, '903338883'
        )

        response = client.post(
            '/api/customers/%d/edit/' % self.customer2.id,
            content_type='application/json',
            data=json.dumps({
                "user": self.test_user2.id, "phone": 92333333,
                "street_address": "spring creek", "zip_code": 4444,
                "city": "noida", "country": "IN",
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            CustomerProfile.objects.get(id=self.customer2.id).zip_code, '4444'
        )




    def test_0070_user_signup_as_agent(self):
        """
        Check user singup as an agent
        """
        User = get_user_model()
        response = client.post(
            '/register', {
                "first_name": "lucky", "last_name":"raja", "username":"luckyr14",
                "email":"lraja@ee.iitr.ac.in", "password1":"getshitdone",
                "password2":"getshitdone",
                "role":"agent", "phone": 126777733, "street_address": "test",
                "zip_code": 12223, "city": "noida", "country": "IN"
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="luckyr14").exists())

        user = User.objects.get(username="luckyr14")
        self.assertFalse(user.is_active)
        self.assertTrue(user.is_agent)
        self.assertFalse(user.is_customer)
        self.assertFalse(user.is_staff)
        self.assertTrue(user in Group.objects.get(name="Agent").user_set.all())

        # Try to login with above created user and it should fail
        response = client.post(
            '/accounts/login/', {
                'username': "luckyr14",
                'password': "getshitdone"
            }
        )
        self.assertEqual(response.status_code, 200)

        current_user = auth.get_user(client)
        self.assertFalse(current_user.is_authenticated)

        response = client.get("/api/loan-requests/")
        self.assertEqual(response.status_code, 403)

        # Activate user
        user.is_active = True
        user.save()

        self.assertTrue(user.is_staff)

        # Try to login again and it should work
        response = client.post(
            '/accounts/login/', {
                'username': "luckyr14",
                'password': "getshitdone"
            }
        )
        self.assertEqual(response.status_code, 302)

        current_user = auth.get_user(client)
        self.assertTrue(current_user.is_authenticated)

        response = client.get("/api/loan-requests/")
        self.assertEqual(response.status_code, 200)

    def test_0080_user_signup_as_customer(self):
        """
        Check user singup for customer
        """
        User = get_user_model()
        response = client.post(
            '/register', {
                "first_name": "lucky", "last_name":"raja", "username":"luckyr14",
                "email":"lraja@ee.iitr.ac.in", "password1":"getshitdone",
                "password2":"getshitdone",
                "role":"customer", "phone": 126777733, "street_address": "test",
                "zip_code": 12223, "city": "noida", "country": "IN"
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="luckyr14").exists())

        user = User.objects.get(username="luckyr14")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_agent)
        self.assertTrue(user.is_customer)

        self.assertTrue(CustomerProfile.objects.filter(user=user.id).exists())
        self.assertTrue(user.customer)

       

        # Try to login and it should work
        response = client.post(
            '/accounts/login/', {
                'username': "luckyr14",
                'password': "getshitdone"
            }
        )
        self.assertEqual(response.status_code, 302)

        current_user = auth.get_user(client)
        self.assertTrue(current_user.is_authenticated)

        response = client.get("/api/loan-requests/")
        self.assertEqual(response.status_code, 200)