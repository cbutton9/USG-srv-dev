from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.mail import send_mail

class Post(models.Model):
    title = models.CharField(max_length=40, unique=True, help_text="Title of the Post")
    content = models.TextField(help_text="Actual content, pure HTML")
    posted = models.DateTimeField(default=datetime.datetime.now(), help_text="Date posted")
    
    def __unicode__(self):
        return self.title

class DropoffPickupTime(models.Model):
    '''
    User's selection from possible dropoff and pickup times of an order
    '''
    dropoff_time = models.DateTimeField("Dropoff Time")
    pickup_time = models.DateTimeField("Pickup Time")
    n_boxes_total = models.IntegerField("Total boxes available")
    n_boxes_bought = models.IntegerField("Total boxes bought", default=0)

    def __unicode__(self):
        return "Dropoff: %s, Pickup: %s" % (self.dropoff_time.strftime("%a %m/%d/%Y %I:%M%p"),
                                            self.pickup_time.strftime("%a %m/%d/%Y %I:%M%p"))

class UnpaidOrder(models.Model):
    '''
    All info describing a student's order; not paid for yet (student can have multiple of these orders)
        User: Name, Email
        Cell phone #
        Proxy name, Proxy email, 
        # Boxes registered for,
    '''
    user = models.ForeignKey(User, related_name="unpaid_order")
    cell_number = models.CharField("Cell phone number", max_length=14)
    dropoff_pickup_time = models.ForeignKey(DropoffPickupTime, verbose_name="Dropoff/pickup times", related_name="unpaid_order")
    proxy_name = models.CharField("Proxy name", max_length=50, blank=True)
    proxy_email = models.CharField("Proxy email", max_length=50, blank=True)
    n_boxes_bought = models.IntegerField("Quantity", max_length=2)
    invoice_id = models.CharField("Invoice ID", max_length=36, unique=True)

    def __unicode__(self):
        return self.user.username


class Order(models.Model):
    '''
    All info describing a student's order
        User: Name, Email
        Cell phone #
        Proxy name, Proxy email, 
        # Boxes paid for,
        picked up empty box (Y/N),
        dropoff time, # boxes dropped off, 
        pickup time, # boxes picked up, 
    '''
    
    user = models.ForeignKey(User, related_name="order", unique=True)
    cell_number = models.CharField("Cell phone number", max_length=14)
    dropoff_pickup_time = models.ForeignKey(DropoffPickupTime, verbose_name="Dropoff/pickup times", related_name="order")
    proxy_name = models.CharField("Proxy name", max_length=50, blank=True)
    proxy_email = models.CharField("Proxy email", max_length=50, blank=True)
    n_boxes_bought = models.IntegerField("Quantity", max_length=2)
    invoice_id = models.CharField("Invoice ID", max_length=36, unique=True)
    
    bool_picked_empty = models.BooleanField("Picked up Empty Boxes", default=False)
    n_boxes_dropped = models.IntegerField("# Dropped Off", max_length=2, blank=True, default=0)
    n_boxes_picked = models.IntegerField("# Picked Up", max_length=2, blank=True, default=0)
    
    def __unicode__(self):
        return self.user.username


from paypal.standard.ipn.signals import payment_was_successful
from paypal.standard.ipn.signals import payment_was_flagged
from django.dispatch import receiver

def confirm_payment(sender, **kwargs):
    s = sender.business
    s += '\n' + sender.invoice
    send_mail('Subject here', 'Here is the message. (Success!)\n' + s, 'from@example.com',
              ['it@princetonusg.com'], fail_silently=False)
    

payment_was_successful.connect(confirm_payment)

def handle_flagged(sender, **kwargs):
    send_mail('Subject here', 'Here is the message. (Flagged!)', 'from@example.com',
              ['it@princetonusg.com'], fail_silently=False)
    
payment_was_flagged.connect(handle_flagged)
