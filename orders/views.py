from django.shortcuts import render, get_object_or_404, redirect
from .models import Restaurant, MenuCategory, MenuItem, Order, OrderItem
from django.views.decorators.csrf import csrf_exempt

def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = MenuItem.objects.filter(category__restaurant=restaurant)
    return render(request, 'orders/restaurant_detail.html', {'restaurant': restaurant, 'menu_items': menu_items})


def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    print('Restaurants:',restaurants)
    return render(request, 'orders/restaurant_list.html', {'restaurants': restaurants})

def menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    categories = restaurant.categories.all()
    return render(request, 'orders/menu.html', {'restaurant': restaurant, 'categories': categories})

@csrf_exempt
def create_order(request, restaurant_id):
    if request.method == 'POST':
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        customer_name = request.POST.get('customer_name')
        customer_address = request.POST.get('customer_address')
        customer_phone = request.POST.get('customer_phone')
        order = Order.objects.create(
            customer_name=customer_name,
            customer_address=customer_address,
            customer_phone=customer_phone,
            restaurant=restaurant
        )

        items = request.POST.getlist('items[]')
        quantities = request.POST.getlist('quantities[]')

        total_amount = 0
        for i in range(len(items)):
            menu_item = get_object_or_404(MenuItem, id=items[i])
            quantity = int(quantities[i])
            item_total = menu_item.price * quantity
            total_amount += item_total

            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                item_total=item_total
            )
        
        order.total_amount = total_amount
        order.save()
        return redirect('order_confirmation', order_id=order.id)

    return redirect('restaurant_list')

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_confirmation.html', {'order': order})
