from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import *  # This is where we import 'generics' such as {TemplateView, View, CreateView, FormView, DetailView, ListView}
from .models import *
from .forms import *
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.http import Http404
from django.core.paginator import Paginator
from django.http import JsonResponse
import requests
from .utils import *
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings

def cancel_order(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        order_id = request.POST.get('order_id')
        try:
            order = Order.objects.get(id=order_id)
            order.order_status = 'Order Cancelled'
            order.cancel_order += 1  # Ensure cancel_order is an integer
            order.save()
            return JsonResponse({'success': True})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


# Create your views here.
class EcomMixin(object):        # this helps to run our site in 'incognito' mode or 'private' window
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)
    
class HomeView(EcomMixin, TemplateView):
    template_name = "home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['myname'] = "Sujan Ghimire"
        all_products = Product.objects.all().order_by("-id")
        paginator = Paginator(all_products, 15)
        page_number = self.request.GET.get('page')
        product_list = paginator.get_page(page_number)
        context['product_list'] = product_list     # this will help to see the current upload product at the top
        return context

class AllProductsView(EcomMixin, TemplateView):
    template_name = "allproducts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all()
        return context

class ProductDetailView(EcomMixin, TemplateView):
    template_name = "productdetail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']  
        product = Product.objects.get(slug=url_slug)# this helps to define 'which' product seen by 'users'
        product.view_count += 1
        product.save()
        context['product']=product
        return context

class AddToCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        # Get product id from requested URL
        product_id = self.kwargs['pro_id']
        
        # Get product
        product_obj = get_object_or_404(Product, id=product_id)
        
        # Check if product exists
        if product_obj:
            # Add product to cart logic goes here
            cart_id = request.session.get("cart_id")
            if cart_id:
                cart_obj = Cart.objects.get(id=cart_id)
                this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)

                # Item already exists in cart
                if this_product_in_cart.exists():
                    cartproduct = this_product_in_cart.last()
                    cartproduct.quantity += 1
                    cartproduct.subtotal += product_obj.selling_price
                    cartproduct.save()
                    cart_obj.total += product_obj.selling_price
                    cart_obj.save()
                else:
                    cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
                    cart_obj.total += product_obj.selling_price
                    cart_obj.save()
            else:
                cart_obj = Cart.objects.create(total=0)
                request.session['cart_id'] = cart_obj.id
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            
            # Redirect user to home page
            return redirect("appGurkha:home")
        
        # Handle invalid product ID, for example, redirect to home
        return redirect("appGurkha:home")

class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        print("This is manage cart view.")
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart
        
        # cart_id = request.session.get("cart_id", None)
        # if cart_id:
        #     cart2 = Cart.objects.get(id=cart_id)
        #     if cart1 != cart2:
        #         return redirect("appGurkha:mycart")
        # else:
        #         return redirect("appGurkha:mycart")
        
        # print(cp_id, action)
        
        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == "dcr":            
            if cp_obj.quantity == 1:
                cp_obj.quantity = 1
            else:
                cp_obj.quantity -= 1
                cp_obj.subtotal -= cp_obj.rate
                cp_obj.save()
                cart_obj.total -= cp_obj.rate
                cart_obj.save()
                
        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("appGurkha:mycart")

class ClearCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("appGurkha:mycart")
    
    def form_valid(self, form):
        
        return super().form_valid(form)
    
class MyCartView(EcomMixin, TemplateView):
    template_name = "mycart.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context

