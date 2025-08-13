import os
import django
import random
from faker import Faker

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_alerts_app.settings')  # Replace with your project.settings
django.setup()

from master.models import UserCustom  # Adjust if your model is in another app

fake = Faker()

def create_users(n=15):
    for _ in range(n):
        username = fake.user_name()
        password = fake.password(length=10)
        passcode = str(random.randint(1000, 9999)) if random.choice([True, False]) else None
        passcode_set = bool(passcode)
        can_reset_password = random.choice([True, False])
        wrong_attempts = random.randint(0, 5)
        is_locked = wrong_attempts > 3

        user = UserCustom.objects.create(
            username=username,
            password=password,
            passcode=passcode,
            passcode_set=passcode_set,
            can_reset_password=can_reset_password,
            wrong_attempts=wrong_attempts,
            is_locked=is_locked,
        )
        print(f"Created user: {user.username}")

create_users(15)

