# store/views/cart.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from ..models import Cart, CartItem, Product, Coupon
from ..forms import CartAddProductForm
from django.utils import timezone

@login_required
def cart_detail(request):
    """Vista del carrito de compras"""
    cart = Cart.objects.get_or_create(user=request.user)[0]
    
    for item in cart.items.all():
        item.update_form = CartAddProductForm(
            initial={'quantity': item.quantity, 'update': True}
        )
    
    coupon_id = request.session.get('coupon_id')
    coupon = None
    if coupon_id:
        try:
            coupon = Coupon.objects.get(
                id=coupon_id,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now(),
                active=True
            )
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
    
    context = {
        'cart': cart,
        'coupon': coupon,
    }
    return render(request, 'store/cart/detail.html', context)

@login_required
def cart_add(request, product_id):
    """Añadir producto al carrito"""
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        quantity = cd['quantity']
        
        if product.stock < quantity:
            messages.error(
                request,
                'No hay suficiente stock disponible.'
            )
            return redirect('product_detail', slug=product.slug)
        
        cart = Cart.objects.get_or_create(user=request.user)[0]
        try:
            cart_item = cart.items.get(product=product)
            if cart_item.quantity + quantity > product.stock:
                messages.error(
                    request,
                    'No hay suficiente stock disponible.'
                )
            else:
                cart_item.quantity += quantity
                cart_item.save()
                messages.success(
                    request,
                    'Producto actualizado en el carrito.'
                )
        except CartItem.DoesNotExist:
            CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity
            )
            messages.success(
                request,
                'Producto añadido al carrito.'
            )
    
    return redirect('cart_detail')

@login_required
def cart_update(request):
    """Actualizar cantidad de producto en el carrito"""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    cart = Cart.objects.get(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    
    if quantity > product.stock:
        return JsonResponse({
            'status': 'error',
            'message': 'No hay suficiente stock disponible.'
        })
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    cart_total = cart.total_amount
    cart_items = cart.total_items
    
    return JsonResponse({
        'status': 'success',
        'cart_total': cart_total,
        'cart_items': cart_items
    })

@login_required
def cart_remove(request, product_id):
    """Eliminar producto del carrito"""
    cart = Cart.objects.get(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
        messages.success(request, 'Producto eliminado del carrito.')
    except CartItem.DoesNotExist:
        pass
    
    return redirect('cart_detail')

@login_required
def apply_coupon(request):
    """Aplicar cupón de descuento"""
    code = request.POST.get('code')
    try:
        coupon = Coupon.objects.get(
            code__iexact=code,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now(),
            active=True
        )
        
        cart = Cart.objects.get(user=request.user)
        cart_total = cart.total_amount
        
        if coupon.minimum_amount and cart_total < coupon.minimum_amount:
            messages.error(
                request,
                f'El monto mínimo para usar este cupón es ${coupon.minimum_amount}'
            )
        elif coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
            messages.error(
                request,
                'Este cupón ya ha alcanzado su límite de uso.'
            )
        else:
            request.session['coupon_id'] = coupon.id
            messages.success(
                request,
                'Cupón aplicado exitosamente.'
            )
    except Coupon.DoesNotExist:
        messages.error(
            request,
            'Cupón inválido o expirado.'
        )
    
    return redirect('cart_detail')

@login_required
def remove_coupon(request):
    """Eliminar cupón aplicado"""
    request.session['coupon_id'] = None
    messages.success(request, 'Cupón removido exitosamente.')
    return redirect('cart_detail')