class CheckoutView(EcomMixin, CreateView):
    template_name="checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("appGurkha:home")
    
    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated and request.user.customer:
    #         print("logged in user")
    #         pass
    #     else:
    #         print("Anynonymous User")
    #         return redirect("/login/?next=/checkout")
    #     return super().dispatch(request, *args, **kwargs)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)

        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        
        context['cart'] = cart_obj
        return context
    
    def form_valid(self, form):  # this function is used for 'django-forms'
        cart_id = self.request.session.get("cart_id")
        
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            del self.request.session['cart_id']
            
            # Check if the order status is "Order Received"
            if form.instance.order_status == "Order Received":
                # Retrieve all products associated with the order
                for cart_product in cart_obj.cartproduct_set.all():
                    product = cart_product.product
                    # Check if the stock is greater than 0 before decrementing
                    if product.stock > 0:
                        product.stock -= 1
                        product.save()
            
            #for khalti payment
            pm = form.cleaned_data.get("payment_method")
            order = form.save()
            if pm == "Khalti":
                return redirect(reverse("appGurkha:khaltirequest") + "?o_id=" + str(order.id))
        else:
            return redirect("appGurkha:home")
        
        return super().form_valid(form)
    
    
    # def post(self, request, *args, **kwargs):
    #     form_data = request.POST
    #     cart_id = self.request.session.get("cart_id")
        
    #     if cart_id:
    #         cart_obj = Cart.objects.get(id=cart_id)
    #         ordered_by = form_data.get('ordered_by')
    #         email = form_data.get('email')
    #         shipping_address = form_data.get('shippingAddress')
    #         mobile = form_data.get('mobile')

    #         # Create order instance
    #         if ordered_by:  # Check if 'ordered_by' is not empty
    #             order = Order.objects.create(
    #                 cart=cart_obj,
    #                 ordered_by=ordered_by,
    #                 email=email,
    #                 shipping_address=shipping_address,
    #                 mobile=mobile,
    #                 subtotal=cart_obj.total,
    #                 discount=0,
    #                 total=cart_obj.total,
    #                 order_status="Ordered Received"
    #             )

    #             # Clear the cart after placing the order
    #             cart_obj.delete()
    #             del request.session['cart_id']

    #             return redirect(self.success_url)
    #         else:
    #             # If 'ordered_by' is empty, return to the checkout page with an error message
    #             return redirect('appGurkha:checkout')

    #     else:
    #         return redirect("appGurkha:home")
    
    
# Implementing the Khalti payment gateway
class KhaltiRequestView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get("o_id")
        order = Order.objects.get(id=o_id)
        context = {
            "order" : order
        }
        return render(request, "Khaltirequest.html", context)

class KhaltiVerifyView(View):
    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        amount = request.GET.get("amount")
        o_id = request.GET.get("order_id")
        print(token, amount, o_id)
        data = {
            "success":True
        }
        
        #this is the 'url' to verify the transaction, this is provided by the 'khalti' official site
        url = "https://khalti.com/api/v2/payment/verify/"
        payload = {
        "token": token,
        "amount": amount
        }
        headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}"
        }

        order_obj = Order.objects.get(id=o_id)
        response = requests.request("POST", url, headers=headers, data=payload)
        # response = requests.get(url, params, headers = headers)
        print("Response", response)
        resp_obj = response.json()
        print(resp_obj)

        if resp_obj.get("idx"):
            success = True
            order_obj.payment_completed = True
            order_obj.save()
        else:
            success = False

        data = {
            "success": success
        }
        return JsonResponse(data)
        

class CustomerRegistrationView(CreateView):
    template_name = 'CustomerRegistration.html' 
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("appGurkha:home")
    
    def form_valid(self, form):
       username = form.cleaned_data.get("username")
       password = form.cleaned_data.get("password")
       email = form.cleaned_data.get("email")
       user = User.objects.create_user(username, email=email, password=password)
       form.instance.user = user
       login(self.request, user)
       return super().form_valid(form)
    
class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("appGurkha:home")

class CustomerLoginView(FormView):
    template_name = 'customerlogin.html'  # You can adjust this template as needed
    form_class = CustomerLoginForm
    success_url_customer = reverse_lazy("appGurkha:home")  # Redirect URL for customers
    success_url_admin = reverse_lazy("appGurkha:adminhome")  # Redirect URL for admins

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if hasattr(user, 'customer'):
                    return redirect(self.success_url_customer)
                elif hasattr(user, 'admin'):
                    return redirect(self.success_url_admin)
            else:
                messages.error(request, 'Invalid username or password.')
        return render(request, self.template_name, {'form': form})
    # template_name = 'customerlogin.html' 
    # form_class = CustomerLoginForm
    # success_url = reverse_lazy("appGurkha:home")
    
    # # form_valid method is a type of 'POST' method, is available in 'CreateView', 'FormView' and 'UpdateView' only
    # def form_valid(self, form):
    #     uname = form.cleaned_data.get("username") # username is the field name here
    #     pword = form.cleaned_data.get("password")
    #     usr = authenticate(username=uname, password=pword)
        
    #     if usr is not None and Customer.objects.filter(user=usr).exists():
    #         login(self.request, usr)
    #     else:
    #         return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid Credentials"})
        
    #     return super().form_valid(form)

class AboutView(EcomMixin, TemplateView):
    template_name = "about.html"

class ContactView(EcomMixin, TemplateView):
    template_name = "contactus.html"
    
