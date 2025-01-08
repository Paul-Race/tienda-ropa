# store/views/checkout.py
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from ..models import Cart, Coupon, Order, OrderItem, ShippingAddress
from ..forms import OrderForm, ShippingAddressForm

@login_required
def checkout(request):
    """Vista del proceso de checkout"""
    cart = Cart.objects.get(user=request.user)
    
    if not cart.items.exists():
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('cart_detail')

    # Obtener o crear dirección de envío predeterminada
    default_address = ShippingAddress.objects.filter(
        user=request.user, 
        default=True
    ).first()

    if request.method == 'POST':
        order_form = OrderForm(request.user, request.POST)
        address_form = ShippingAddressForm(request.POST)

        if order_form.is_valid() and (
            request.POST.get('use_existing_address') or address_form.is_valid()
        ):
            try:
                with transaction.atomic():
                    # Crear o actualizar dirección de envío
                    if request.POST.get('use_existing_address'):
                        shipping_address = default_address
                    else:
                        shipping_address = address_form.save(commit=False)
                        shipping_address.user = request.user
                        shipping_address.save()

                    # Crear orden
                    order = order_form.save(commit=False)
                    order.user = request.user
                    order.shipping_address = str(shipping_address)
                    
                    # Aplicar cupón si existe
                    coupon_id = request.session.get('coupon_id')
                    if coupon_id:
                        coupon = Coupon.objects.get(id=coupon_id)
                        if coupon.discount_amount:
                            order.discount = coupon.discount_amount
                        else:
                            order.discount = (
                                cart.total_amount * coupon.discount_percentage / 100
                            )
                        coupon.used_count += 1
                        coupon.save()
                        request.session['coupon_id'] = None

                    order.subtotal = cart.total_amount
                    order.save()

                    # Crear items de la orden
                    for cart_item in cart.items.all():
                        if cart_item.quantity > cart_item.product.stock:
                            raise Exception(
                                f'No hay suficiente stock de {cart_item.product.name}'
                            )

                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            product_name=cart_item.product.name,
                            product_price=cart_item.product.price,
                            quantity=cart_item.quantity,
                        )

                        # Actualizar stock
                        product = cart_item.product
                        product.stock -= cart_item.quantity
                        product.save()

                    # Limpiar carrito
                    cart.items.all().delete()

    

                    messages.success(
                        request,
                        'Pedido realizado exitosamente. Te enviaremos un email de confirmación.'
                    )
                    return redirect('order_success', order_id=order.id)

            except Exception as e:
                messages.error(request, str(e))
                return redirect('checkout')
    else:
        initial_data = {}
        if default_address:
            initial_data = {
                'street_address': default_address.street_address,
                'apartment_address': default_address.apartment_address,
                'city': default_address.city,
                'state': default_address.state,
                'zip_code': default_address.zip_code,
            }
        
        order_form = OrderForm(request.user)
        address_form = ShippingAddressForm(initial=initial_data)

    context = {
        'cart': cart,
        'order_form': order_form,
        'address_form': address_form,
        'default_address': default_address,
    }
    return render(request, 'store/checkout/checkout.html', context)

@login_required
def order_success(request, order_id):
    """Vista de confirmación de orden"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/checkout/success.html', {'order': order})