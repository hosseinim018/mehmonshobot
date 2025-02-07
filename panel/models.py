from django.db import models
from django.utils import timezone
from panel.assist import generate_uid
from django.core.validators import MinValueValidator


# Create your models here.
class Games(models.Model):
    name = models.CharField(max_length=100)

class Profile(models.Model):
  enter_name = models.CharField(max_length=255, blank=True, null=True)
  enter_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
  full_name = models.CharField(max_length=255, blank=True, null=True)
  username = models.CharField(max_length=255, blank=True, null=True)
  picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
  user_id = models.BigIntegerField()
  friends = models.ManyToManyField('self', through='profileFriend', blank=True)
  # login_code = models.CharField(max_length=255, blank=True, null=True)  # Can be blank if not used
  # referral_code = models.CharField(max_length=255, blank=True, null=True, default=generate_uid())  # Can be blank if not used
  status = models.CharField(max_length=20, default="Unregistered", choices=(('Registered', 'Registered'), ('Registering', 'Registering'), ('Unregistered', 'Unregistered')))
  unread_message_number = models.PositiveIntegerField(blank=True, null=True, default=0)
  unread_payment_number = models.PositiveIntegerField(blank=True, null=True, default=0)

  def __str__(self):
      return f"{self.username} ({self.full_name})"  # Use f-strings for cleaner formatting

class profileFriend(models.Model):
    from_user = models.ForeignKey(Profile, related_name='friend_set', on_delete=models.CASCADE)
    to_user = models.ForeignKey(Profile, related_name='to_friend_set', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')])

class Lottery(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='lottery_entries')  # User who participated
    register_date = models.DateTimeField(default=timezone.now, blank=True, null=True)  # Date and time of registration
    game = models.ForeignKey(Games, on_delete=models.CASCADE, related_name='lottery_game', blank=True, null=True)  # User who participated
    friends = models.ManyToManyField(Profile, blank=True, related_name='lottery_friends')  # Friend who participated (optional)
    ticket = models.CharField(max_length=255, blank=True, null=True, default=generate_uid())  # Can be blank if not used  # Ticket number for the lottery
    status = models.CharField(max_length=20, default="Unregistered", choices=(('Registered', 'Registered'), ('Registering', 'Registering'), ('Unregistered', 'Unregistered')))  # Payment status
    ticket_picture = models.ImageField(upload_to='img/uploads/', blank=True)
    payment_status = models.CharField(max_length=20, default="PENDING", choices=(('PENDING', 'Pending'), ('PAID', 'Paid'), ('FAILED', 'Failed')))  # Payment status
    payment_picture = models.ImageField(upload_to='img/uploads/', blank=True)
    winning = models.BooleanField(default=False)  # Whether the ticket is a winner

    def __str__(self):
        return f"Lottery for {self.game} by {self.profile.username} (Ticket: {self.ticket}) - {self.payment_status}"

class LotteryHistory(models.Model):
    """
    Model representing the history of a lottery event.

    Attributes:
        date (DateTimeField): The date and time when the lottery was held.
        winners (JSONField): A list of winners for the lottery event.
    """
    date = models.DateTimeField(default=timezone.now, blank=True)
    winners = models.JSONField(default=list)

    def __str__(self):
        """
        Returns a string representation of the LotteryHistory instance,
        including the date of the lottery and the list of winners.

        Returns:
            str: A formatted string displaying the lottery date and winners.
        """
        return f"Lottery on {self.date.strftime('%Y-%m-%d %H:%M:%S')} with winners: {self.winners}"

class Messages(models.Model):
  sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_messages')
  message = models.TextField(blank=True, null=True)
  sender_picture = models.ImageField(upload_to='img/uploads/', blank=True)
  answer = models.TextField(blank=True, null=True)
  answer_picture = models.ImageField(upload_to='img/uploads/', blank=True)
  status = models.CharField(max_length=20, choices=(('OPEN', 'Open'), ('CLOSED', 'Closed')), default='OPEN')
  created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)

class Admins(models.Model):
    name = models.CharField(max_length=255, blank=True)
    user_id = models.BigIntegerField()
    # login_code = models.CharField(max_length=255, blank=True, null=True, default=generate_uid())  # Can be blank if not used


class Setting(models.Model):
    # payment
    card_name = models.CharField(max_length=100)
    card_number = models.PositiveBigIntegerField(blank=True, null=True)
    price = models.PositiveIntegerField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=(('card-to-card', 'card-to-card'), ('gateway', 'gateway')), default='card-to-card')

    # lottery date
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    lottery_time = models.DateTimeField(blank=True, null=True)

    is_lottery_started = models.BooleanField(default=False)

    channel = models.CharField(max_length=255, blank=True)
    link = models.URLField(blank=True)

    total_unread_messages = models.PositiveIntegerField(blank=True, null=True, default=0)
    total_payments = models.PositiveIntegerField(blank=True, null=True, default=0)


class Payment(models.Model):
    # Payment status choices
    STATUS_CHOICES = [
        ('VERIFIED', 'VERIFIED'),
        ('PAID', 'PAID'),
        ('IN_BANK', 'IN_BANK'),
        ('FAILED', 'FAILED'),
        ('REVERSED', 'REVERSED'),
    ]

    # Payment method choices
    PAYMENT_METHOD_CHOICES = [
        ('card_to_card', 'Card-to-Card Transfer'),
        ('gateway', 'Payment Gateway'),
    ]

    # User who participated
    lottery = models.ForeignKey(Lottery, on_delete=models.CASCADE, related_name='lottery_payment')

    # Common fields for all payment types
    amount = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='VERIFIED')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    authority = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Fields specific to card-to-card transfers
    # sender_card_number = models.CharField(max_length=16, blank=True, null=True)  # Encrypt in production
    # receiver_card_number = models.CharField(max_length=16, blank=True, null=True)  # Encrypt in production
    # sender_name = models.CharField(max_length=255, blank=True, null=True)
    # receiver_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Payment {self.id} - {self.amount} ({self.status})"

    class Meta:
        ordering = ['-created_at']