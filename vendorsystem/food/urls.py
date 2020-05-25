from django.urls import path
from food import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token


app_name = "food"

urlpatterns = [

    path('register/vendor',views.RegisterVendor.as_view(),name="vendor"),
    path('register/customer',views.RegisterCustomer.as_view(),name="customer"),
    path('register/password/vendor/<int:vendorID>',views.SetVendorPassword.as_view(),name="vendor_password"),
    path('register/password/customer/<int:customerID>',views.SetCustomerPassword.as_view(),name="customer_password"),
    path('login',obtain_auth_token,name="login"),
    path('menu/<int:vendorID>', views.VendorMenu.as_view(), name="menu"),
    path('menu/update/<int:menuID>', views.UpdateVendorMenu.as_view(), name="menu_update"),
    path('status', views.CreateStatus.as_view(), name="status"),
    path('cart/add/<int:customerID>', views.AddToCartView.as_view(), name="add_item_to_cart"),
    path('cart/delete/<int:cartID>', views.DeleteFromCartView.as_view(), name="remove_item_from_cart"),
    path('cart/<int:customerID>', views.CartView.as_view(), name="get_item_in_cart"),
    path('order/<int:customerID>', views.PlaceOrderView.as_view(), name="order"),
    path('confirm/order/<int:vendorID>/<int:orderID>', views.ConfirmOrderView.as_view(), name="confirm_order"),
    path('cancel/order/<int:customerID>/<int:orderID>', views.CancelOrderView.as_view(), name="cancel_order"),
    path('confirm/delivery/<int:vendorID>/<int:orderID>', views.ConfirmDeliveryView.as_view(), name="confirm_delivery"),
    path('notification/<int:vendorID>/<int:orderID>', views.NotificationView.as_view(), name="notification"),
    path('report/<int:vendorID>', views.DailyReportView.as_view(), name="report"),

]