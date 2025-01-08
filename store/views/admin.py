# store/views/admin.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import HttpResponse
import csv
import xlsxwriter
from io import BytesIO
from ..models import (
    Product, Category, Brand, Order, 
    OrderItem, Coupon
)
from ..forms import (
    ProductForm, CategoryForm, BrandForm,
    OrderStatusForm, CouponForm
)
from ..decorators import staff_required

@staff_required
def admin_dashboard(request):
    """Dashboard administrativo"""
    # Estadísticas generales
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_customers = User.objects.filter(is_staff=False).count()
    
    # Ventas del último mes
    thirty_days_ago = timezone.now() - timedelta(days=30)
    monthly_sales = Order.objects.filter(
        created_at__gte=thirty_days_ago,
        status='delivered'
    ).aggregate(
        total=Sum('total')
    )['total'] or 0
    
    # Productos con stock bajo
    low_stock_threshold = 5  # Definir en settings
    low_stock_products = Product.objects.filter(
        stock__lte=low_stock_threshold
    )
    
    # Productos más vendidos
    top_products = OrderItem.objects.values(
        'product__name'
    ).annotate(
        total_sold=Count('id')
    ).order_by('-total_sold')[:5]
    
    # Ventas por mes (últimos 6 meses)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_orders = Order.objects.filter(
        created_at__gte=six_months_ago
    ).values(
        'created_at__month'
    ).annotate(
        total=Sum('total')
    ).order_by('created_at__month')
    
    context = {
        'total_orders': total_orders,
        'total_products': total_products,
        'total_customers': total_customers,
        'monthly_sales': monthly_sales,
        'low_stock_products': low_stock_products,
        'top_products': top_products,
        'monthly_orders': monthly_orders,
    }
    return render(request, 'store/admin/dashboard.html', context)

@staff_required
def product_list_admin(request):
    """Lista de productos para administración"""
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'store/admin/product_list.html', {'products': products})

@staff_required
def product_create(request):
    """Crear nuevo producto"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('product_list_admin')
    else:
        form = ProductForm()
    
    return render(request, 'store/admin/product_form.html', {'form': form})

@staff_required
def product_edit(request, pk):
    """Editar producto existente"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('product_list_admin')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'store/admin/product_form.html', {
        'form': form,
        'product': product
    })

@staff_required
def product_delete(request, pk):
    """Eliminar producto"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('product_list_admin')
    
    return render(request, 'store/admin/product_confirm_delete.html', {
        'product': product
    })

@staff_required
def order_list_admin(request):
    """Lista de órdenes para administración"""
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'store/admin/order_list.html', {'orders': orders})

@staff_required
def order_detail_admin(request, order_id):
    """Detalle de orden para administración"""
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estado de orden actualizado.')
            return redirect('order_list_admin')
    else:
        form = OrderStatusForm(instance=order)
    
    return render(request, 'store/admin/order_detail.html', {
        'order': order,
        'form': form
    })

@staff_required
def export_orders_csv(request):
    """Exportar órdenes a CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Cliente', 'Email', 'Total', 'Estado',
        'Fecha de creación', 'Productos'
    ])
    
    orders = Order.objects.all()
    for order in orders:
        writer.writerow([
            order.id,
            order.user.get_full_name(),
            order.user.email,
            order.total,
            order.get_status_display(),
            order.created_at,
            ', '.join([
                f"{item.quantity}x {item.product_name}"
                for item in order.items.all()
            ])
        ])
    
    return response

@staff_required
def export_orders_excel(request):
    """Exportar órdenes a Excel"""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Definir formatos
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#F7F7F7',
        'border': 1
    })
    
    # Escribir encabezados
    headers = [
        'ID', 'Cliente', 'Email', 'Total', 'Estado',
        'Fecha de creación', 'Productos'
    ]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Escribir datos
    orders = Order.objects.all()
    for row, order in enumerate(orders, start=1):
        worksheet.write(row, 0, order.id)
        worksheet.write(row, 1, order.user.get_full_name())
        worksheet.write(row, 2, order.user.email)
        worksheet.write(row, 3, float(order.total))
        worksheet.write(row, 4, order.get_status_display())
        worksheet.write(row, 5, order.created_at.strftime('%Y-%m-%d %H:%M'))
        worksheet.write(row, 6, ', '.join([
            f"{item.quantity}x {item.product_name}"
            for item in order.items.all()
        ]))
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="orders.xlsx"'
    
    return response