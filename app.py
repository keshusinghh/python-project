from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import join_room, leave_room, emit
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
from extensions import db, socketio, login_manager

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'swiftserve-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///swiftserve.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
socketio.init_app(app, cors_allowed_origins="*")
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models
from models.user import User
from models.restaurant import Restaurant
from models.menu_item import MenuItem
from models.order import Order
from models.order_item import OrderItem

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            print(f'Stored password hash for {email}: {user.password}')  # Debugging line
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'customer':
                return redirect(url_for('customer_dashboard'))
            elif user.role == 'restaurant':
                return redirect(url_for('restaurant_dashboard'))
            elif user.role == 'delivery_agent':
                return redirect(url_for('delivery_dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        print(f'Hashed password for {email}: {password}')  # Debugging line
        role = request.form['role']
        latitude = float(request.form.get('latitude', 0))
        longitude = float(request.form.get('longitude', 0))
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        new_user = User(
            name=name,
            email=email,
            password=password,
            role=role,
            latitude=latitude,
            longitude=longitude
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            # If restaurant, create restaurant profile
            if role == 'restaurant':
                restaurant = Restaurant(
                    owner_id=new_user.id,
                    name=f"{name}'s Restaurant",
                    address='',
                    cuisine_type='',
                    latitude=latitude,
                    longitude=longitude
                )
                db.session.add(restaurant)
                db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Customer routes
@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        return redirect(url_for('index'))
    
    restaurants = Restaurant.query.all()
    return render_template('customer_dashboard.html', restaurants=restaurants)

@app.route('/customer/restaurant/<int:restaurant_id>')
@login_required
def restaurant_menu(restaurant_id):
    if current_user.role != 'customer':
        return redirect(url_for('index'))
    
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    return render_template('restaurant_menu.html', restaurant=restaurant, menu_items=menu_items)

# Restaurant routes
@app.route('/restaurant/dashboard')
@login_required
def restaurant_dashboard():
    if current_user.role != 'restaurant':
        return redirect(url_for('index'))
    
    restaurant = Restaurant.query.filter_by(owner_id=current_user.id).first()
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant.id).all() if restaurant else []
    orders = Order.query.filter_by(restaurant_id=restaurant.id).all() if restaurant else []
    
    return render_template('restaurant_dashboard.html', 
                         restaurant=restaurant, 
                         menu_items=menu_items, 
                         orders=orders)

# Restaurant profile edit
@app.route('/restaurant/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_restaurant_profile():
    if current_user.role != 'restaurant':
        return redirect(url_for('index'))

    restaurant = Restaurant.query.filter_by(owner_id=current_user.id).first()
    if not restaurant:
        flash('Restaurant profile not found.', 'error')
        return redirect(url_for('restaurant_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', restaurant.name)
        address = request.form.get('address', restaurant.address)
        cuisine_type = request.form.get('cuisine_type', restaurant.cuisine_type)

        restaurant.name = name
        restaurant.address = address
        restaurant.cuisine_type = cuisine_type
        try:
            db.session.commit()
            flash('Restaurant profile updated successfully.', 'success')
            return redirect(url_for('restaurant_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update restaurant profile.', 'error')

    return render_template('restaurant_edit_profile.html', restaurant=restaurant)

# Delivery Agent routes
@app.route('/delivery/dashboard')
@login_required
def delivery_dashboard():
    if current_user.role != 'delivery_agent':
        return redirect(url_for('index'))
    
    available_orders = Order.query.filter_by(status='ready_for_pickup').all()
    my_orders = Order.query.filter_by(agent_id=current_user.id).all()
    
    return render_template('delivery_dashboard.html', 
                         agent=current_user,
                         available_orders=available_orders, 
                         my_orders=my_orders)

# Order tracking
@app.route('/track/<int:order_id>')
def track_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_tracking.html', order=order)

# API Routes
@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    if current_user.role != 'customer':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)
    
    # Store in session cart
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    if str(item_id) in cart:
        cart[str(item_id)] += quantity
    else:
        cart[str(item_id)] = quantity
    
    session['cart'] = cart
    return jsonify({'success': True, 'cart_count': sum(cart.values())})

@app.route('/api/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    if current_user.role != 'customer':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    item_id = str(data.get('item_id'))
    
    if 'cart' in session and item_id in session['cart']:
        del session['cart'][item_id]
        session.modified = True
    
    return jsonify({'success': True})

@app.route('/api/order/place', methods=['POST'])
@login_required
def place_order():
    if current_user.role != 'customer':
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'cart' not in session or not session['cart']:
        return jsonify({'error': 'Cart is empty'}), 400
    
    data = request.get_json()
    restaurant_id = data.get('restaurant_id')
    
    try:
        # Create order
        order = Order(
            customer_id=current_user.id,
            restaurant_id=restaurant_id,
            status='pending',
            timestamp=datetime.utcnow()
        )
        db.session.add(order)
        db.session.flush()
        
        # Add order items
        for item_id, quantity in session['cart'].items():
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=int(item_id),
                quantity=quantity
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # Clear cart
        session['cart'] = {}
        
        # Emit real-time update to restaurant
        socketio.emit('new_order', {
            'order_id': order.id,
            'customer_name': current_user.name,
            'items': len(session['cart'])
        }, room=f'restaurant_{restaurant_id}')
        
        return jsonify({'success': True, 'order_id': order.id})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Order placement failed'}), 500

@app.route('/api/order/update_status', methods=['POST'])
@login_required
def update_order_status():
    data = request.get_json()
    order_id = data.get('order_id')
    new_status = data.get('status')
    
    order = Order.query.get_or_404(order_id)
    
    # Check permissions
    if current_user.role == 'restaurant' and order.restaurant.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    elif current_user.role == 'delivery_agent' and order.agent_id != current_user.id and order.agent_id is None:
        # Allow delivery agent to accept order
        if new_status == 'picked_up':
            order.agent_id = current_user.id
        else:
            return jsonify({'error': 'Unauthorized'}), 403
    elif current_user.role == 'delivery_agent' and order.agent_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    order.status = new_status
    db.session.commit()
    
    # Emit real-time update
    socketio.emit('order_status_update', {
        'order_id': order.id,
        'status': new_status,
        'timestamp': datetime.utcnow().isoformat()
    }, room=f'order_{order.id}')
    
    return jsonify({'success': True})

# Restaurant API: toggle open/closed status
@app.route('/api/restaurant/toggle_status', methods=['POST'])
@login_required
def toggle_restaurant_status():
    if current_user.role != 'restaurant':
        return jsonify({'error': 'Unauthorized'}), 403

    restaurant = Restaurant.query.filter_by(owner_id=current_user.id).first()
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404

    data = request.get_json(silent=True) or {}
    action = data.get('action')  # 'open' or 'closed'
    try:
        if action == 'open':
            restaurant.is_active = True
        elif action == 'closed':
            restaurant.is_active = False
        else:
            restaurant.is_active = not restaurant.is_active

        db.session.commit()
        return jsonify({'success': True, 'is_active': restaurant.is_active})
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Failed to update status'}), 500

# Delivery agent API: toggle available/unavailable status
@app.route('/api/delivery/agent/toggle_status', methods=['POST'])
@login_required
def toggle_delivery_agent_status():
    if current_user.role != 'delivery_agent':
        return jsonify({'error': 'Unauthorized'}), 403

    agent = User.query.get_or_404(current_user.id)
    data = request.get_json(silent=True) or {}
    is_available = data.get('is_available')

    try:
        if is_available is not None:
            agent.is_available = is_available
        else:
            agent.is_available = not agent.is_available
        
        db.session.commit()
        return jsonify({'success': True, 'is_available': agent.is_available})
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Failed to update status'}), 500


# Restaurant routes: add menu item
@app.route('/restaurant/menu/add', methods=['GET', 'POST'])
@login_required
def add_menu_item():
    if current_user.role != 'restaurant':
        return redirect(url_for('index'))

    restaurant = Restaurant.query.filter_by(owner_id=current_user.id).first()
    if not restaurant:
        flash('Restaurant profile not found.', 'error')
        return redirect(url_for('restaurant_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        price_raw = request.form.get('price')
        description = request.form.get('description')
        is_available = bool(request.form.get('is_available'))

        try:
            price = float(price_raw)
        except (TypeError, ValueError):
            flash('Invalid price value.', 'error')
            return render_template('restaurant_add_menu_item.html', restaurant=restaurant)

        if not name:
            flash('Name is required.', 'error')
            return render_template('restaurant_add_menu_item.html', restaurant=restaurant)

        try:
            item = MenuItem(
                restaurant_id=restaurant.id,
                name=name,
                price=price,
                description=description,
                is_available=is_available
            )
            db.session.add(item)
            db.session.commit()
            flash('Menu item added successfully.', 'success')
            return redirect(url_for('restaurant_dashboard'))
        except Exception:
            db.session.rollback()
            flash('Failed to add menu item.', 'error')

    return render_template('restaurant_add_menu_item.html', restaurant=restaurant)

# SocketIO events
@socketio.on('join_order_room')
def handle_join_order_room(data):
    order_id = data.get('order_id')
    join_room(f'order_{order_id}')

@socketio.on('join_restaurant_room')
def handle_join_restaurant_room(data):
    restaurant_id = data.get('restaurant_id')
    join_room(f'restaurant_{restaurant_id}')

@socketio.on('location_update')
def handle_location_update(data):
    order_id = data.get('order_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    # Emit to order tracking room
    emit('delivery_location_update', {
        'order_id': order_id,
        'latitude': latitude,
        'longitude': longitude,
        'timestamp': datetime.utcnow().isoformat()
    }, room=f'order_{order_id}')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)