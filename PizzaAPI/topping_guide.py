"""Pizza topping code guide."""

# Format: code: (name, category, tags)
TOPPINGS = {
    # Pizza Toppings
    'X': ('Robust Inspired Tomato Sauce', 'Sauce', ['NonMeat']),
    'Bq': ('Honey BBQ Sauce', 'Sauce', ['NonMeat']),
    'Xw': ('Garlic Parmesan Sauce', 'Sauce', ['NonMeat']),
    'C': ('Cheese', 'Cheese', ['NonMeat']),
    'E': ('Cheddar Cheese Blend', 'Cheese', ['NonMeat']),
    'Fe': ('Feta Cheese', 'Cheese', ['NonMeat']),
    'Cs': ('Shredded Parmesan Asiago', 'Cheese', ['NonMeat']),
    'Ac': ('American Cheese', 'Cheese', ['NonMeat']),
    'Cp': ('Shredded Provolone', 'Cheese', ['NonMeat']),
    
    # Meats
    'H': ('Ham', 'Meat', ['Meat']),
    'B': ('Beef', 'Meat', ['Meat']),
    'P': ('Pepperoni', 'Meat', ['Meat']),
    'S': ('Italian Sausage', 'Meat', ['Meat']),
    'Du': ('Premium Chicken', 'Meat', ['Meat']),
    'K': ('Bacon', 'Meat', ['Meat']),
    'Pm': ('Philly Steak', 'Meat', ['Meat']),
    
    # Vegetables
    'F': ('Garlic', 'Vegetable', ['NonMeat']),
    'J': ('Jalapeno Peppers', 'Vegetable', ['NonMeat']),
    'O': ('Onions', 'Vegetable', ['NonMeat']),
    'Z': ('Banana Peppers', 'Vegetable', ['NonMeat']),
    'Td': ('Diced Tomatoes', 'Vegetable', ['NonMeat']),
    'R': ('Black Olives', 'Vegetable', ['NonMeat']),
    'M': ('Mushrooms', 'Vegetable', ['NonMeat']),
    'N': ('Pineapple', 'Vegetable', ['NonMeat']),
    'G': ('Green Peppers', 'Vegetable', ['NonMeat']),
    'Si': ('Spinach', 'Vegetable', ['NonMeat']),
    
    # Special
    'Rd': ('Ranch', 'Sauce', ['NonMeat']),
    'GOB': ('Garlic Crust Seasoning', 'Seasoning', []),
    'PARM': ('Parmesan Crust Seasoning', 'Seasoning', [])
}

# Size codes
SIZES = {
    '10': 'Small (10")',
    '12': 'Medium (12")',
    '14': 'Large (14")'
} 