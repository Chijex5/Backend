import os
from flask import Flask, request, jsonify
from flask_mail import Mail
from datetime import datetime
from flask_mysqldb import MySQL
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Mail Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
mail = Mail(app)

# MySQL Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT'))
mysql = MySQL(app)

# Secret Key
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
count = 0
@app.route('/', methods=['GET'])
def home():
    count += 1
    return jsonify({'message': 'Welcome to the Uniboks Backend API! Our Backend is up and runing', count}), 200


def log_event(user_id, event, metadata=None):
    cursor = mysql.connection.cursor()
    query = "INSERT INTO analytics (user_id, event, metadata) VALUES (%s, %s, %s)"
    cursor.execute(query, (user_id, event, metadata))
    mysql.connection.commit()
    cursor.close()
    
@app.route('/purchase', methods=['POST'])
def handle_purchase():
    data = request.get_json()

    # Check if data is a list (multiple purchases)
    if isinstance(data, list):
        for item in data:
            user_id = item.get('userId')
            book_id = item.get('bookId')
            price = item.get('price')
            payment_method = item.get('paymentMethod')
            date_purchased = datetime.now()

            try:
                cursor = mysql.connection.cursor()
                cursor.execute(
                    "INSERT INTO purchases (userId, bookId, price, paymentMethod, datePurchased) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, book_id, price, payment_method, date_purchased)
                )
                mysql.connection.commit()
                cursor.close()
            except Exception as e:
                print(f"Error inserting purchase data: {e}")
                return jsonify({'error': 'Failed to store purchase data'}), 500

        return jsonify({"message": "All purchases recorded successfully!"}), 200
    else:
        # Handle a single purchase
        user_id = data.get('userId')
        book_id = data.get('bookId')
        price = data.get('price')
        payment_method = data.get('paymentMethod')
        date_purchased = datetime.now()

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO purchases (userId, bookId, price, paymentMethod, datePurchased) VALUES (%s, %s, %s, %s, %s)",
                (user_id, book_id, price, payment_method, date_purchased)
            )
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Purchase recorded successfully!"}), 200
        except Exception as e:
            print(f"Error inserting purchase data: {e}")
            return jsonify({'error': 'Failed to store purchase data'}), 500


@app.route('/user/purchases', methods=['GET'])
def get_purchase_summary():
    user_id = request.args.get('userId')  # Get the userId from query params

    # SQL Query to sum the prices and count the number of books for the given user
    query = """
        SELECT SUM(price) as totalSum, COUNT(bookId) as totalBooks
        FROM purchases 
        WHERE userId = %s
    """
    cursor = mysql.connection.cursor()
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()

    # If no purchases are found, return 0 for both fields
    total_sum = result[0] if result[0] is not None else 0
    total_books = result[1] if result[1] is not None else 0

    # Return the result as JSON
    return jsonify({
        'totalSum': float(total_sum),
        'totalBooks': total_books
    })

"""
CREATE TABLE purchases (
    purchaseId INT AUTO_INCREMENT PRIMARY KEY,   -- Unique ID for each purchase
    userId VARCHAR(255) COLLATE utf8mb3_general_ci NOT NULL,  -- Matches userId column in users table
    bookId INT NOT NULL,                         -- Matches the type of id in books table
    price DECIMAL(10, 2) NOT NULL,               -- The price of the book
    paymentMethod VARCHAR(50) NOT NULL,          -- Payment method (e.g., Credit Card, PayPal, etc.)
    datePurchased DATETIME DEFAULT CURRENT_TIMESTAMP, -- Date and time of purchase
    FOREIGN KEY (userId) REFERENCES users(userId),   -- Foreign key to users table
    FOREIGN KEY (bookId) REFERENCES books(id)        -- Foreign key to books table
);
"""
    


