from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from main.models import Comment
from main.utilities import (send_activation_notification,
                            send_new_comment_notification)

post_register = Signal()


@receiver(post_register)
def post_register_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs["instance"])


@receiver(post_save, sender=Comment)
def post_save_dispatcher(sender, **kwargs):
    author = kwargs["instance"].bb.author
    if kwargs["created"] and author.send_messages:
        send_new_comment_notification(kwargs["instance"])
