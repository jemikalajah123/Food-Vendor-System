from django.shortcuts import render
from django.shortcuts import render, redirect, get_list_or_404
from . models import Vendor, Customer, Menu, Status, Order, Notification, Auth, Cart, OrderContent
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . serializers import VendorSerializer, CustomerSerializer, MenuSerializer, StatusSerializer, OrderSerializer, NotificationSerializer, AuthSerializer, CartSerializer, OrderContentSerializer
from django.http import HttpResponse, Http404
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib import messages
# Create your views here.


class RegisterVendor(APIView):
    def post(self, request, format=None):
        to_email = []
        serializer = VendorSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            vendor = serializer.save()
            data['response'] = "successfully registered a new Vendor"
            data['email'] = vendor.email
            mail_subject = 'Vendor Email Confirmation '
            to = str(vendor.email)
            to_email.append(to)
            from_email = 'okeoghene.philip5@gmail.com'
            message = "Hi "+vendor.full_name + \
                " Your are welcome to the best Online Food Vendor Platform . Please complete your registration by entering your registered email and setting your desired password. Your ID number is  " + \
                str(vendor.id)+". "
            send_mail(
                mail_subject,
                message,
                from_email,
                to_email,
                fail_silently=False,
            )
        else:
            data = serializer.errors
        return Response(data)

    def get(self, request):
        vendor = Vendor.objects.all()
        serializer = VendorSerializer(vendor, many=True)
        return Response(serializer.data)


class RegisterCustomer(APIView):
    def post(self, request, format=None):
        to_email = []
        serializer = CustomerSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            customer = serializer.save()
            data['response'] = "successfully registered a new Customer"
            data['email'] = customer.email
            mail_subject = 'Customer Email Confirmation '
            to = str(customer.email)
            to_email.append(to)
            from_email = 'okeoghene.philip5@gmail.com'
            message = "Hi "+customer.first_name + \
                " Your are welcome to the best Online Food Vendor Platform . Please complete your registration by entering your registered email and setting your desired password. Your ID number is  " + \
                str(customer.id)+". "
            send_mail(
                mail_subject,
                message,
                from_email,
                to_email,
                fail_silently=False,
            )
        else:
            data = serializer.errors
        return Response(data)

    def get(self, request):
        customer = Customer.objects.all()
        serializer = CustomerSerializer(customer, many=True)
        return Response(serializer.data)


class SetVendorPassword(APIView):
    def post(self, request, vendorID, format=None):
        try:
            vendor = Vendor.objects.get(id=vendorID)
        except Vendor.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AuthSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            if vendor.email == self.request.data['email'] and self.request.data['user_type'] == "Vendor":
                auth = serializer.save()
                data['response'] = "successfully registered a new Vendor"
                data['email'] = auth.email
                token = Token.objects.get(user=auth).key
                data['token'] = token
                return Response(data)
            else:
                data = serializer.errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetCustomerPassword(APIView):
    def post(self, request, customerID, format=None):
        try:
            customer = Customer.objects.get(id=customerID)
        except Customer.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AuthSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            if customer.email == self.request.data['email'] and self.request.data['user_type'] == "Customer":
                auth = serializer.save()
                data['response'] = "successfully registered a new Customer"
                data['email'] = auth.email
                token = Token.objects.get(user=auth).key
                data['token'] = token
                return Response(data)
            else:
                data = serializer.errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorMenu(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, vendorID, format=None):
        try:
            vendor = Vendor.objects.get(id=vendorID)
        except Vendor.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = MenuSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            if vendor.id is int(self.request.data['vendor_id']):
                menu = serializer.save()
                data['response'] = "successfully registered a new Menu"
                data['name'] = menu.name
                return Response(data)
            else:
                data = serializer.errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateVendorMenu(APIView):
    permission_classes = (IsAuthenticated,)
    def get_object(self, vendorID):
        menu = Menu.objects.get(id=vendorID)
        return menu

    def patch(self, request, menuID):
        try:
            menu = Menu.objects.get(id=menuID)
            user = menu.vendor_id.id
        except Menu.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        menu = self.get_object(menu)
        serializer = MenuSerializer(menu, data=request.data, partial=True)
        data = {}
        if serializer.is_valid():
            if user is int(self.request.data['vendor_id']):
                menu = serializer.save()
                data["success"] = "Update successful"
                return Response({"success": "Menu '{}' updated successfully".format(menu.name)})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateStatus(APIView):
    def post(self,request):
        status = Status.objects.create(payment_status="Pending", order_status="Pending", delivery_status="Pending",message_status="Pending")
        status.save()
        return Response({"success": "status update created successfully"})

