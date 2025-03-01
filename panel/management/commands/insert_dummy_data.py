from django.core.management.base import BaseCommand
from django.utils import timezone
from panel.models import Profile, Lottery, Games

class Command(BaseCommand):
    help = 'Insert dummy data into the Profile model'

    def handle(self, *args, **options):
        for i in range(1, 101):  # Generate 100 users
            name = f'user{i}'
            profile = Profile(
                enter_name=name,
                enter_id=name,
                full_name=name,
                username=name,
                user_id=f'{i:010d}',  # 10-digit phone number
                status='Registered',  # Default status
            )
            profile.save()

            game = Games(
                name=f'game{i}',
            )
            game.save()

            lottery = Lottery(
                profile=profile,  # Pass the profile object itself
                game=game,  # Pass the game object itself
                status='Registered',
                payment_status='PAID',
                ticket_picture='img/tickets/b2156dfd_1740098822.274514.png',
            )
            lottery.save()

        self.stdout.write(self.style.SUCCESS('Successfully inserted dummy data into Profile model'))