@app.route('/complete-profile', methods=['POST'])
def complete_profile():
    data = request.json

    # Extract user data from the request
    user_id = data.get('user_id')
    email = data.get('email')
    username = data.get('username', "")
    profile_url = data.get('profileUrl', "")
    level = data.get('level', "")
    flat_no = data.get('flatNo', "")
    street = data.get('street', "")
    city = data.get('city', "")
    state = data.get('state', "")
    postal_code = data.get('postalCode', "")
    phone = data.get('phone', "")
    department = data.get('department', "")

    # Connect to the database
    
    try:
        cursor = mysql.connection.cursor()

        # Insert the user data into the users table
        insert_query = """
        INSERT INTO users (userid, email, username, profileUrl, level, flatNo, street, city, state, postalCode, phone, department)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (user_id, email, username, profile_url, level, flat_no, street, city, state, postal_code, phone, department))
        mysql.connection.commit()
        log_event(user_id, 'CompleteProfile', 'User completed profile')

        # Respond with success
        return jsonify({'message': 'Profile completed successfully'}), 201

    except Exception as e:
        print(f"Error inserting user data: {e}")
        return jsonify({'error': 'Failed to complete profile'}), 500
    
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        email = data.get('email')
        username = data.get('username', "")
        profile_url = data.get('profileUrl', "")

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username, level, profileUrl, address, phone, department,flatno, street, city, state, postalcode FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            response = {
                'name': user[0],
                'level': user[1] or "",
                'profileUrl': profile_url or user[2] or "",
                'address': user[3] or "",
                'phone': user[4] or "",
                'department': user[5] or "",
                'flat_no': user[6] or "",
                'street': user[7] or "",
                'city': user[8] or "",
                'state': user[9] or "",
                'postal_code': user[10] or "",
                'email': email,
                'userId': user_id
            }
            cursor.close()
            log_event(user_id, 'login', 'User logged in successfully')
            return jsonify(response), 200
        else:
            # User not found, create a new user
            cursor.execute(
                "INSERT INTO users (userId, email, username, level, profileUrl, address, phone, department) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (user_id, email, username, "", profile_url, "", "", "")
            )
            mysql.connection.commit()

            response = {
                'name': username,
                'level': "",
                'profileUrl': profile_url,
                'address': "",
                'phone': "",
                'department': "",
                'email': email
            }
            cursor.close()
            log_event(user_id, 'login', 'New User created successfully')
            return jsonify(response), 201  # 201 Created

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/check-user', methods=['POST'])
def check_user():
    try:
        data = request.get_json()
        user_id = data.get('userId')
        email = data.get('email')

        # Ensure that at least one identifier is provided
        if not user_id and not email:
            return jsonify({'error': 'User ID or Email is required'}), 400

        cursor = mysql.connection.cursor()

        # Check if a user exists by userId or email
        if user_id:
            cursor.execute("SELECT * FROM users WHERE userId = %s", (user_id,))
        elif email:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        
        user = cursor.fetchone()
        cursor.close()

        if user:
            # User exists
            return jsonify({'exists': True, 'message': 'User found.'}), 200
        else:
            # User does not exist
            return jsonify({'exists': False, 'message': 'User not found.'}), 404

    except Exception as e:
        log_event(user_id, 'error', str(e))
        return jsonify({'error': str(e)}), 500



@app.route('/updateuser', methods=['PUT'])
def update_user():
    try:
        data = request.get_json()
        user_id = data.get('userId')


        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        # Extract other fields to be updated
        username = data.get('username', '')
        profile_url = data.get('profileUrl', '')
        level = data.get('level', '')
        postal_code = data.get('postal_code', '')
        phone = data.get('phone', '')
        department = data.get('department', '')
        flat_no = data.get('flat_no', '')
        city = data.get('city', '')
        street = data.get('street', '')
        state = data.get('state', '')

        cursor = mysql.connection.cursor()

        # Update user information in the database
        cursor.execute("""
            UPDATE users
            SET username = %s, profileUrl = %s, level = %s, postalcode = %s, state = %s, street = %s, flatno = %s, city = %s, phone = %s, department = %s
            WHERE userId = %s
        """, (username, profile_url, level, postal_code, state, street, flat_no, city, phone, department, user_id))

        mysql.connection.commit()
        cursor.close()
        log_event(user_id, 'Update', 'User Updated Profile')

        return jsonify({'message': 'User data updated successfully'}), 200

    except Exception as e:
        print(e)
        log_event(user_id, 'error', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/getbooks', methods=['GET'])
def get_books():
    try:
        user_id = request.args.get('userId')
        cursor = mysql.connection.cursor()
        print(f"User ID: {user_id}")

        # Fetch the department associated with the user
        cursor.execute("SELECT department FROM users WHERE userId = %s", (user_id,))
        department = cursor.fetchone()
        print(f"Department: {department}")

        if department:
            department_name = department[0]

            # Fetch books from the user's department
            cursor.execute("SELECT * FROM books WHERE department = %s", (department_name,))
            department_books = cursor.fetchall() 
        else:
            department_books = []
        # Fetch the most recent books
        cursor.execute("SELECT * FROM books ORDER BY id DESC LIMIT 10")
        recent_choices = cursor.fetchall()
        response = {
            'allBooks': department_books,
            'recentChoices': recent_choices
        }
        return jsonify(response), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/findbooks', methods=['GET'])
def find_books():
    try:
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM books")
        allbooks = cursor.fetchall()

        # Query for recent choices
        cursor.execute("SELECT * FROM books ORDER BY id DESC LIMIT 10")
        recent_choices = cursor.fetchall()

        # Query for new arrivals
        cursor.execute("SELECT * FROM books ORDER BY id DESC LIMIT 3")
        new_arrivals = cursor.fetchall()

        # Query for top-rated books (assuming a rating column exists)
        cursor.execute("SELECT * FROM books ORDER BY rating DESC LIMIT 10")
        top_rated_books = cursor.fetchall()

        # Query for books on sale (assuming a discount or price filter)
        cursor.execute("SELECT * FROM books WHERE price < 2000")
        on_sale_books = cursor.fetchall()

        # Query for engineering books
        cursor.execute("SELECT * FROM books WHERE department = 'art'")
        arts_books = cursor.fetchall()

        cursor.execute("SELECT * FROM books WHERE department = 'Engineering'")
        engineering_books = cursor.fetchall()

        cursor.execute("SELECT * FROM books WHERE department = 'it'")
        it_books = cursor.fetchall()

        cursor.execute("SELECT * FROM books WHERE department = 'geology'")
        featured_books = cursor.fetchall()

        # Query for science books
        cursor.execute("SELECT * FROM books WHERE department IN ('Physics and Astronomy', 'Pure and Industrial Chemistry', 'Micro Biology')")
        science_books = cursor.fetchall()

        # Query for arts bo@FROM books ORDER BY views DESC LIMIT 3")
        most_viewed_books = cursor.fetchall()

        #  for popular books (e.g., based on views or sales)
        cursor.execute("SELECT * FROM books ORDER BY views DESC LIMIT 3")
        popular_books = cursor.fetchall()

        cursor.close()

        # Construct the response
        response = {
            'allBooks': allbooks,
            'recentChoices': recent_choices,
            'newArrivals': new_arrivals,
            'topRatedBooks': top_rated_books,
            'onSaleBooks': on_sale_books,
            'engineeringBooks': engineering_books,
            'scienceBooks': science_books,
            'artsBooks': arts_books,
            'itBooks': it_books,
            'featuredBooks': featured_books,
            'mostViewedBooks': most_viewed_books,
            'popularBooks': popular_books
        }

        return jsonify(response), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/addToWishlist', methods=['POST'])
def addToWishlist():
    data = request.get_json()
    user_id = data.get('userId')
    book_id = data.get('bookId')
    print(f"add to wishlist invoked for {user_id}, {book_id}")
    try:
    
        if user_id and book_id:
            cursor = mysql.connection.cursor()
            
            # Check if the book is already in the wishlist
            cursor.execute("SELECT * FROM wishlists WHERE userId = %s AND bookId = %s", (user_id, book_id))
            existing_item = cursor.fetchone()
            
            if existing_item:
                return jsonify({'message': 'Book already Exist'}), 409
            else:
                # Insert the new book into the wishlist
                cursor.execute("INSERT INTO wishlists (userId, bookId) VALUES (%s, %s)", (user_id, book_id))
                mysql.connection.commit()
                return jsonify({'message': 'book added to wishlist successfully'}), 200
        else:
            return jsonify({'message': 'Userid and bookid required'}), 405
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


@app.route('/removeFromWishlist', methods=['DELETE'])
def handle_remove_from_wishlist():
    try:
        user_id = request.args.get('userId')
        book_id = request.args.get('bookId')

        if user_id and book_id:
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM wishlists WHERE userId = %s AND bookId = %s", (user_id, book_id))
            mysql.connection.commit()
            cursor.execute("""
                SELECT books.id, books.code, books.title, books.department, 
                       books.price, books.available, books.level, 
                       books.rating, books.category  
                FROM books 
                JOIN wishlists ON books.id = wishlists.bookid 
                WHERE wishlists.userId = %s
            """, (user_id,))
            
            wishlist_items = cursor.fetchall()
            cursor.close()
            return jsonify(wishlist_items), 200
        else:
            return jsonify({'error': 'User ID and Book ID are required'}), 400  # 400 Bad Request for missing parameters
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Handle any exceptions


@app.route('/getWishlist', methods=['GET'])
def handle_get_wishlist():
    try:
        # Directly retrieve the 'userId' from request.args
        user_id = request.args.get('userId')
        print(f"get wishlist invoked {user_id}")
        
        if user_id:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT books.id, books.code, books.title, books.department, 
                       books.price, books.available, books.level, 
                       books.rating, books.category  
                FROM books 
                JOIN wishlists ON books.id = wishlists.bookid 
                WHERE wishlists.userId = %s
            """, (user_id,))
            
            wishlist_items = cursor.fetchall()
            cursor.close()
            
            return jsonify(wishlist_items), 200
        else:
            return jsonify({'error': 'User ID is required'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

