from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import JsonResponse
from django.contrib.auth import logout
from .models import Category, Product, Order, OrderItem
from .cart import Cart
from .forms import OrderCreateForm, UserRegistrationForm, UserEditForm

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Фильтрация по цене
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Поиск
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    # Пагинация
    paginator = Paginator(products, 9)  # 9 товаров на странице
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    # Получаем похожие товары из той же категории
    similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:3]
    
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'similar_products': similar_products,
    })

@login_required
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Товар "{product.name}" добавлен в корзину',
            'cart_items_count': len(cart)
        })
    
    messages.success(request, f'Товар "{product.name}" добавлен в корзину')
    return redirect('shop:cart')

def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity, override_quantity=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Количество товара "{product.name}" обновлено',
            'cart_items_count': len(cart)
        })
    
    messages.success(request, f'Количество товара "{product.name}" обновлено')
    return redirect('shop:cart')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_items_count': len(cart)
        })
    
    return redirect('shop:cart')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart.html', {'cart': cart})

@login_required
def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            cart.clear()
            messages.success(request, 'Ваш заказ успешно создан!')
            return redirect('shop:profile')
    else:
        form = OrderCreateForm()
    
    return render(request, 'shop/checkout.html', {
        'cart': cart,
        'form': form,
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Аккаунт успешно создан! Теперь вы можете войти.')
            return redirect('shop:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'shop/register.html', {'form': form})

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'shop/profile.html', {'orders': orders})

@login_required
def profile_update(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()

        # Обновляем адрес в профиле
        if hasattr(user, 'profile'):
            user.profile.address = request.POST.get('address', '')
            user.profile.save()
        else:
            # Если профиль не существует, создаем его
            from .models import Profile
            Profile.objects.create(user=user, address=request.POST.get('address', ''))

        messages.success(request, 'Профиль успешно обновлен')
        return redirect('shop:profile')
    
    return redirect('shop:profile')

def welcome(request):
    # Получаем 3 самых популярных товара (по количеству заказов)
    popular_products = Product.objects.filter(available=True).annotate(
        order_count=Count('order_items')
    ).order_by('-order_count')[:3]
    
    return render(request, 'shop/welcome.html', {
        'popular_products': popular_products,
    })

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('shop:welcome')

def about(request):
    return render(request, 'shop/about.html')
