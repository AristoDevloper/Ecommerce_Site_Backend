from django.db import models
from django.contrib.auth.models import User
import uuid

class Store(models.Model):
    store_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, null=True)
    name = models.CharField(max_length=100)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class StoreProduct(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey('EcomApp.Product', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} in {self.store.name}"
