from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    transactions = db.relationship('Transaction', backref='category', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\yesal\\Desktop\\Python\\Budget\\test.db'
db.init_app(app)

# Create the database tables.
with app.app_context():
    db.create_all()

@app.route('/categories', methods=['POST'])
def handle_categories():
    if request.method == 'POST':
        data = request.form
        new_category = Category(name=data['name'])
        db.session.add(new_category)
        db.session.commit()
        return redirect(url_for('show_categories'))
    else:
        # Handle GET request here
        categories = Category.query.all()
        return jsonify([{'id': cat.id, 'name': cat.name} for cat in categories])

@app.route('/categories/<int:category_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'GET':
        return jsonify(name=category.name)
    elif request.method == 'PUT':
        data = request.form
        category.name = data['name']
        db.session.commit()
        return jsonify(category_id=category.id), 200
    elif request.method == 'DELETE':
        db.session.delete(category)
        db.session.commit()
        return '', 204
    

@app.route('/transactions', methods=['POST'])
def create_transaction():
    if request.method == 'POST':
        data = request.form
        new_transaction = Transaction(description=data['description'], amount=float(data['amount']), category_id=int(data['category_id']))
        db.session.add(new_transaction)
        db.session.commit()
        return redirect(url_for('show_transactions'))
    else:
        transactions = Transaction.query.all()
        return jsonify([{'description': tran.description, 'amount': tran.amount} for tran in transactions])
        



@app.route('/transactions/<int:transaction_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if request.method == 'GET':
        return jsonify(description=transaction.description, amount=transaction.amount, category_id=transaction.category_id)
    elif request.method == 'PUT':
        data = request.form
        transaction.description = data['description']
        transaction.amount = float(data['amount'])
        transaction.category_id = int(data['category_id'])
        db.session.commit()
        return jsonify(transaction_id=transaction.id), 200
    elif request.method == 'DELETE':
        db.session.delete(transaction)
        db.session.commit()
        return '', 204

@app.route('/create_transaction', methods=['GET'])
def create_transaction_form():
    categories = Category.query.all()
    return render_template('create_transaction.html', categories=categories)

@app.route('/create_category', methods=['GET'])
def create_category_form():
    return render_template('create_category.html')

@app.route('/show_categories', methods=['GET'])
def show_categories():
    categories = Category.query.all()
    return render_template('show_categories.html', categories=categories)

@app.route('/show_transactions', methods=['GET'])
def show_transactions():
    transactions = Transaction.query.all()
    for transaction in transactions:
      transaction.amount = float(transaction.amount)
    
    totals_by_category = db.session.query(
        Category.name, func.sum(Transaction.amount)
    ).join(Transaction).group_by(Category.name).all()

    total_general = float(db.session.query(func.sum(Transaction.amount)).scalar())

    return render_template('show_transactions.html', transactions=transactions,totals_by_category=totals_by_category, total_general=total_general)

if __name__ == '__main__':
    app.run(debug=True)