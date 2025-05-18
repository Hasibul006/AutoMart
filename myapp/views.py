from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from myapp.models import Product
from myapp.models import Cart
from myapp.models import Category
from myapp.models import Order
from myapp.models import OrderItem
from django.db.models import Q
from django.core.paginator import Paginator
User = get_user_model() 

def delete_product(request, product_id):
    if not request.user.role == 'admin':
        return HttpResponseForbidden("You are not authorized to delete this product.")
    
    product_to_delete = get_object_or_404(Product, id=product_id)
    product_to_delete.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect('/admin_dashboard')

def update_product(request, product_id):

    if not request.user.role == 'admin':
        return HttpResponseForbidden("You are not authorized to update this product.")

    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        print(product.image)
        id = request.POST.get('id')
        name = request.POST.get('name')
        image = request.FILES.get('image')  
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        company = request.POST.get('company')
        category = request.POST.get('category')
        product.id = id
        product.name = name
        if image:  
            product.image = image
        product.description = description
        product.price = price
        product.stock = stock
        product.company = company
        category_obj = get_object_or_404(Category, name=category)
        product.category = category_obj
        product.save()
        messages.success(request, "Product updated successfully.")
        return redirect('/admin_dashboard')
    categories = Category.objects.all()
    return render(request, 'update_product.html', {'product': product, 'categories': categories})   

def add_category(request):

    if not request.user.role == 'admin':
        return HttpResponseForbidden("You are not authorized to add a category.")
    
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        if name:
            Category.objects.create(name=name, image=image)
            messages.success(request, f"Category '{name}' added successfully.")
        else:
            messages.error(request, "Category name cannot be empty.")
    for c in Category.objects.all():
        print(c.image)
    return redirect('admin_dashboard')    

def products(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    sort_by = request.GET.get('sort', 'name')  # Default sorting by name

    products = Product.objects.all()
    categories = Category.objects.all()
    selected_category = None
    if request.user.is_authenticated:
        total_cart = Cart.objects.filter(user=request.user, checkout=False).count()
    else:
        total_cart = 0

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if category_id:
        selected_category = Category.objects.filter(id=category_id).first()
        if selected_category:
            products = products.filter(category=selected_category)

    # Apply sorting
    if sort_by == 'price':
        products = products.order_by('price')
    else:
        products = products.order_by('name')

    # Pagination
    paginator = Paginator(products, 9)  # Show 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'sort_by': sort_by,
        'total_cart': total_cart,
    }
    return render(request, 'products.html', context)

def delete_category(request, category_name):
    if not request.user.role == 'admin':
        return HttpResponseForbidden("You are not authorized to delete this category.")
    
    category_to_delete = get_object_or_404(Category, name=category_name)
    if Product.objects.filter(category=category_to_delete).exists():
        messages.error(request, "Cannot delete a category with associated existing products.")
        return redirect('/admin_dashboard')
    category_to_delete.delete()
    messages.success(request, "Category deleted successfully.")
    return redirect('/admin_dashboard')

def add_product(request):
    if not request.user.role == 'admin':
        return HttpResponseForbidden("You are not authorized to add a product.")
    if not request.user.is_authenticated:
        return redirect('/login')
    
    if request.method == 'POST':
        # Get POST data
        name = request.POST.get('name').strip()
        image = request.FILES.get('image')
        description = request.POST.get('description').strip()
        price = request.POST.get('price').strip()
        stock = request.POST.get('stock').strip()
        company = request.POST.get('company').strip()
        category = request.POST.get('category').strip()

        # Log category value for debugging
        print(f"Submitted category: '{category}'")
        print(f"Existing categories: {[c.name for c in Category.objects.all()]}")

        # Check if category exists
        try:
            category_obj = Category.objects.get(name=category)
        except Category.DoesNotExist:
            print(f"Category does not exist: {category}")
            messages.error(request, "The selected category does not exist.")
            return redirect('/add_product')

        # Check if the product already exists
        if Product.objects.filter(name=name).exists():
            messages.error(request, "Product already exists.")
            return redirect('/add_product')

        # Create and save the new product
        product = Product(name=name,image=image, description=description, price=price, stock=stock, company=company, category=category_obj)
        product.save()
        messages.success(request, "Product added successfully.")
        return redirect('/admin_dashboard')

    # Fetch all categories for the form
    categories = Category.objects.all()
    return render(request, 'add_product.html', {'categories': categories})

def index(request):
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('/admin_dashboard')
    products = Product.objects.all()
    if request.user.is_authenticated:
        total_cart = Cart.objects.filter(user=request.user, checkout=False).count()
    else:
        total_cart = 0
    print(total_cart)
    top_products = Product.objects.all().order_by('-stock')[:4]
    categories = Category.objects.all()
    return render(request, 'index.html', {'products': products, 'categories': categories, 'top_products' : top_products, 'total_cart': total_cart})

def search(request):
    query = request.GET.get('name', '')
    product = Product.objects.filter(name__icontains=query).first()

    if product:
        return redirect(f'/product_details/{product.id}')

    return redirect('/')

def add_to_cart(request, product_id, quantity=1):
    if not request.user.is_authenticated:
        return redirect('/login')
    
    product = get_object_or_404(Product, id=product_id)
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user, product=product)
    cart.quantity += quantity
    cart.save()
    return redirect('/cart')

def add_to_cart_with_quantity(request, product_id):
    if not request.user.is_authenticated:
        return redirect('/login')
    quantity = int(request.POST.get('quantity', 1))
    return add_to_cart(request, product_id, quantity)

