from django import forms

class LoginForm(forms.Form):
    mobile_no = forms.CharField(label="Mobile Number", max_length=15, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"class": "form-control"}))

class OTPForm(forms.Form):
    otp = forms.CharField(label="Enter OTP", max_length=6, widget=forms.TextInput(attrs={"class": "form-control"}))
