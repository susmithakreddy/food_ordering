from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    class Meta:
        db_table = 'restaurant'

    def __str__(self):
        return self.name

class MenuCategory(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='categories', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'menucategory'

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    category = models.ForeignKey(MenuCategory, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'menuitem'

    def __str__(self):
        return f"{self.name} - {self.price}"

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(max_length=255)
    customer_address = models.TextField()
    customer_phone = models.CharField(max_length=15)
    restaurant = models.ForeignKey(Restaurant, related_name='orders', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'order'

    def __str__(self):
        return f"Order {self.id} by {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    item_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'orderitem'

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} for {self.order.customer_name}"
