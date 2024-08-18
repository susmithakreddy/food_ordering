from django.shortcuts import render, get_object_or_404, redirect
from .models import Restaurant, MenuCategory, MenuItem, Order, OrderItem
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Address, Order
from .forms import UserProfileForm, AddressForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')  # Redirect to the restaurant list or another page after login
    else:
        form = AuthenticationForm()
    return render(request, 'account/login.html', {'form': form})

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('index')

def signup_view(request):
    # have to add signup logic here
    pass

@login_required
def user_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    addresses = user_profile.addresses.all()
    orders = Order.objects.filter(user=request.user)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        address_form = AddressForm(request.POST)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('user_profile')
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user_profile = user_profile
            address.save()
            return redirect('user_profile')
    else:
        profile_form = UserProfileForm(instance=user_profile)
        address_form = AddressForm()
    
    return render(request, 'orders/user_profile.html', {
        'profile_form': profile_form,
        'address_form': address_form,
        'addresses': addresses,
        'orders': orders
    })

@login_required
def restaurant_detail(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    menu_items = MenuItem.objects.filter(category__restaurant=restaurant)

    if request.method == 'POST':
        selected_items = request.POST.getlist('menu_items')
        quantity = request.POST.getlist('quantity')

        if selected_items:
            order = Order.objects.create(
                user=request.user,
                restaurant=restaurant,
                total_amount=0
            )

            total_amount = 0
            for item_id, qty in zip(selected_items, quantity):
                item = get_object_or_404(MenuItem, id=item_id)
                item_total = item.price * int(qty)
                OrderItem.objects.create(
                    order=order,
                    menu_item=item,
                    quantity=int(qty),
                    item_total=item_total
                )
                total_amount += item_total

            order.total_amount = total_amount
            order.save()
            return redirect('order_summary', order_id=order.id)

    return render(request, 'orders/restaurant_detail.html', {
        'restaurant': restaurant,
        'menu_items': menu_items
    })

@login_required
def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'orders/restaurant_list.html', {'restaurants': restaurants})


@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_summary.html', {'order': order})


@login_required
def checkout(request, order_id):
    print(f"Order ID: {order_id}")
    order = Order.objects.get(id=order_id, user=request.user)
    print(f"Order: {order}")

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.menu_item.name,
                    },
                    'unit_amount': int(item.menu_item.price * 100),  # Convert to cents
                },
                'quantity': item.quantity,
            } for item in order.order_items.all()
        ],
        mode='payment',
        success_url=request.build_absolute_uri(f'/order-confirmation/{order.id}/'),
        cancel_url=request.build_absolute_uri(f'/order-summary/{order.id}/'),
    )
    print(f"Checkout Session: {checkout_session.url}")
    return redirect(checkout_session.url)



@csrf_exempt
def webhook(request):
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Fulfill the purchase
        fulfill_order(session)

    return HttpResponse(status=200)

@login_required
def fulfill_order(session):
    # Implement your order fulfillment logic here
    pass

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})
