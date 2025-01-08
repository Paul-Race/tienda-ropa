# store/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Cart, Order, OrderItem, Product
from .utils.email import send_order_confirmation_email, send_low_stock_alert

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    """Crear un carrito cuando se registra un nuevo usuario"""
    if created:
        Cart.objects.create(user=instance)

@receiver(post_save, sender=Order)
def send_order_emails(sender, instance, created, **kwargs):
    """Enviar emails cuando se crea o actualiza un pedido"""
    if created:
        send_order_confirmation_email(instance)
    elif instance.status == 'shipped':
        send_shipping_confirmation_email(instance)

@receiver(post_save, sender=OrderItem)
def update_product_stock(sender, instance, created, **kwargs):
    """Actualizar el stock del producto cuando se crea un pedido"""
    if created and instance.product:
        product = instance.product
        product.stock -= instance.quantity
        product.save()
        
        # Enviar alerta si el stock es bajo
        if product.stock <= 5:
            send_low_stock_alert(product)

# Registrar las señales en el archivo apps.py
class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        import store.signals