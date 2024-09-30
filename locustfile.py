from locust import HttpUser, TaskSet, task, between
import random
from datetime import datetime

class UserBehavior(TaskSet):
    def on_start(self):
        """
        Called when a simulated user starts.
        We'll simulate user login here and store the user_id for subsequent requests.
        """
        self.user_id = f"user_{random.randint(1000, 9999)}"
        self.email = f"{self.user_id}@example.com"
        self.login()

    def login(self):
        # Simulate user login
        login_data = {
            'user_id': self.user_id,
            'email': self.email,
            'username': 'testuser',
            'profileUrl': ''
        }
        with self.client.post("/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Login failed: {response.text}")

    @task(1)
    def home(self):
        # Access the home endpoint
        self.client.get("/")

    @task(2)
    def complete_profile(self):
        # Simulate completing user profile
        profile_data = {
            'user_id': self.user_id,
            'email': self.email,
            'username': 'testuser',
            'profileUrl': '',
            'level': '200',
            'flatNo': '12B',
            'street': 'Main Street',
            'city': 'Anytown',
            'state': 'Anystate',
            'postalCode': '12345',
            'phone': '555-1234',
            'department': 'Engineering'
        }
        self.client.post("/complete-profile", json=profile_data)

    @task(3)
    def get_books(self):
        # Fetch books relevant to the user
        params = {'userId': self.user_id}
        self.client.get("/getbooks", params=params)

    @task(2)
    def find_books(self):
        # General book search
        self.client.get("/findbooks")

    @task(1)
    def add_to_wishlist(self):
        # Add a random book to the wishlist
        data = {
            'userId': self.user_id,
            'bookId': random.randint(1, 100)  # Assuming book IDs range from 1 to 100
        }
        self.client.post("/addToWishlist", json=data)

    @task(1)
    def get_wishlist(self):
        # Retrieve the user's wishlist
        params = {'userId': self.user_id}
        self.client.get("/getWishlist", params=params)

    @task(1)
    def remove_from_wishlist(self):
        # Remove a random book from the wishlist
        params = {
            'userId': self.user_id,
            'bookId': random.randint(1, 100)
        }
        self.client.delete("/removeFromWishlist", params=params)

    @task(1)
    def update_user(self):
        # Update user profile information
        update_data = {
            'userId': self.user_id,
            'username': 'updateduser',
            'profileUrl': '',
            'level': '300',
            'postal_code': '54321',
            'phone': '555-4321',
            'department': 'Science',
            'flat_no': '34C',
            'city': 'New City',
            'street': 'Second Street',
            'state': 'New State'
        }
        self.client.put("/updateuser", json=update_data)

    @task(1)
    def purchase(self):
        # Simulate making a purchase
        purchase_data = {
            'customer_name': 'Test User',
            'address': '123 Test Lane',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'purchasedDetails': {
                'userId': self.user_id,
                'bookId': random.randint(1, 100),
                'price': round(random.uniform(10.0, 100.0), 2),
                'paymentMethod': 'Credit Card'
            },
            'purchases': [
                {
                    'book_code': f"BOOK{random.randint(100, 999)}",
                    'quantity': random.randint(1, 5),
                    'unit_price': round(random.uniform(10.0, 100.0), 2),
                    'total_price': round(random.uniform(10.0, 500.0), 2)
                }
            ],
            'method': {
                'type': 'Credit Card',
                'account_name': 'Test User',
                'account_number': '1234567890',
                'pay_by': 'Online'
            }
        }
        self.client.post("/purchase", json=purchase_data)

    @task(1)
    def get_purchase_summary(self):
        # Get the user's purchase summary
        params = {'userId': self.user_id}
        self.client.get("/user/purchases", params=params)

    @task(1)
    def check_user(self):
        # Check if the user exists
        data = {'userId': self.user_id}
        self.client.post("/check-user", json=data)

    @task(1)
    def profile_avatar(self):
        # Update the user's profile avatar
        data = {
            'userId': self.user_id,
            'profileUrl': f"https://example.com/avatar/{self.user_id}.png"
        }
        self.client.put("/profileavatar", json=data)

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)  # Simulate user think time between 1 to 5 seconds
    host = "https://backend-2-9t4g.onrender.com"  # Replace with your actual backend host and port
