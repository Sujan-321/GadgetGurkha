from django.urls import path
from .views import *

app_name = "appGurkha"
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("home/", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("all-products/", AllProductsView.as_view(), name="allproducts"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="productdetail"),
    path("add-to-cart-<int:pro_id>/", AddToCartView.as_view(), name="addtocart"),
    path("my-cart/", MyCartView.as_view(), name="mycart"),
    path("manage-cart/<int:cp_id>", ManageCartView.as_view(), name="managecart"),
    path("clear-cart/", ClearCartView.as_view(), name="clearcart"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("register/", CustomerRegistrationView.as_view(), name="CustomerRegistration"),
    path("logout/", CustomerLogoutView.as_view(), name="customerlogout"),
    path("login/", CustomerLoginView.as_view(), name="customerlogin"),
    path("profile/", CustomerProfileView.as_view(), name="customerprofile"),
    path("profile/order-<int:pk>/", CustomerOrderDetailView.as_view(), name="customerorderdetail"),
    path("search/",SearchView.as_view(), name="search"),
    path('cancel-order/', cancel_order, name='cancel_order'),
    
    # for admin section
    path("admin-login/", AdminLoginView.as_view(), name="adminlogin"),
    path("admin-home/", AdminHomeView.as_view(), name="adminhome"),
    path("admin-order/<int:pk>/",AdminOrderDetailView.as_view(), name="adminorderdetail"),
    path("admin-all-orders/", AdminOrderListView.as_view(), name="adminorderlist"),
    path("admin-order-<int:pk>-change/", AdminOrdersStatusChangeView.as_view(), name="adminorderstatuschange"),
    path("admin-product/list/", AdminProductListView.as_view(), name="adminproductlist"),
    path("admin-product/add/", AdminProductCreateView.as_view(), name="adminproductcreate"),
    path('admin-product/edit/<int:product_id>/', AdminProductEditView.as_view(), name='admin-product-edit'),
    path('admin-product/delete/<int:pk>/', AdminProductDeleteView.as_view(), name='adminproductdelete'),
    
    #payment request from "khalti"
    path("khalti-request/", KhaltiRequestView.as_view(), name="khaltirequest"),
    path("khalti-verify/", KhaltiVerifyView.as_view(), name="khaltiverify"),

    # forget password
    path("forget-password/", PasswordForgetView.as_view(), name="passwordforget"),
    path("password-reset/<email>/<token>/", PasswordResetView.as_view(), name="passwordreset"),
]
