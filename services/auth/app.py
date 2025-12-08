from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import random
import string
import time
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# --- 資料庫設定 (從環境變數讀取) ---
db_user = os.environ.get('DB_USER', 'root')
db_pass = os.environ.get('DB_PASSWORD', 'mypassword')
db_host = os.environ.get('DB_HOST', 'db') # Docker service name
db_name = os.environ.get('DB_NAME', 'auth_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Email 設定 (請務必修改為你的真實設定) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'n503jackie2@gmail.com'  # <--- 請修改
app.config['MAIL_PASSWORD'] = 'dcatuupwwtmlcuqf'      # <--- 請修改 (非登入密碼)

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- 資料庫模型 ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- 工具函式：產生驗證碼 ---
def generate_code():
    return ''.join(random.choices(string.digits, k=6))

# --- 路由 ---



@app.route('/')
def index():
    return render_template('index.html')

# 1. 註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email 已經被註冊過了')
            return redirect(url_for('register'))

        # 產生驗證碼與加密密碼
        code = generate_code()
        hashed_pw = generate_password_hash(password)

        new_user = User(username=username, email=email, password_hash=hashed_pw, verification_code=code)
        db.session.add(new_user)
        db.session.commit()

        # 寄送驗證信
        try:
            msg = Message('您的驗證碼', sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f'你好 {username}，你的驗證碼是：{code}'
            mail.send(msg)
            
            # 將 User ID 暫存於 Session 以便下一步驗證
            session['temp_user_id'] = new_user.id
            flash('註冊成功！驗證碼已寄送到您的信箱')
            return redirect(url_for('verify'))
        except Exception as e:
            flash(f'寄信失敗: {str(e)}')
            return redirect(url_for('register'))

    return render_template('register.html')

# 2. 輸入驗證碼
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        code = request.form.get('code')
        user_id = session.get('temp_user_id')
        
        if not user_id:
            return redirect(url_for('register'))

        user = User.query.get(user_id)
        
        if user and user.verification_code == code:
            user.is_verified = True
            user.verification_code = None # 清除驗證碼
            db.session.commit()
            session.pop('temp_user_id', None)
            flash('驗證成功，請登入！')
            return redirect(url_for('login'))
        else:
            flash('驗證碼錯誤')

    return render_template('verify.html')

# 3. 登入
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_verified:
                flash('請先完成 Email 驗證')
                session['temp_user_id'] = user.id
                return redirect(url_for('verify'))
                
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('帳號或密碼錯誤')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# 加入這段來建立資料庫表格
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # --- 加入重試機制 ---
    with app.app_context():
        while True:
            try:
                db.create_all()
                print("資料庫連線成功，表格已建立！")
                break  # 成功就跳出迴圈
            except OperationalError:
                print("資料庫還沒準備好，等待 3 秒後重試...")
                time.sleep(3)  # 等待 3 秒
    
    app.run(host='0.0.0.0', debug=True)