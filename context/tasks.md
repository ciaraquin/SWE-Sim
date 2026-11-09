## Task
Implement a Python module `cart.py` with the following functionality:
- A `CartItem` class with `name`, `price`, and `quantity` attributes
- A `ShoppingCart` class with:
  - `add_item(item)` — adds a CartItem
  - `apply_discount(code)` — applies a percentage discount (use "SAVE10" for 10%, "SAVE20" for 20%)
  - `total()` — returns the total price after discount