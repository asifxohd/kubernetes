from django.shortcuts import render,redirect
from user_authentication.models import CustomUser
from admin_home.models import Category,Product,SizeVariant,ProductImage
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import cache_control
from django.contrib.auth import authenticate, login


# function for loading the Admin Base Template
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def admin_base(request):
    return render(request, "admin_panel/admin_base.html")


# function for admin login
def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "User has No access to Admin panel")
                return redirect('admin_login')
        else:
            messages.error(request, "Invalid user")
            return redirect('admin_login')
    return render(request, 'admin_panel/admin_login.html')


#function for admin DashBoard
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def admin_dash(request):
    return render(request, "admin_panel/admin_dash.html", )


# function for showing the all users on the admin side
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def admin_users(request):
    users = CustomUser.objects.all().exclude(is_superuser=True).order_by('id')
    return render(request, "admin_panel/users.html", {'users': users})


# function for showing all catogerys in the admin side 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def admin_catogory(request):
    catogory = Category.objects.all().order_by('id')
    return render(request, 'admin_panel/categories.html', {'categories':catogory})


#function for changing the user status (block and Unblock)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def user_status(request,id):
    user = CustomUser.objects.filter(id=id)[0]
    if user.is_active == True:
        user.is_active = False
        user.save()
    else:
        user.is_active = True
        user.save()
    return redirect('admin_users')

 
# function for changing the catogery status (list and Unlist)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def category_status(request, id):
    cat = Category.objects.filter(id=id)[0]
    if cat.is_active == True:
        cat.is_active = False
        cat.save()
    else:
        cat.is_active = True
        cat.save()
        
    return redirect('admin_catogeory')


# function for adding product data like image ,size variants,etc.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def add_products(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        discount_price = request.POST.get('discount_price', 0.0)
        category_id = request.POST['category']
        gender = request.POST['gender']

        product = Product(
            name=name,
            description=description,
            price=price,
            discount_price=discount_price,
            category_id=category_id,
            gender=gender,
        )

        product.save()
        
        for i in range(41, 46):  
            size = i
            name = f'size_{i}'
            quantity = request.POST.get(name, 0)  # Use default value 0 if quantity is not provided
            print(quantity, name)
            if int(quantity) >= 0:
                SizeVariant(product=product, size=size, quantity=quantity).save()
            else:
                return redirect('admin_products')
                
        print('image is comming here')
        images = request.FILES.getlist('images')
        for image in images:
            ProductImage(product=product, image=image).save()
        print("product saved seccefully ")

        return redirect('admin_products')

    return render(request, 'admin_panel/add_products.html', {'categories': categories})


# function for edit catogory
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def edit_category(request, id):
    category = Category.objects.get(id=id)
    
    if request.method == 'POST':
        updated_name = request.POST.get('category_name')
        
        if updated_name != category.name:
            if Category.objects.filter(name=updated_name).exists():
                messages.error(request, "Category with this name already exists")
            else:
                category.name = updated_name
                category.save()
                return redirect('admin_category')
        
    return render(request, 'admin_panel/editcat.html', {'category_name': category.name})


# function for add catogery
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def add_category(request):
    if request.method == 'POST':
        newCatogeryName = request.POST.get('new_updated_catogory')
        if Category.objects.filter(name=newCatogeryName):
            messages.error(request, "Category already exists")
            return redirect('add_category')
            
        obj = Category(name=newCatogeryName)
        obj.save()
        return redirect('admin_catogeory')
    return render(request,'admin_panel/add_categories.html')


# function for showing the product variant, image on the product variant page 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def show_product_varient(request, id):
    product = Product.objects.filter(pk=id, status=True).prefetch_related('productimage_set', 'sizevariant_set').first()
    print(product)
    return render(request, 'admin_panel/product_varient.html', {'product': product})


# function for showing the product on trash page variant, image on the product variant page 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def trash_product_varient(request, id):
    product = Product.objects.filter(pk=id, status=False).prefetch_related('productimage_set', 'sizevariant_set').first()
    print(product)
    return render(request, 'admin_panel/product_varient.html', {'product': product})


    
# function to show products on the admin side
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def admin_products(request):
    products = Product.objects.prefetch_related('productimage_set').filter(status=True)
    return render(request, "admin_panel/products.html", {'products': products})


# function for soft-deleting the product
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def ajax_soft_delete_product(request, id):
    product = Product.objects.filter(id=id).first()
    if product:
        product.status = False
        product.save()
        return redirect('admin_products')  
    else:
        return redirect('admin_products')
    
    
# function for loading the product Trash coloumn 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def admin_trash(request):
    products = Product.objects.prefetch_related('productimage_set').filter(status=False)
    return render(request, "admin_panel/trash.html", {'products': products})


# function for restoring product from the product Trash
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def restore_product(request, id):
    product = Product.objects.filter(id=id).first()
    if product:
        product.status = True
        product.save()
        return render(request,"admin_panel/trash.html")
    else:
        return redirect('admin_trash')


# function for editing the product details and sending the context for the input fields 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def edit_product(request, id):
    product = Product.objects.get(id=id)
    images = ProductImage.objects.filter(product=product)
    size_variants = SizeVariant.objects.filter(product=product)
    cat = Category.objects.all()

    context = {
        'cat': cat,
        'product': product,
        'images': images,
        'size_variants': size_variants,
    }

    if request.method == 'POST':
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.price = request.POST['price']
        product.discount_price = request.POST.get('discount_price', 0.0)
        product.category_id = request.POST['category']
        product.gender = request.POST['gender']

        product.save()

        for i in range(41, 46):
            size = i
            name = f'size_{i}'
            print(request.POST.get(name))
            quantity = request.POST.get(name, 0)  
            # print(f"Size: {size}, Quantity: {quantity}, Field Name: {name}")
    
            if int(quantity) >= 0:
                existing_size_variant = SizeVariant.objects.filter(product=product, size=size).first()
                if existing_size_variant:
                    existing_size_variant.quantity = quantity
                    existing_size_variant.save()
                else:
                    SizeVariant(product=product, size=size, quantity=quantity).save()
            else:
                return redirect('admin_products')

        new_images = request.FILES.getlist('images')

        if new_images:
            # Delete existing images and save the new ones
            ProductImage.objects.filter(product=product).delete()
            for image in new_images:
                ProductImage(product=product, image=image).save()


        print("Product updated successfully")

        return redirect('admin_products')

    return render(request, 'admin_panel/edit_products.html', context)


    