def update_cart_quantity(request, product_id):
    if not request.user.is_authenticated:
        return redirect('/login')
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)
        user = request.user
        cart = Cart.objects.filter(user=user, product=product).first()
        if cart:
            cart.quantity = quantity
            cart.save()
    return redirect('cart')

def remove_from_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('/login')
    product = get_object_or_404(Product, id=product_id)
    user = request.user
    cart = Cart.objects.filter(user=user, product=product).first()
    if cart:
        cart.delete()
    return redirect('/cart')

def cart(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    
    user = request.user
    cart_items = Cart.objects.filter(user=user, checkout=False)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

def checkout(request):
    if not request.user.is_authenticated:
        total_cart = 0
        return redirect('/login')
    else:
        total_cart = Cart.objects.filter(user=request.user).count()
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price, 'total_cart': total_cart})

def place_order(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    user = request.user
    cart_items = Cart.objects.filter(user=user, checkout=False)
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')
        total_price = sum(item.get_total_price() for item in cart_items)
        order = Order(user=user, fullname=fullname, email=email, phone=phone, address=address, payment_method=payment_method, total_price=total_price)
        order.save()
        for item in cart_items:
            item.product.stock -= item.quantity
            item.product.save()
            item.delete()
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price * item.quantity)
        return redirect('/') 
    
def product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    # Calculate the grand total and delivery charge
    quantity = int(request.GET.get('quantity', 1))  # default quantity is 1
    delivery_charge = 50
    total_price = product.price * quantity
    grand_total = total_price + delivery_charge
    if request.user.is_authenticated:
        total_cart = Cart.objects.filter(user=request.user, checkout=False).count()
    else:
        total_cart = 0
    
    context = {
        'product': product,
        'quantity': quantity,
        'total_price': total_price,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
        'total_cart': total_cart,
    }
    return render(request, 'product_details.html', context)

def delete_user(request, user_name):
    if request.user.role != 'admin':
        messages.error(request, "You are not authorized to delete users.")
        return redirect('/')
    
    user_to_delete = get_object_or_404(User, username=user_name)
    # Optional: Prevent admin from deleting themselves
    if user_to_delete.role == 'admin':
        messages.error(request,"You cannot delete an admin.")
        return redirect('/admin_dashboard')
    if request.user.role == 'user':
        messages.error(request,"You are not authorized to delete users.")
        return redirect('/admin_dashboard')
    if user_to_delete == request.user:
        print(request.user.username)
        messages.error(request,"You cannot delete yourself.")
        return redirect('/admin_dashboard')

    user_to_delete.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('/admin_dashboard')

def admin_dashboard(request):
    if not request.user.is_authenticated or request.user == None:
        return redirect('/login')
    if request.user and request.user.role != 'admin':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('/')
    
    if request.method == 'POST':
        logout(request)
        messages.success(request, "Logged out successfully.")
        return redirect('/')

    users = User.objects.all()           # Fetch all users
    products = Product.objects.all()     # Fetch all products
    categories = Category.objects.all()
    context = {
        'users': users,
        'products': products,
        'categories': categories
    }
    return render(request, 'admin_dashboard.html', context)

def edit_user(request, user_name):
    if not request.user.is_authenticated:
        return redirect('/login')
    user = get_object_or_404(User, username=user_name)

    if user.role == 'admin' and user.username != request.user.username:
        messages.error(request, "You cannot update the info of an admin.")
        return redirect('/admin_dashboard')

    if not request.user.role == 'admin' and request.user.role == 'user' and user != request.user:
        messages.error(request, "Unauthorized access.")
        return redirect('profile')

    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        image = request.FILES.get('image')
        print(image)
        
        user.fullname = fullname
        user.email = email
        user.username = username
        user.phone = phone
        user.address = address
        if image:
            user.profile_image = image
        user.save()

        messages.success(request, "User updated successfully.")
        return redirect('/admin_dashboard' if request.user.role == 'admin' else '/profile')

    return render(request, 'edit_user.html', {'user': user})

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)

        if user is not None:  
            auth_login(request, user) 

            if user.role == 'admin':
                messages.success(request, "Logged in successfully as admin.")
                return redirect('/admin_dashboard')  
            else:
                messages.success(request, "Logged in successfully as user.")
                return redirect('/')  

        else: 
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html')

    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname').strip()
        email = request.POST.get('email').strip()
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        phone = request.POST.get('phone').strip()
        address = request.POST.get('address').strip()
        image = request.FILES.get('image')


        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different username.")
            return render(request, 'signup.html')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists. Please choose a different email.")
            return render(request, 'signup.html')

        # Create the user
        user = User.objects.create_user(username=username, email=email, fullname=fullname, password=password, phone=phone, address=address, role='user', profile_image=image)
        user.save()

        auth_login(request, user)

        if(user.role == 'admin'):
            return redirect('/admin_dashboard')
        else:
            return redirect('/')
        
    return render(request, 'signup.html')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('/login') 
    
    recent_orders = Order.objects.filter(user=request.user).order_by('-ordered_at')[:5]
    return render(request, 'profile.html', {'user': request.user, 'orders': recent_orders})  

def orderDetails(request, order_id):
    if not request.user.is_authenticated:
        return redirect('/login')
    order = get_object_or_404(Order, id=order_id)
    if order.user != request.user:
        return redirect('/')
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'orderDetails.html', {'order': order, 'order_items': order_items})

def logout(request):
    auth_logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('/')
