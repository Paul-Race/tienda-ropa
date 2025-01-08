# store/context_processors.py
from .models import Category, Cart
from .forms import ProductSearchForm

def categories(request):
    """Añade las categorías al contexto global de las plantillas"""
    return {
        'categories': Category.objects.all()
    }

def cart(request):
    """Añade la información del carrito al contexto global"""
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        return {
            'cart': cart,
            'cart_total_items': cart.total_items if cart else 0
        }
    return {'cart': None, 'cart_total_items': 0}

def search_form(request):
    """Añade el formulario de búsqueda al contexto global"""
    return {
        'search_form': ProductSearchForm(request.GET or None)
    }