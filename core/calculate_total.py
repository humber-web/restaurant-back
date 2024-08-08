from .models import MenuItem

def calculate_totals(order_items):
    total_amount = 0
    total_iva = 0
    for item in order_items:
        menu_item = MenuItem.objects.get(pk=item['menu_item'])
        quantity = item['quantity']
        total_amount += menu_item.price * quantity
        total_iva += menu_item.iva * quantity
    return total_amount, total_iva