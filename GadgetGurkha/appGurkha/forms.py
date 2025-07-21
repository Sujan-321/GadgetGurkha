from django import forms
from .models import *
from django.forms.widgets import *
from django.contrib.auth.models import User

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["ordered_by", "shipping_address", "mobile", "email", "payment_method"]
        
        widgets = {
            'ordered_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'shipping_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Shipping Address'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile', 'maxlength': '10'}),
        }


class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    class Meta:
        model = Customer
        fields = ["username", "email", "full_name", "address", "password"]

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already register.")
        return email
    
    def clean_username(self):
        uname = self.cleaned_data.get("username")

        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError("This Username is already taken.")
        return uname
    
class CustomerLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

# class AdminLoginForm(forms.Form):

class ProductForm(forms.ModelForm):
    more_images = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'multiple': False}))
    class Meta:
        model = Product
        fields = ["title", "slug", "category", "image", "marked_price", "selling_price", "description", "warrenty", "return_policy", "stock"]

        widgets = {
            "title": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Leather Jacket'}),
            "slug": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. leather-jacket'}),
            "category": forms.Select(attrs={'class': 'form-control'}),
            "image": forms.ClearableFileInput(attrs={'class': 'form-control'}),
            "marked_price": forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Marked Price of the Product...'}),
            "selling_price": forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Selling Price of the Product...'}),
            "description": forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'description', 'rows':5}),
            "warrenty": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Warrenty Period'}),
            "return_policy": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Return Policy'}),
            "stock": forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '50'}),
        }
        
class ProductEditForm(forms.ModelForm):
    more_images = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'multiple': False}))
    
    class Meta:
        model = Product
        fields = ["title", "slug", "category", "image", "marked_price", "selling_price", "description", "warrenty", "return_policy", "stock"]

        widgets = {
            "title": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Title'}),
            "slug": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Slug'}),
            "category": forms.Select(attrs={'class': 'form-control'}),
            "image": forms.ClearableFileInput(attrs={'class': 'form-control'}),
            "marked_price": forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Marked Price'}),
            "selling_price": forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Selling Price'}),
            "description": forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Product Description', 'rows': 5}),
            "warrenty": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Warranty'}),
            "return_policy": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Return Policy'}),
            "stock": forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '50'}),
        }

# for forget password
class PasswordForgetForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your email here....."
    }))
    
    def clean_email(self):
        e = self.cleaned_data.get("email")

        if Customer.objects.filter(user__email=e).exists():
            pass
        else:
            raise forms.ValidationError("Customer with this account doesnot exists.")
        return e

class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "autocomplete": "new-password",
        "placeholder": "New Password",
    }), label="New Password")

    confirm_new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "autocomplete": "new-password",
        "placeholder": "Confirm Password",
    }), label="Confirm Password")
    
    def clean_confirm_new_password(self):
        new_password = self.cleaned_data.get("new_password")
        confirm_new_password = self.cleaned_data.get("confirm_new_password")

        if new_password != confirm_new_password:
            raise forms.ValidationError("Passwords didn't match!")
        
        return confirm_new_password