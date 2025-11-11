# SwiftServe - Real-Time Hyperlocal Delivery Platform

A full-stack Python Flask application that provides a real-time hyperlocal delivery platform similar to Zomato/Swiggy, featuring three user roles: Customers, Restaurant Owners, and Delivery Agents.

## Features

### Core Functionality
- **User Authentication**: Registration and login for three roles (Customer, Restaurant Owner, Delivery Agent)
- **Restaurant Management**: CRUD operations for menu items and restaurant profiles
- **Order Management**: Complete order lifecycle from placement to delivery
- **Real-time Updates**: Live order status updates using SocketIO
- **Live Tracking**: Real-time delivery tracking with Leaflet.js maps
- **Shopping Cart**: Add/remove items with quantity management
- **Payment Integration**: Mock payment processing with success/failure simulation

### User Roles
1. **Customers**: Browse restaurants, add items to cart, place orders, track deliveries
2. **Restaurant Owners**: Manage menus, accept/reject orders, update order status
3. **Delivery Agents**: Accept delivery requests, update delivery status, track routes

## Technology Stack

- **Backend**: Python Flask, Flask-SocketIO, SQLAlchemy
- **Frontend**: Jinja2 templates, Bootstrap 5, Vanilla JavaScript
- **Database**: PostgreSQL with PostGIS (development: SQLite)
- **Maps**: Leaflet.js with OpenStreetMap
- **Real-time**: SocketIO for live updates
- **Styling**: Custom CSS with Bootstrap 5

## Project Structure

```
swiftserve/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── init_db.py               # Database initialization script
├── .env                     # Environment configuration
├── models/                  # SQLAlchemy models
│   ├── __init__.py
│   ├── user.py
│   ├── restaurant.py
│   ├── menu_item.py
│   ├── order.py
│   └── order_item.py
├── templates/               # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── customer_dashboard.html
│   ├── restaurant_dashboard.html
│   ├── restaurant_menu.html
│   ├── delivery_dashboard.html
│   ├── order_tracking.html
│   └── payment_success.html
├── static/                  # Static assets
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── realtime.js
│       └── maps.js
└── config/                  # Configuration files
    └── __init__.py
```

## Setup Instructions

### Prerequisites
- Python 3.7+
- PostgreSQL (optional, SQLite for development)
- Node.js (for development tools)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd swiftserve
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   - Copy `.env` file and update configuration
   - For development, SQLite is configured by default
   - For production, update PostgreSQL settings

5. **Initialize database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open browser to `http://localhost:5000`
   - Use demo accounts provided below

## Demo Accounts

### Customers
- **john@customer.com** / customer123
- **sarah@customer.com** / customer123

### Restaurant Owners
- **mike@restaurant.com** / restaurant123 (owns Burger Palace & Pizza Express)
- **lisa@restaurant.com** / restaurant123 (owns Spice Garden & Sushi Corner)

### Delivery Agents
- **david@delivery.com** / delivery123
- **emma@delivery.com** / delivery123

## Usage Guide

### For Customers
1. Register or login as a customer
2. Browse available restaurants on the dashboard
3. Click on a restaurant to view its menu
4. Add items to your cart
5. Proceed to checkout and place order
6. Track your order in real-time
7. View order history and status

### For Restaurant Owners
1. Register or login as a restaurant owner
2. Access the restaurant dashboard
3. Manage menu items (add, edit, delete, toggle availability)
4. View and manage incoming orders
5. Update order status (confirmed, preparing, ready, etc.)
6. Track order statistics and performance

### For Delivery Agents
1. Register or login as a delivery agent
2. Toggle availability status
3. Accept available delivery requests
4. Update delivery status during transit
5. View delivery history and earnings
6. Use live map for navigation

## API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - User authentication
- `GET /register` - Registration page
- `POST /register` - User registration
- `GET /logout` - User logout

### Customer Operations
- `GET /customer/dashboard` - Customer dashboard
- `GET /restaurant/<id>` - View restaurant menu
- `POST /api/cart/add` - Add item to cart
- `POST /api/cart/remove` - Remove item from cart
- `POST /api/order/place` - Place order
- `GET /order/<id>/track` - Track order

### Restaurant Operations
- `GET /restaurant/dashboard` - Restaurant dashboard
- `POST /api/menu/add` - Add menu item
- `POST /api/menu/update/<id>` - Update menu item
- `POST /api/menu/delete/<id>` - Delete menu item
- `POST /api/order/status/<id>` - Update order status

### Delivery Operations
- `GET /delivery/dashboard` - Delivery dashboard
- `POST /api/delivery/accept/<id>` - Accept delivery
- `POST /api/delivery/status/<id>` - Update delivery status
- `POST /api/delivery/complete/<id>` - Complete delivery

### Real-time SocketIO Events
- `join_room` - Join user-specific room
- `order_update` - Order status updates
- `location_update` - Delivery agent location updates
- `new_order` - New order notifications

## Configuration

### Environment Variables
- `FLASK_ENV` - Flask environment (development/production)
- `SECRET_KEY` - Flask secret key for sessions
- `DATABASE_URL` - PostgreSQL connection string
- `SQLALCHEMY_DATABASE_URI` - Database URI (SQLite for development)
- `CORS_ALLOWED_ORIGINS` - CORS origins for SocketIO

### Map Settings
- `MAP_DEFAULT_LAT` - Default map latitude
- `MAP_DEFAULT_LNG` - Default map longitude
- `MAP_DEFAULT_ZOOM` - Default map zoom level
- `MAX_DELIVERY_RADIUS_KM` - Maximum delivery radius
- `DELIVERY_AGENT_RADIUS_KM` - Agent notification radius

## Development

### Database Schema
The application uses SQLAlchemy ORM with the following models:

- **User**: Authentication and profile information
- **Restaurant**: Restaurant details and location
- **MenuItem**: Food items with pricing
- **Order**: Order tracking and status
- **OrderItem**: Individual items within orders

### Real-time Features
SocketIO integration provides:
- Live order status updates
- Real-time delivery tracking
- Instant notifications for all user roles
- Location sharing for delivery agents

### Map Integration
Leaflet.js provides:
- Interactive maps with custom markers
- Real-time location tracking
- Route visualization
- Distance calculations

## Deployment

### Production Considerations
1. Use PostgreSQL with PostGIS for location data
2. Configure Redis for SocketIO scaling
3. Set up proper environment variables
4. Enable HTTPS for secure connections
5. Configure rate limiting and security headers
6. Set up monitoring and logging

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## Troubleshooting

### Common Issues
1. **Database Connection**: Ensure PostgreSQL is running and credentials are correct
2. **SocketIO Connection**: Check CORS settings and firewall configuration
3. **Map Loading**: Verify internet connection for OpenStreetMap tiles
4. **Location Services**: Ensure browser permissions for geolocation

### Debug Mode
Enable debug mode in `.env` file:
```
FLASK_DEBUG=True
FLASK_ENV=development
```

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section
- Review the GitHub issues
- Contact the development team