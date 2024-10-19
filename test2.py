from flask import Flask, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.secret_key = 'super_secret_key'

login_manager = LoginManager(app)
users = {"testuser": generate_password_hash('password')}


class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    return User()

oauth = OAuth(app)
auth0 = oauth.register(
    'authO',
    client_id='MHO9YJ93n2Hjc38E94Q6kDWt8Bk3Pj5I',
    client_secret='UAt5iJ4enrFn5U3nbm9Gi8HrSwkgbK896VpQpZAsZHyhQyU4MlJkyWw1LX5d9Wcp',
    api_base_url='dev-0ffge6zvwb2fsxxb.us.auth0.com',
    access_token_url='https://dev-0ffge6zvwb2fsxxb.us.auth0.com/oauth/token',
    authorize_url='https://dev-0ffge6zvwb2fsxxb.us.auth0.com/oauth/authorize',
    client_kwargs={'scope': 'openid profile email'},
)

@app.route('/')
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login Page</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                margin: 0;
                padding: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .login-container {
                background-color: #fff;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                width: 300px;
                text-align: center;
            }
            h1 {
                font-size: 24px;
                margin-bottom: 20px;
            }
            input[type="text"], input[type="password"] {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            button {
                width: 100%;
                padding: 10px;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #218838;
            }
            .auth0-login {
                margin-top: 10px;
                background-color: #007bff;
            }
            .auth0-login:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h1>Welcome! Please Log In</h1>
            <form method="POST" action="/login_direct">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Log In</button>
            </form>
            <form method="GET" action="/login">
                <button class="auth0-login" type="submit">Log in with Auth0</button>
        </div>
    </body>
    </html>
    """
    return html_content

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=url_for('callback_handling', _external=True))

@app.route('/callback')
def callback_handling():
    resp = auth0.authorize_access_token()
    session['jwt_payload'] = resp.json()
    user = User()
    user.id = session['jwt_payload']['sub']
    login_user(user)
    return redirect('/dashboard')

@app.route('/login_direct', methods=["POST"])
def login_direct():
    if check_password_hash(users.get(request.form['username'], ''), request.form['password']):
        user = User()
        user.id = request.form["username"]
        login_user(user)
        return redirect('/dashboard')
    else:
        session['error'] = 'Invalid credentials, please try again!'
        return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    return 'Welcome to the Dashboard!'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
