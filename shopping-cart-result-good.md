Certainly! Below is a simple implementation of a shopping cart in Python, adhering to the coding tendencies and practices you described for Alex.

### ShoppingCart Implementation

```python
from typing import List, Dict, Optional

class Item:
    """Represents an item in the shopping cart."""
    
    def __init__(self, name: str, price: float, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        if price < 0:
            raise ValueError("Price cannot be negative.")
        
        self.name = name
        self.price = price
        self.quantity = quantity

    def total_price(self) -> float:
        """Calculate the total price for this item."""
        return self.price * self.quantity

class ShoppingCart:
    """Represents a shopping cart containing multiple items."""
    
    def __init__(self) -> None:
        self.items: Dict[str, Item] = {}

    def add_item(self, name: str, price: float, quantity: int) -> None:
        """Add an item to the cart."""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        
        if name in self.items:
            self.items[name].quantity += quantity
        else:
            self.items[name] = Item(name, price, quantity)

    def remove_item(self, name: str) -> None:
        """Remove an item from the cart."""
        if name in self.items:
            del self.items[name]
        else:
            raise KeyError(f"Item '{name}' not found in cart.")

    def total_cost(self) -> float:
        """Calculate the total cost of all items in the cart."""
        return sum(item.total_price() for item in self.items.values())

    def clear_cart(self) -> None:
        """Remove all items from the cart."""
        self.items.clear()

    def apply_discount(self, code: str) -> float:
        """Apply a discount code and return the discounted total."""
        discount_codes: Dict[str, float] = {
            'SAVE10': 0.10,
            'SAVE20': 0.20,
        }
        
        if code in discount_codes:
            return self.total_cost() * (1 - discount_codes[code])
        else:
            raise ValueError("Invalid discount code.")

    def get_items(self) -> List[Item]:
        """Return a list of items in the cart."""
        return list(self.items.values())
```

### Unit Tests Implementation

```python
import unittest

class TestShoppingCart(unittest.TestCase):
    """Unit tests for ShoppingCart."""

    def setUp(self) -> None:
        self.cart = ShoppingCart()

    def test_add_item(self) -> None:
        self.cart.add_item("apple", 0.5, 3)
        self.assertEqual(self.cart.total_cost(), 1.5)
        
        # Test adding more of the same item
        self.cart.add_item("apple", 0.5, 2)
        self.assertEqual(self.cart.total_cost(), 2.5)

    def test_remove_item(self) -> None:
        self.cart.add_item("banana", 0.75, 2)
        self.cart.remove_item("banana")
        self.assertEqual(self.cart.total_cost(), 0.0)

    def test_clear_cart(self) -> None:
        self.cart.add_item("grapes", 2.0, 1)
        self.cart.clear_cart()
        self.assertEqual(self.cart.total_cost(), 0.0)

    def test_apply_discount(self) -> None:
        self.cart.add_item("orange", 1.0, 3)
        discounted_total = self.cart.apply_discount('SAVE10')
        self.assertEqual(discounted_total, 2.7)  # 3.0 - 10%

    def test_invalid_discount(self) -> None:
        self.cart.add_item("pear", 1.5, 1)
        with self.assertRaises(ValueError):
            self.cart.apply_discount('INVALIDCODE')

    def test_negative_quantity(self) -> None:
        with self.assertRaises(ValueError):
            self.cart.add_item("kiwi", 1.0, -1)

    def test_nonexistent_item_removal(self) -> None:
        with self.assertRaises(KeyError):
            self.cart.remove_item("pineapple")

if __name__ == "__main__":
    unittest.main()
```

### Explanation

1. **Item Class**: Models individual items stored in the cart with attributes such as `name`, `price`, and `quantity`. It includes a method to calculate total price for the item.

2. **ShoppingCart Class**: Manages a collection of `Item` objects. Provides methods to add and remove items, calculate total cost, apply discounts, and clear the cart.

3. **Unit Tests**: Uses the `unittest` framework to test various functionalities of the `ShoppingCart` class, including adding/removing items, calculating totals, and applying discounts, while also handling edge cases like invalid operations.

This implementation provides a solid foundation for a shopping cart system while adhering to clean coding practices.