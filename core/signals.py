# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import *


# @receiver(post_save, sender=PurchaseProduct)
# def add_to_stock(sender, instance, created, **kwargs):
#     if created:
#         Stock.objects.create(
#             product_name=instance.product_name,
#             quantity=instance.quantity,
#             sell_price=instance.price,
#             description=instance.description,
#             added_by=instance.added_by,
#         )
