from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from EcomApp.models.users import Profile

class Command(BaseCommand):
    help = 'Creates demo accounts for the application'

    def handle(self, *args, **kwargs):
        demo_accounts = [
            {
                'email': 'buyer@demo.com',
                'username': 'buyer_demo',
                'password': 'password123',
                'first_name': 'Demo',
                'last_name': 'Buyer',
                'role': 'customer',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'email': 'seller@demo.com',
                'username': 'seller_demo',
                'password': 'password123',
                'first_name': 'Demo',
                'last_name': 'Seller',
                'role': 'seller',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'email': 'admin@demo.com',
                'username': 'admin_demo',
                'password': 'password123',
                'first_name': 'Demo',
                'last_name': 'Admin',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            },
        ]

        for account in demo_accounts:
            user, created = User.objects.get_or_create(
                email=account['email'],
                defaults={
                    'username': account['username'],
                    'first_name': account['first_name'],
                    'last_name': account['last_name'],
                    'is_staff': account['is_staff'],
                    'is_superuser': account['is_superuser'],
                }
            )

            if created:
                user.set_password(account['password'])
                user.save()
                
                # Create or update profile
                Profile.objects.update_or_create(
                    user=user,
                    defaults={
                        'role': account['role'],
                        'display_name': f"{account['first_name']} {account['last_name']}"
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created demo user: {account["email"]}'))
            else:
                # Ensure password is correct and profile role is correct even if user existed
                user.set_password(account['password'])
                user.is_staff = account['is_staff']
                user.is_superuser = account['is_superuser']
                user.save()
                
                Profile.objects.update_or_create(
                    user=user,
                    defaults={
                        'role': account['role'],
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully updated demo user: {account["email"]}'))

        self.stdout.write(self.style.SUCCESS('All demo accounts are ready!'))
