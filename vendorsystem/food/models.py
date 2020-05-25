from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# Create your models here.


class MyAccountManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError('The Email must be set')
        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,

        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Auth(AbstractBaseUser):

    vendor = 'Vendor'
    customer = 'Customer'
    admin = 'Admin'

    TYPE = (
        (vendor, vendor),
        (customer, customer),
        (admin, admin),
    )

    user_type = models.CharField(max_length=100, choices=TYPE, default=admin)
    email = models.EmailField(max_length=254, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def __int__(self):
        return self.id


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Vendor(models.Model):
    full_name = models.CharField(max_length=200)
    business_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254, unique=True)
    phone_number = PhoneNumberField(null=False, blank=False, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.id


class Customer(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254, unique=True)
    phone_number = PhoneNumberField(null=False, blank=False, unique=True)
    address = models.CharField(max_length=200)
    orders = models.IntegerField(default=0)
    total_sale = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    created = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.id


class Menu(models.Model):
    vendor_id = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.id


class Status(models.Model):
    pending = 'Pending'
    completed = 'Completed'

    STATUS = (
        (pending, pending),
        (completed, completed),
    )

    pending = 'Pending'
    sent = 'Sent'

    MESSAGE = (
        (pending, pending),
        (sent, sent),
    )

    payment_status = models.CharField(max_length=100, choices=STATUS)
    order_status = models.CharField(max_length=100, choices=STATUS)
    delivery_status = models.CharField(max_length=100, choices=STATUS)
    message_status = models.CharField(max_length=100, choices=MESSAGE)
    created = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.id

    def confirmOrder(self):
        if Order.balance_amount == 0.00:
            self.payment_status = self.completed
            self.save()
        self.order_status = self.completed
        self.save()
        return True

    def confirmDelivery(self):
        if Status.order_status != "Pending":
            self.payment_status = self.completed
            self.save()
            self.delivery_status = self.completed
            self.save()
            return True

    def confirmMessage(self):
        if Status.message_status != "sent":
            self.message_status = self.sent
            self.save()
            return True

    def resetMessageStatus(self):
        if Status.message_status != "Pending":
            self.message_status = self.pending
            self.save()
            return True

    class Meta:
        verbose_name = 'Status'
        verbose_name_plural = 'Statuses'


class Order (models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, default=1)
    if_cancelled = models.BooleanField(default=False)
    cod = 'Cash On Delivery'
    card = 'Card Payment'

    PAYMENT = (
        (cod, cod),
        (card, card),
    )
    payment_method = models.CharField(max_length=100, choices=PAYMENT)
    pickup = 'PickUp'
    delivery = 'Delivery'

    TYPE = (
        (pickup, pickup),
        (delivery, delivery),
    )
    delivery_method = models.CharField(max_length=100, choices=TYPE)
    location = models.CharField(max_length=200, default="none")
    quantity = models.IntegerField(default=1)
    amount_due = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    balance_amount = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)

    one = 'One Hour'
    two = 'Two Hour'
    thirty = 'Thirty Minutes'
    immediately = 'Immediately'
    people_choices = (
        (one, 'one'), (two, 'two'),
        (thirty, 'thirty'), (immediately, 'immediately')
    )
    delivery_time = models.CharField(max_length=100, choices=people_choices)
    created = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.id

    def cancelOrder(self):
        if Status.delivery_status != "Completed":
            self.if_cancelled = True
            self.save()

    def updateOrder(self, customer):
        status = Status.objects.create(payment_status="Pending", order_status="Pending", delivery_status="Pending",message_status="Pending")
        status.save()
        status = Status.objects.get(id=status.id)
        customer = Customer.objects.get(id=customer)
        items = Cart.objects.filter(customer=customer)
        for item in items:
            menu = item.menu
            quantity = item.quantity
            self.customer = customer
            self.amount_due = float(menu.price)*float(item.quantity)
            self.location = customer.address
            self.quantity = quantity
            self.status = status
            self.balance_amount = float(self.amount_due) - float(self.amount_paid)
            self.save()
            return True


class OrderContent(models.Model):
    order = models.ForeignKey(
        Order, related_name='ordercontent', on_delete=models.CASCADE)
    menu = models.ForeignKey(
        Menu, related_name='ordercontent', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.id


class Cart(models.Model):
    quantity = models.IntegerField(default=1)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.id


class Notification(models.Model):

    vendor = 'Vendor'
    customer = 'Customer'

    TYPE = (
        (vendor, vendor),
        (customer, customer),
    )
    vendor_id = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    subject_user = models.CharField(max_length=100, choices=TYPE)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    def __int__(self):
        return self.id
