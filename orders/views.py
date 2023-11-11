from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from user_authentication.models import CustomUser
from cart.models import CartItem
from user_profile.models import Address
from .models import Orders,OrdersItem,CancelledOrderItem
from django.db import transaction
from datetime import timedelta 
from django.http import JsonResponse
from admin_home.models import SizeVariant
import uuid
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
import razorpay

# for the Razorpay
client = razorpay.Client(auth=('rzp_test_F83XKwHAQwFDZG', 'etDY4jG2xDLoFngOnDsM7wqY'))

# Create your views here.
def load_order_page(request):
    if 'user' in request.session:
        order_id = request.session['ord_id']
        current_order = Orders.objects.get(order_id=order_id)
        context= {
        "current_order" : current_order
        }
        
    return render(request, 'user_side/order_details.html',context)

#function for loading order history
def order_history(request):
    if 'user' in request.session:
        email = request.session['user']
        user = CustomUser.objects.get(email=email)
        orders = Orders.objects.filter(user=user).order_by('order_date').exclude(payment_status="temp")
        order_items = OrdersItem.objects.filter(order__in=orders).order_by('order')

    return render(request, 'user_side/order_history.html', {'order_items':order_items})


def place_order(request):
    if 'user' in request.session:
        user_email = request.session['user']
        user_instance = CustomUser.objects.get(email=user_email)
        print("address_id")

        if request.method == 'POST':
            address_id = request.POST.get('address')
            payment_type = request.POST.get('payment')
            cart_items = CartItem.objects.filter(user=user_instance)
            print(payment_type)
            delivery_address = Address.objects.filter(id=address_id).first()
            
            if payment_type == "COD":
                if cart_items.exists():
                    try:
                        with transaction.atomic():
                            # Create a new order instance
                            order = Orders.objects.create(
                                user=user_instance,
                                address=delivery_address,
                                payment_method=payment_type,
                                quantity=0,
                            )

                            for cart_item in cart_items:
                                # Create an order item for each cart item
                                order_item = OrdersItem.objects.create(
                                    order=order,
                                    variant=cart_item.size_variant,
                                    quantity=cart_item.quantity,
                                    price=cart_item.size_variant.price,
                                    status='Order confirmed',
                                )
                                
                                #for dicreamenting quantity
                                qua  = cart_item.size_variant
                                qua.quantity -= cart_item.quantity
                                qua.save()
                                
                                
                                # Update the order's price, total_amount, and quantity
                                order.quantity += order_item.quantity

                                cart_item.delete()

                            # Calculate the expected delivery date 
                            order.expected_delivery_date = (order.order_date + timedelta(days=7))

                            # Save the order
                            order.save()
                            request.session['order_id'] = str(order.order_id)
                        

                            response_data = {
                                'success': True,
                                'message': 'Order placed successfully',
                                'order_id': order.order_id,
                            }
                            return JsonResponse(response_data)

                    except Exception as e:
                        print(f"Error while placing the order: {e}")
                        response_data = {
                            'success': False,
                            'message': 'Error while placing the order',
                        }
                        return JsonResponse(response_data)

                else:
                    response_data = {
                        'success': False,
                        'message': 'Your cart is empty',
                    }
                    return JsonResponse(response_data)
                
            elif payment_type == "onlinePayment":
                
                try:
                    if cart_items.exists():
                        # Create a new order instance
                        order = Orders.objects.create(
                            user=user_instance,
                            address=delivery_address,
                            payment_method=payment_type,
                            quantity=0,
                            payment_status="temp"
                        )

                        request.session['ord_id'] = str(order.order_id)
                        for cart_item in cart_items:
                            # Create an order item for each cart item
                            order_item = OrdersItem.objects.create(
                                order=order,
                                variant=cart_item.size_variant,
                                quantity=cart_item.quantity,
                                price=cart_item.size_variant.price,
                                status='Pending',
                            )

                        # Calculate the expected delivery date
                        order.expected_delivery_date = (order.order_date + timedelta(days=7))

                        order.save()
                        # for item in cart_items:
                        #     amount_in_paise = item.size_variant.price * item.quantity
                        # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        amount_in_paise = sum(cart_items.values_list('cart_price', flat=True))
                        print(amount_in_paise)
                       

                        # Create a Razorpay order
                        razorpay_order_data = {
                            'amount': amount_in_paise*100,
                            'currency': 'INR',
                            'receipt': str(order.order_id),
                        }

                        # Use the Razorpay client to create the order
                        razorpay_order = client.order.create(data=razorpay_order_data)
                        
                        return JsonResponse({'razorpay_order':razorpay_order, "success":False})

                    else:
                        response_data = {
                            'success': False,
                            'message': 'Your cart is empty',
                        }
                        return JsonResponse(response_data)

                except Exception as e:
                    print(f"Error while placing the order: {e}")
                    response_data = {
                        'success': False,
                        'message': 'Error while placing the order',
                    }
                    return JsonResponse(response_data)
    else:
        response_data = {
            'success': False,
            'message': 'User not logged in',
        }
        return JsonResponse(response_data)


def verifyPayment(request):
    email = request.session['user']
    user = CustomUser.objects.get(email=email)
    cart_items = CartItem.objects.filter(user=user)
    ord_id = request.session['ord_id']
    order = Orders.objects.get(order_id=ord_id)
    order.payment_status = "success"
    order.save() 
    order_items = OrdersItem.objects.filter(order=order) 
    
    for order_item in order_items:  # Fixed: Iterate over order_items
        order_item.status = 'Order confirmed'
        order_item.save()  # Fixed: Save the updated order_item
        
        qua = order_item.variant
        qua.quantity -= order_item.quantity
        qua.save()

    cart_items.delete()  # Delete all associated cart_items
    
    return JsonResponse({"success": True})

   

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admin_orders(request):
    ite = OrdersItem.objects.exclude(order__payment_status="temp")
    items = ite.exclude(status="Cancellation request sent")
    print(items)
    return render(request,'admin_panel/admin_orders.html',{'items':items})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def view_order_details(request, id):
    obj = OrdersItem.objects.get(id=id)
    return render(request,'admin_panel/view_order_details.html',{'obj':obj})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def change_status(request,id):
    obj = OrdersItem.objects.get(id=id)
    status = request.POST.get('statusRadio')
    obj.status = status
    obj.save()
    return redirect('view_order_details',id=obj.id)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def cancel_request_page(request):
    order = OrdersItem.objects.filter(status="Cancellation request sent")
    return render(request, 'admin_panel/cancel_requests.html',{'order':order})


def cancel_request(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        cancel_reason = request.POST.get('cancel_reason')
        print(order_id)
        print(cancel_reason)

        order = OrdersItem.objects.filter(id=order_id).first()
        print(order)
        if order:
            order.status = "Cancellation request sent"
            order.save()

            cr = CancelledOrderItem.objects.create(order_item=order)
            cr.cancellation_reason = cancel_reason
            cr.save()
            response_data = {
                'success': True,
                'message': 'Cancellation request sent successfully',
                'order_status': order.status,
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': 'Order not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def cancell_product(request, id):
    order = OrdersItem.objects.get(id=id)
    order.status = 'Cancelled'
    order.variant.quantity += order.quantity
    order.variant.save()
    
    order.save()
    return redirect('admin_orders')


