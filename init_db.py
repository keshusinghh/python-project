import os
import sys
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.user import User
from models.restaurant import Restaurant
from models.menu_item import MenuItem
from models.order import Order
from models.order_item import OrderItem

def create_sample_data():
    """Create sample data for demonstration"""
    
    # Create users
    users = [
        {
            'name': 'John Doe',
            'email': 'john@customer.com',
            'password': 'customer123',
            'role': 'customer',
            'latitude': 12.9716,
            'longitude': 77.5946
        },
        {
            'name': 'Sarah Wilson',
            'email': 'sarah@customer.com',
            'password': 'customer123',
            'role': 'customer',
            'latitude': 12.9352,
            'longitude': 77.6245
        },
        {
            'name': 'Mike Chen',
            'email': 'mike@restaurant.com',
            'password': 'restaurant123',
            'role': 'restaurant',
            'latitude': 12.9539,
            'longitude': 77.6309
        },
        {
            'name': 'Lisa Patel',
            'email': 'lisa@restaurant.com',
            'password': 'restaurant123',
            'role': 'restaurant',
            'latitude': 12.9784,
            'longitude': 77.6404
        },
        {
            'name': 'David Kumar',
            'email': 'david@delivery.com',
            'password': 'delivery123',
            'role': 'delivery',
            'latitude': 12.9600,
            'longitude': 77.6100
        },
        {
            'name': 'Emma Rodriguez',
            'email': 'emma@delivery.com',
            'password': 'delivery123',
            'role': 'delivery',
            'latitude': 12.9800,
            'longitude': 77.6500
        }
    ]
    
    created_users = []
    for user_data in users:
        user = User(
            name=user_data['name'],
            email=user_data['email'],
            password=generate_password_hash(user_data['password']),
            role=user_data['role'],
            latitude=user_data['latitude'],
            longitude=user_data['longitude']
        )
        db.session.add(user)
        created_users.append(user)
    
    db.session.commit()
    print(f"Created {len(created_users)} users")
    
    # Create restaurants (owned by restaurant users)
    restaurants = [
        {
            'owner_id': created_users[2].id,  # Mike Chen
            'name': 'Burger Palace',
            'address': '123 MG Road, Bangalore',
            'cuisine_type': 'American',
            'latitude': 12.9539,
            'longitude': 77.6309
        },
        {
            'owner_id': created_users[2].id,  # Mike Chen
            'name': 'Pizza Express',
            'address': '456 Brigade Road, Bangalore',
            'cuisine_type': 'Italian',
            'latitude': 12.9639,
            'longitude': 77.6209
        },
        {
            'owner_id': created_users[3].id,  # Lisa Patel
            'name': 'Spice Garden',
            'address': '789 Koramangala, Bangalore',
            'cuisine_type': 'Indian',
            'latitude': 12.9784,
            'longitude': 77.6404
        },
        {
            'owner_id': created_users[3].id,  # Lisa Patel
            'name': 'Sushi Corner',
            'address': '321 Indiranagar, Bangalore',
            'cuisine_type': 'Japanese',
            'latitude': 12.9684,
            'longitude': 77.6504
        }
    ]
    
    created_restaurants = []
    for restaurant_data in restaurants:
        restaurant = Restaurant(**restaurant_data)
        db.session.add(restaurant)
        created_restaurants.append(restaurant)
    
    db.session.commit()
    print(f"Created {len(created_restaurants)} restaurants")
    
    # Create menu items
    menu_items_data = [
        # Burger Palace
        {'restaurant_id': created_restaurants[0].id, 'name': 'Classic Burger', 'price': 150, 'description': 'Juicy beef patty with lettuce, tomato, and special sauce', 'is_available': True},
        {'restaurant_id': created_restaurants[0].id, 'name': 'Cheese Burger', 'price': 170, 'description': 'Classic burger with melted cheese', 'is_available': True},
        {'restaurant_id': created_restaurants[0].id, 'name': 'Chicken Burger', 'price': 160, 'description': 'Grilled chicken patty with mayo and veggies', 'is_available': True},
        {'restaurant_id': created_restaurants[0].id, 'name': 'French Fries', 'price': 80, 'description': 'Crispy golden fries', 'is_available': True},
        {'restaurant_id': created_restaurants[0].id, 'name': 'Coca Cola', 'price': 40, 'description': 'Chilled soft drink', 'is_available': True},
        
        # Pizza Express
        {'restaurant_id': created_restaurants[1].id, 'name': 'Margherita Pizza', 'price': 250, 'description': 'Classic pizza with tomato sauce and mozzarella', 'is_available': True},
        {'restaurant_id': created_restaurants[1].id, 'name': 'Pepperoni Pizza', 'price': 300, 'description': 'Pizza with pepperoni and cheese', 'is_available': True},
        {'restaurant_id': created_restaurants[1].id, 'name': 'Veggie Pizza', 'price': 280, 'description': 'Pizza with assorted vegetables', 'is_available': True},
        {'restaurant_id': created_restaurants[1].id, 'name': 'Garlic Bread', 'price': 90, 'description': 'Toasted bread with garlic butter', 'is_available': True},
        {'restaurant_id': created_restaurants[1].id, 'name': 'Pasta Alfredo', 'price': 220, 'description': 'Creamy pasta with parmesan cheese', 'is_available': True},
        
        # Spice Garden
        {'restaurant_id': created_restaurants[2].id, 'name': 'Butter Chicken', 'price': 280, 'description': 'Creamy chicken curry with butter', 'is_available': True},
        {'restaurant_id': created_restaurants[2].id, 'name': 'Palak Paneer', 'price': 200, 'description': 'Spinach curry with cottage cheese', 'is_available': True},
        {'restaurant_id': created_restaurants[2].id, 'name': 'Chicken Biryani', 'price': 320, 'description': 'Fragrant rice with chicken and spices', 'is_available': True},
        {'restaurant_id': created_restaurants[2].id, 'name': 'Naan Bread', 'price': 40, 'description': 'Soft Indian flatbread', 'is_available': True},
        {'restaurant_id': created_restaurants[2].id, 'name': 'Lassi', 'price': 60, 'description': 'Yogurt-based drink', 'is_available': True},
        
        # Sushi Corner
        {'restaurant_id': created_restaurants[3].id, 'name': 'California Roll', 'price': 180, 'description': 'Sushi roll with crab, avocado, and cucumber', 'is_available': True},
        {'restaurant_id': created_restaurants[3].id, 'name': 'Salmon Sashimi', 'price': 350, 'description': 'Fresh salmon slices', 'is_available': True},
        {'restaurant_id': created_restaurants[3].id, 'name': 'Tuna Roll', 'price': 200, 'description': 'Sushi roll with tuna', 'is_available': True},
        {'restaurant_id': created_restaurants[3].id, 'name': 'Miso Soup', 'price': 80, 'description': 'Traditional Japanese soup', 'is_available': True},
        {'restaurant_id': created_restaurants[3].id, 'name': 'Green Tea', 'price': 50, 'description': 'Traditional Japanese tea', 'is_available': True},
    ]
    
    created_menu_items = []
    for item_data in menu_items_data:
        menu_item = MenuItem(**item_data)
        db.session.add(menu_item)
        created_menu_items.append(menu_item)
    
    db.session.commit()
    print(f"Created {len(created_menu_items)} menu items")
    
    # Create some sample orders
    order_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'picked_up', 'delivered']
    
    sample_orders = [
        {
            'customer_id': created_users[0].id,  # John Doe
            'restaurant_id': created_restaurants[0].id,  # Burger Palace
            'agent_id': created_users[4].id,  # David Kumar
            'status': 'delivered',
            'total_amount': 370,
            'delivery_address': '123 MG Road, Bangalore',
            'special_instructions': 'Please ring the doorbell'
        },
        {
            'customer_id': created_users[1].id,  # Sarah Wilson
            'restaurant_id': created_restaurants[1].id,  # Pizza Express
            'agent_id': created_users[5].id,  # Emma Rodriguez
            'status': 'delivered',
            'total_amount': 590,
            'delivery_address': '456 Brigade Road, Bangalore',
            'special_instructions': 'Leave at the reception'
        },
        {
            'customer_id': created_users[0].id,  # John Doe
            'restaurant_id': created_restaurants[2].id,  # Spice Garden
            'agent_id': created_users[4].id,  # David Kumar
            'status': 'preparing',
            'total_amount': 660,
            'delivery_address': '123 MG Road, Bangalore',
            'special_instructions': 'Extra spicy please'
        }
    ]
    
    created_orders = []
    for order_data in sample_orders:
        order = Order(**order_data)
        db.session.add(order)
        created_orders.append(order)
    
    db.session.commit()
    print(f"Created {len(created_orders)} orders")
    
    # Create order items
    order_items_data = [
        # First order (delivered)
        {'order_id': created_orders[0].id, 'menu_item_id': created_menu_items[0].id, 'quantity': 2, 'price_at_order': 150, 'special_instructions': ''},
        {'order_id': created_orders[0].id, 'menu_item_id': created_menu_items[3].id, 'quantity': 1, 'price_at_order': 80, 'special_instructions': ''},
        {'order_id': created_orders[0].id, 'menu_item_id': created_menu_items[4].id, 'quantity': 2, 'price_at_order': 40, 'special_instructions': ''},
        
        # Second order (delivered)
        {'order_id': created_orders[1].id, 'menu_item_id': created_menu_items[5].id, 'quantity': 1, 'price_at_order': 250, 'special_instructions': ''},
        {'order_id': created_orders[1].id, 'menu_item_id': created_menu_items[6].id, 'quantity': 1, 'price_at_order': 300, 'special_instructions': ''},
        {'order_id': created_orders[1].id, 'menu_item_id': created_menu_items[7].id, 'quantity': 1, 'price_at_order': 280, 'special_instructions': ''},
        
        # Third order (preparing)
        {'order_id': created_orders[2].id, 'menu_item_id': created_menu_items[10].id, 'quantity': 1, 'price_at_order': 280, 'special_instructions': 'Extra spicy'},
        {'order_id': created_orders[2].id, 'menu_item_id': created_menu_items[11].id, 'quantity': 1, 'price_at_order': 200, 'special_instructions': ''},
        {'order_id': created_orders[2].id, 'menu_item_id': created_menu_items[12].id, 'quantity': 1, 'price_at_order': 320, 'special_instructions': ''},
    ]
    
    created_order_items = []
    for item_data in order_items_data:
        order_item = OrderItem(**item_data)
        db.session.add(order_item)
        created_order_items.append(order_item)
    
    db.session.commit()
    print(f"Created {len(created_order_items)} order items")
    
    print("\nSample data created successfully!")
    print("\nDemo Accounts:")
    print("Customer: john@customer.com / customer123")
    print("Customer: sarah@customer.com / customer123")
    print("Restaurant: mike@restaurant.com / restaurant123")
    print("Restaurant: lisa@restaurant.com / restaurant123")
    print("Delivery: david@delivery.com / delivery123")
    print("Delivery: emma@delivery.com / delivery123")

def main():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        print("\nCreating sample data...")
        create_sample_data()
        print("\nDatabase initialization completed!")

if __name__ == '__main__':
    main()