class ConfirmOrderView(APIView):
    def put(self, request, vendorID, orderID):
        to_email = []
        try:
            vendor = Vendor.objects.get(id=vendorID)
            order = Order.objects.get(id=orderID)
            orderItems = OrderContent.objects.get(order=order.id)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        vendorID = orderItems.menu.vendor_id.id
        if vendor.id == vendorID:
            status = order.status.confirmOrder()
            order.customer.total_sale += order.amount_due
            order.customer.orders += 1
            order.customer.save()
            mail_subject = 'Order Confirmed'
            to = str(orderItems.order.customer.email)
            to_email.append(to)
            from_email = 'okeoghene.philip5@gmail.com'
            message = "Hi "+order.customer.first_name+" Your order was confirmed successfully for delivery. Please go to your dashboard to see your order status history. Your order id is " + \
                str(orderID)+".Any balance amount is paid on delivery "
            send_mail(
                mail_subject,
                message,
                from_email,
                to_email,
                fail_silently=False,
            )

            return Response({"success": " '{}' Your order has been confirmed for delivery".format(order.customer.first_name)})


class CancelOrderView(APIView):
    def put(self, request, customerID, orderID):
        to_email = []
        try:
            customer = Customer.objects.get(id=customerID)
            order = Order.objects.get(id=orderID)
            orderItems = OrderContent.objects.get(order=order.id)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        customerID = orderItems.order.customer.id
        if customer.id == customerID:
            status = order.cancelOrder()
            customerID = order.customer.id
            customer = Customer.objects.get(id=customerID)
            customer.total_sale -= order.amount_due
            customer.orders -= 1
            customer.save()
            mail_subject = 'Order Cancelled'
            to = str(orderItems.menu.vendor_id.email)
            to_email.append(to)
            from_email = 'okeoghene.philip5@gmail.com'
            message = "Hi "+orderItems.menu.vendor_id.full_name+" An order was cancelled by a customer. The order id is " + \
                str(orderID)+". Sorry for the incoveniences!!!"
            send_mail(
                mail_subject,
                message,
                from_email,
                to_email,
                fail_silently=False,
            )

            mail_subject = 'Order Cancelled'
            to = str(orderItems.order.customer.email)
            to_email.append(to)
            from_email = 'okeoghene.philip5@gmail.com'
            message = "Hi "+order.customer.first_name+" Your order was cancelled successfully. Please share your reason for cancelling your order with us. Your order id is " + \
                str(orderID)+". WE HOPE YOUR BUY FROM US ANOTHER TIME"
            send_mail(
                mail_subject,
                message,
                from_email,
                to_email,
                fail_silently=False,
            )

            return Response({"success": " '{}' Your order was cancelled successfully".format(order.customer.first_name)})


