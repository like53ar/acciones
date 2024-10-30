from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "supersecretkey"
db = SQLAlchemy(app)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    total_investment = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=True)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_type = db.Column(db.String(10), nullable=False)  # Nuevo campo para tipo de transacción (compra o venta)

    def price_difference(self):
        return (self.current_price - self.purchase_price) * self.quantity if self.current_price else 0

    def percentage_difference(self):
        return ((self.current_price - self.purchase_price) / self.purchase_price * 100) if self.current_price else 0

    def days_elapsed(self):
        return (datetime.utcnow() - self.purchase_date).days

@app.route('/')
def index():
    stocks = Stock.query.all()
    return render_template('portfolio.html', stocks=stocks)

@app.route('/add', methods=['POST'])
def add_stock():
    company = request.form['company'].upper()
    symbol = request.form['symbol'].upper()
    quantity = int(request.form['quantity'])
    purchase_price = float(request.form['purchase_price'])
    total_investment = quantity * purchase_price
    current_price = float(request.form['current_price'])
    purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d')
    transaction_type = request.form['transaction_type']  # Capturar el tipo de transacción
    
    new_stock = Stock(company=company, symbol=symbol, quantity=quantity,
                      purchase_price=purchase_price, total_investment=total_investment,
                      current_price=current_price, purchase_date=purchase_date,
                      transaction_type=transaction_type)
    
    db.session.add(new_stock)
    db.session.commit()
    flash('Transacción agregada correctamente')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_stock(id):
    stock_to_delete = Stock.query.get_or_404(id)
    db.session.delete(stock_to_delete)
    db.session.commit()
    flash('Transacción eliminada correctamente')
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
