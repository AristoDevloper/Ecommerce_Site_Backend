import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from EcomApp.models import Profile, Store, Cart

class Command(BaseCommand):
    help = 'Seeds the database with demo users (buyer, seller, admin).'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding demo users...')

        # Demo Buyer
        buyer_email = 'buyer@demo.com'
        if not User.objects.filter(email=buyer_email).exists():
            buyer = User.objects.create_user(username='demo_buyer', email=buyer_email, password='password123')
            Profile.objects.create(user=buyer, role='customer', display_name='Demo Buyer')
            Cart.objects.create(user=buyer)
            self.stdout.write(self.style.SUCCESS(f'Created buyer: {buyer_email}'))
        else:
            self.stdout.write(f'Buyer {buyer_email} already exists.')

        # Demo Seller
        seller_email = 'seller@demo.com'
        if not User.objects.filter(email=seller_email).exists():
            seller = User.objects.create_user(username='demo_seller', email=seller_email, password='password123')
            Profile.objects.create(user=seller, role='seller', display_name='Demo Seller')
            Cart.objects.create(user=seller)
            Store.objects.create(name="Demo Store", owner=seller)
            self.stdout.write(self.style.SUCCESS(f'Created seller: {seller_email} with Demo Store'))
        else:
            self.stdout.write(f'Seller {seller_email} already exists.')

        # Demo Admin
        admin_email = 'admin@demo.com'
        if not User.objects.filter(email=admin_email).exists():
            # Create user with is_staff=True, but is_superuser=False
            admin = User.objects.create_user(username='demo_admin', email=admin_email, password='password123')
            admin.is_staff = True
            admin.is_superuser = False
            admin.save()
            Profile.objects.create(user=admin, role='admin', display_name='Demo Admin')
            Cart.objects.create(user=admin)
            self.stdout.write(self.style.SUCCESS(f'Created admin: {admin_email} (is_staff=True)'))
        else:
            self.stdout.write(f'Admin {admin_email} already exists.')

        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
