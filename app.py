from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'MuseumDB1'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = 'your_secret_key'  # Set a strong secret key

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/events')
def events():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    cursor.close()
    return render_template('events.html', events=events)

# Booking Form Route
@app.route('/book_ticket', methods=['GET', 'POST'])
def book_ticket():
    if request.method == 'POST':
        # Collect form data
        visitor_name = request.form['visitor_name']
        visitor_email = request.form['visitor_email']
        visitor_phone = request.form['visitor_phone']
        event_id = request.form['event_id']
        visit_date = request.form['visit_date']
        adults = int(request.form['adults'])
        students = int(request.form['students'])
        children = int(request.form['children'])

        # Calculate total amount (example prices: adults $20, students $15, children $10)
        total_amount = adults * 20 + students * 15 + children * 10

        # Insert visitor details into visitors table
        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO visitors (name, email, phone) VALUES (%s, %s, %s)',
            (visitor_name, visitor_email, visitor_phone)
        )
        visitor_id = cursor.lastrowid  # Get the inserted visitor's ID
        
        # Insert ticket details into tickets table
        cursor.execute(
            'INSERT INTO tickets (event_id, visit_date, adults, students, children, total_amount, visitor_id) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (event_id, visit_date, adults, students, children, total_amount, visitor_id)
        )
        ticket_id = cursor.lastrowid  # Get the inserted ticket's ID
        mysql.connection.commit()
        cursor.close()

        # Store ticket_id in session to pass to the summary page
        session['ticket_id'] = ticket_id

        # Redirect to the summary page
        return redirect(url_for('ticket_summary'))

    # Fetch available events for the dropdown
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM events')
    events = cursor.fetchall()
    cursor.close()

    return render_template('book_ticket.html', events=events)

@app.route('/ticket_summary', methods=['GET', 'POST'])
def ticket_summary():
    ticket_id = session.get('ticket_id')

    if ticket_id:
        # Fetch ticket and visitor details
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT tickets.*, events.title, visitors.name, visitors.email, visitors.phone '
            'FROM tickets '
            'JOIN events ON tickets.event_id = events.id '
            'JOIN visitors ON tickets.visitor_id = visitors.id '
            'WHERE tickets.id = %s', [ticket_id]
        )
        ticket_details = cursor.fetchone()
        cursor.close()

        if request.method == 'POST':
            # Proceed to payment or confirm booking
            return redirect(url_for('ticket'))

        return render_template('ticket_summary.html', ticket=ticket_details)

    return redirect(url_for('book_ticket'))

@app.route('/ticket')
def ticket():
    ticket_id = session.get('ticket_id')

    if ticket_id:
        # Fetch ticket and event details
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT tickets.*, events.title, visitors.name, visitors.email, visitors.phone '
            'FROM tickets '
            'JOIN events ON tickets.event_id = events.id '
            'JOIN visitors ON tickets.visitor_id = visitors.id '
            'WHERE tickets.id = %s', [ticket_id]
        )
        ticket_details = cursor.fetchone()
        cursor.close()

        return render_template('ticket.html', ticket=ticket_details)

    return redirect(url_for('book_ticket'))

# Route for the Membership page
@app.route('/membership')
def membership():
    return render_template('membership.html')

# Routes for the Login and Registration pages
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
