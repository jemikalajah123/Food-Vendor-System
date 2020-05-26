from rest_framework import serializers
from . models import Vendor, Customer, Menu, Status, Order, Notification, Auth, OrderContent, Cart

class AuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = Auth
        fields = '__all__'

    def save(self):
        auth = Auth(
            user_type=self.validated_data['user_type'],
            email=self.validated_data['email']
        )
        password = self.validated_data['password']
        auth.set_password(password)
        auth.save()
        return auth


class VendorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendor
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = '__all__'

class MenuSerializer(serializers.ModelSerializer):

    class Meta:
        model = Menu
        fields = '__all__'


class OrderContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderContent
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = '__all__'

class StatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Status
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'

    def save(self):
        notification = Notification(

            vendor_id=self.validated_data['vendor_id'],
            customer_id=self.validated_data['customer_id'],
            order_id=self.validated_data['order_id'],
            subject_user=self.validated_data['subject_user'],
            message=self.validated_data['message'],

        )
        notification.save()
        return notification