class CustomerProfileView(TemplateView):
    template_name = "customerprofile.html"
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile")
        return super().dispatch(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context
    
class CustomerOrderDetailView(DetailView):
    template_name = "customerorderdetail.html"
    model = Order
    context_object_name = "ord_obj"
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            try:
                order = Order.objects.get(id=order_id)
                if request.user.customer != order.cart.customer:
                    return redirect("appGurkha:customerprofile")
            except Order.DoesNotExist:
                return redirect("appGurkha:customerprofile")
                
        else:
            return redirect("/login/?next=/profile")
        return super().dispatch(request, *args, **kwargs)
    
class SearchView(TemplateView):
    template_name = 'search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # kw = self.request.GET["keyword"]    # also use to get the data from the search bar
        kw = self.request.GET.get("keyword")
        results = Product.objects.filter(Q(title__icontains=kw) | Q(description__icontains=kw) | Q(return_policy__icontains=kw))   #helps to search product with no "case-sensitivity"
        print("user search for : ", kw)
        print("System show the result to user: ", results)
        context["results"] = results
        return context
    
    
# admin pages
class AdminLoginView(FormView):
    template_name = "adminpages/adminlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("appGurkha:adminhome")
    
    def form_valid(self, form):
        uname = form.cleaned_data.get("username") # username is the field name here
        pword = form.cleaned_data.get("password")
        usr = authenticate(username=uname, password=pword)
        
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid Credentials"})

        return super().form_valid(form)

class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/admin-login/")
        return super().dispatch(request, *args, **kwargs)
    
class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/adminhome.html"
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendingorders"] = Order.objects.filter(order_status = "Order Received")
        return context
    
class AdminOrderDetailView(AdminRequiredMixin, DetailView):
    template_name = 'adminpages/adminorderdetail.html'
    model = Order
    context_object_name = "ord_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context
    

class AdminOrderListView(ListView):
    template_name ='adminpages/adminorderlist.html'
    queryset = Order.objects.all().order_by("-id")
    context_object_name = 'allorders'
    
    
class AdminOrdersStatusChangeView(AdminRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("status")
        print("updated_status: ", new_status)
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(reverse_lazy("appGurkha:adminorderdetail", kwargs={"pk": self.kwargs["pk"]}))

class AdminProductListView(AdminRequiredMixin, ListView):
    template_name = "adminpages/adminproductlist.html"
    queryset = Product.objects.all().order_by("-id")
    context_object_name = "allproducts"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_id'] = self.kwargs.get('product_id')  # Add this line
        return context

class AdminProductCreateView(AdminRequiredMixin, CreateView):
    template_name = "adminpages/adminproductcreate.html"
    form_class = ProductForm
    success_url = reverse_lazy("appGurkha:adminproductlist")

    def form_valid(self, form):
        p = form.save()
        images = self.request.FILES.getlist("more_images")

        for i in images:
            ProductImage.objects.create(product=p, image=i)
            
        return super().form_valid(form)
    
class AdminProductEditView(View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = ProductEditForm(instance=product)
        return render(request, 'adminpages/adminproductedit.html', {'form': form, 'product': product})

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = ProductEditForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('appGurkha:adminproductlist')
        return render(request, 'adminpages/adminproductedit.html', {'form': form, 'product': product})


#product delete
class AdminProductDeleteView(AdminRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('appGurkha:adminproductlist')

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        if pk:
            product = Product.objects.get(pk=pk)
            product.delete()
        return redirect('appGurkha:adminproductlist')

    
# forget Password for customer
class PasswordForgetView(FormView):
    template_name = "forgetpassword.html"
    form_class = PasswordForgetForm
    success_url = "/forget-password/?m=s" # /mail-sent/

    def form_valid(self, form):
        #get email from user
        email = form.cleaned_data.get("email")
        print("applied to reset password : ", email)
        
        # get current host ip/domain
        url = self.request.META['HTTP_HOST']
        customer = Customer.objects.get(user__email=email) # get customer and then user
        user = customer.user
        text_content = 'Please Click the link below to reset your password.' # send mail to the user with email
        html_content = url + "/password-reset/" + email + \
            "/" + password_reset_token.make_token(user) + "/"
        send_mail(
            'Password Reset Link | GadgetGurkha',
            text_content + html_content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return super().form_valid(form)
    
class PasswordResetView(FormView):
    template_name = 'passwordreset.html'
    form_class = PasswordResetForm
    success_url = "/login/"
    
    def dispatch(self, request, *args, **kwargs):
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        token = self.kwargs.get("token")

        if user is not None and password_reset_token.check_token(user, token):
            pass
        else:
            return redirect(reverse("appGurkha:passwordforget") + "?m=e")

        return super().dispatch(request, *args, **kwargs)
    

    def form_valid(self, form):
        password = form.cleaned_data['new_password']
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return super().form_valid(form)