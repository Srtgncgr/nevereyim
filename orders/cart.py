from decimal import Decimal
from products.models import Product

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            self.session['cart'] = {}
        self.cart = self.session.get('cart', {})

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.session['cart'] = self.cart
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session['cart'] = self.cart
            self.session.modified = True

    def __len__(self):
        """
        Get the total quantity of all items in the cart.
        """
        total = 0
        for item in self.cart.values():
            total += item['quantity']
        return total

    def get_total_price(self):
        """
        Get the total price of all items in the cart.
        """
        total = 0
        for item in self.cart.values():
            total += Decimal(item['price']) * item['quantity']
        return total

    def clear(self):
        """
        Remove the cart from session.
        """
        self.session['cart'] = {}
        self.session.modified = True

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item 