class ConfirmDeliveryView(APIView):
    def put(self, request, vendorID, orderID):
        to_email = []
        try:
            vendor = Vendor.objects.get(id=vendorID)
            order = Order.objects.get(id=orderID)
            orderItems = OrderContent.objects.get(order=order.id)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        vendorID = orderItems.menu.vendor_id.id
        if vendor.id == vendorID:
            status = order.status.confirmDelivery()
            mail_subject = 'Order Delivered successfully'
            to = str(orderItems.order.customer.email)
            to_email.append(to)
            from_email = 'okeoghene.philip5@gmail.com'
            message = "Hi "+order.customer.first_name+" Your order was delivered successfully. Please go to your dashboard to see your order status history. Your order id is " + \
                str(orderID)+". Share your feedback with us."
            send_mail(
                mail_subject,
                message,
                from_email,
                to_email,
                fail_silently=False,
            )
            return Response({"success": " '{}' Your order was delivered successfully".format(order.customer.first_name)})


class AddToCartView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, customerID):
        try:
            customer = Customer.objects.get(id=customerID)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CartSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            if customer.id == int(self.request.data['customer']):
                cart = serializer.save()
                data['response'] = "successfully added an item to your cart"
                data['customer'] = cart.customer.email
            else:
                data = serializer.errors
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteFromCartView(APIView):
    permission_classes = (IsAuthenticated,)
    def delete(self, request, cartID):
        try:
            item = Cart.objects.get(id=cartID)
        except item.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        operation = item.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


class CartView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, customerID):
        customer = Customer.objects.get(id=customerID)
        cart = Cart.objects.filter(customer=customer.id)
        serializer = CartSerializer(cart, many=True)
        return Response(serializer.data)


class PlaceOrderView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, customerID):
        to_email = []
        customer = Customer.objects.get(id=customerID)
        items = Cart.objects.filter(customer=customerID)
        for item in items:
            menu = item.menu
            quantity = item.quantity
            serializer = OrderSerializer(data=request.data)
            data = {}
            if serializer.is_valid():
                menu.quantity -= int(quantity)
                order = serializer.save()
                update_order = order.updateOrder(customer)
                order = Order.objects.get(id=order.id)
                mail_subject = 'Order Placed successfully'
                to = str(customer.email)
                to_email.append(to)
                from_email = 'okeoghene.philip5@gmail.com'
                message = "Hi "+customer.first_name + \
                    " Your order was placed successfully. Please go to your dashboard to see your order history. Your order id is " + \
                    str(order.id)+""
                send_mail(
                    mail_subject,
                    message,
                    from_email,
                    to_email,
                )
                mail_subject = 'Order Received'
                to = str(item.menu.vendor_id.email)
                to_email.append(to)
                from_email = 'okeoghene.philip5@gmail.com'
                message = "Hi "+item.menu.vendor_id.full_name + \
                    " An order has been received. Please attend to it immediately. The order id is " + \
                    str(order.id)+""
                send_mail(
                    mail_subject,
                    message,
                    from_email,
                    to_email,
                )
            else:
                data = serializer.errors
            orderContent = OrderContent(menu=menu, order=order)
            orderContent.save()
            item.delete()
            data['response'] = "Hi "+customer.first_name + \
                " Your order was placed successfully. Please go to your dashboard to see your order history. Your order id is " + \
                str(order.id)+""
        return Response(data)

    def get(self, request, customerID):
        order = Order.objects.all()
        for items in order:
            order = Order.objects.filter(customer=customerID)
            serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)


class NotificationView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, vendorID, orderID, format=None):
        try:
            vendor = Vendor.objects.get(id=vendorID)
            order = Order.objects.get(id=orderID)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        order.status.resetMessageStatus()
        serializer = NotificationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            if vendor.id is int(self.request.data['vendor_id']) and order.customer.id is int(self.request.data['customer_id']) and order.id is int(self.request.data['order_id']):
                notification = serializer.save()
                data['response'] = "successfully sent a notification"
                order.status.confirmMessage()
                return Response(data)
            else:
                data = serializer.errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DailyReportView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, vendorID):
        vendor = Vendor.objects.get(id=vendorID)
        report = Order.objects.filter(ordercontent__menu__vendor_id=vendor.id)
        serializer = OrderSerializer(report, many=True)
        return Response(serializer.data)
