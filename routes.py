import random
import string
from datetime import datetime
from decimal import Decimal
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import or_, desc
from app import app, db
from models import User, Wallet, Transaction
from forms import RegistrationForm, LoginForm, TransferForm, ProfileForm

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access your wallet.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_wallet_number():
    """Generate a unique 10-digit wallet number"""
    while True:
        wallet_number = ''.join(random.choices(string.digits, k=10))
        if not Wallet.query.filter_by(wallet_number=wallet_number).first():
            return wallet_number

def generate_transaction_reference():
    """Generate a unique transaction reference"""
    while True:
        reference = 'NP' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        if not Transaction.query.filter_by(reference=reference).first():
            return reference

@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                phone_number=form.phone_number.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.flush()  # Get user ID before creating wallet
            
            # Create wallet for the user with ₦2000 starting balance
            wallet = Wallet(
                user_id=user.id,
                wallet_number=generate_wallet_number(),
                balance=2000.00
            )
            
            db.session.add(wallet)
            db.session.commit()
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Check if login is username or email
        user = User.query.filter(
            or_(User.username == form.username.data, User.email == form.username.data)
        ).first()
        
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username/email or password.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    wallet = current_user.wallet
    if not wallet:
        # Create wallet if it doesn't exist with ₦2000 starting balance
        wallet = Wallet(
            user_id=current_user.id,
            wallet_number=generate_wallet_number(),
            balance=2000.00
        )
        db.session.add(wallet)
        db.session.commit()
    
    # Get recent transactions
    recent_transactions = Transaction.query.filter(
        or_(Transaction.sender_id == current_user.id, Transaction.receiver_id == current_user.id)
    ).order_by(desc(Transaction.created_at)).limit(5).all()
    
    return render_template('dashboard.html', wallet=wallet, transactions=recent_transactions)

@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    """Money transfer"""
    form = TransferForm()
    wallet = current_user.wallet
    
    if form.validate_on_submit():
        recipient_identifier = form.recipient.data
        amount = form.amount.data
        description = form.description.data or 'Money transfer'
        
        # Check sender balance
        if wallet.balance < amount:
            flash('Insufficient balance for this transaction.', 'error')
            return render_template('transfer.html', form=form, wallet=wallet)
        
        # Find recipient by username or wallet number
        recipient_user = User.query.filter_by(username=recipient_identifier).first()
        if not recipient_user:
            recipient_wallet = Wallet.query.filter_by(wallet_number=recipient_identifier).first()
            if recipient_wallet:
                recipient_user = recipient_wallet.user
        
        if not recipient_user:
            flash('Recipient not found. Please check the username or wallet number.', 'error')
            return render_template('transfer.html', form=form, wallet=wallet)
        
        if recipient_user.id == current_user.id:
            flash('You cannot transfer money to yourself.', 'error')
            return render_template('transfer.html', form=form, wallet=wallet)
        
        try:
            # Create transaction record
            transaction = Transaction(
                sender_id=current_user.id,
                receiver_id=recipient_user.id,
                amount=amount,
                description=description,
                reference=generate_transaction_reference(),
                status='completed'  # For MVP, all transactions are automatically completed
            )
            
            # Update balances
            wallet.balance -= amount
            recipient_user.wallet.balance += amount
            wallet.updated_at = datetime.utcnow()
            recipient_user.wallet.updated_at = datetime.utcnow()
            
            db.session.add(transaction)
            db.session.commit()
            
            flash(f'Transfer of ₦{amount:,.2f} to {recipient_user.get_full_name()} completed successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Transfer error: {e}")
            flash('An error occurred while processing your transfer. Please try again.', 'error')
    
    return render_template('transfer.html', form=form, wallet=wallet)

@app.route('/transactions')
@login_required
def transactions():
    """Transaction history"""
    page = request.args.get('page', 1, type=int)
    
    user_transactions = Transaction.query.filter(
        or_(Transaction.sender_id == current_user.id, Transaction.receiver_id == current_user.id)
    ).order_by(desc(Transaction.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('transactions.html', transactions=user_transactions)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    form = ProfileForm()
    
    if form.validate_on_submit():
        try:
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.email = form.email.data
            current_user.phone_number = form.phone_number.data
            current_user.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Profile update error: {e}")
            flash('An error occurred while updating your profile. Please try again.', 'error')
    
    # Pre-populate form with current user data
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.phone_number.data = current_user.phone_number
    
    return render_template('profile.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
