from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import json

class IVACLoginInfo(models.Model):
    mobile_no = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)  # Encrypted
    cookies = models.JSONField(default=dict, blank=True)  # Store cookies as JSON
    session_id = models.CharField(max_length=255, unique=True, null=True)  # Store session_id
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Encrypt password before saving"""
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def set_cookies(self, cookies):
        """Store cookies in JSON format"""
        self.cookies = json.dumps(cookies)
        self.save()

    def get_cookies(self):
        """Retrieve cookies from JSON"""
        return json.loads(self.cookies) if self.cookies else {}

    def __str__(self):
        return self.mobile_no
    
class PaymentInfo(models.Model):
    """Model to store payment information with a title and link to IVACLoginInfo."""
    
    title = models.CharField(max_length=255)
    ivac_login_info = models.ForeignKey(IVACLoginInfo, on_delete=models.CASCADE, related_name='payment_info_sessions')

    email = models.EmailField(max_length=255, blank=True, null=True)
    
    bgd1 = models.CharField(max_length=255, blank=True, null=True)
    name1 = models.CharField(max_length=255, blank=True, null=True)
    bgd2 = models.CharField(max_length=255, blank=True, null=True)
    name2 = models.CharField(max_length=255, blank=True, null=True)
    bgd3 = models.CharField(max_length=255, blank=True, null=True)
    name3 = models.CharField(max_length=255, blank=True, null=True)
    bgd4 = models.CharField(max_length=255, blank=True, null=True)
    name4 = models.CharField(max_length=255, blank=True, null=True)
    bgd5 = models.CharField(max_length=255, blank=True, null=True)
    name5 = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title