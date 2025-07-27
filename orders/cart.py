from decimal import Decimal
from django.conf import settings
from books.models import Book
import logging

logger = logging.getLogger(__name__)

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        logger.debug(f"Cart initialized: {self.cart}")

    def add(self, book, quantity=1, update_quantity=False):
        book_id = str(book.id)
        logger.debug(f"Adding book {book_id} with quantity {quantity}")
        
        if book_id not in self.cart:
            self.cart[book_id] = {
                'quantity': 0,
                'price': str(book.price)
            }
        
        if update_quantity:
            self.cart[book_id]['quantity'] = quantity
        else:
            self.cart[book_id]['quantity'] += quantity
            
        logger.debug(f"Cart after adding: {self.cart}")
        self.save()

    def save(self):
        logger.debug(f"Saving cart: {self.cart}")
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True
        logger.debug(f"Session after save: {self.session.get(settings.CART_SESSION_ID)}")

    def remove(self, book):
        book_id = str(book.id)
        if book_id in self.cart:
            del self.cart[book_id]
            self.save()

    def __iter__(self):
        book_ids = self.cart.keys()
        logger.debug(f"Iterating cart with book_ids: {book_ids}")
        books = Book.objects.filter(id__in=book_ids)
        cart = self.cart.copy()
        
        for book in books:
            cart[str(book.id)]['book'] = book
            
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True 