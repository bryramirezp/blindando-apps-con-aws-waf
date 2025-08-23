from flask import Flask
from flask import request, redirect, url_for, session, render_template_string

app = Flask(__name__)

from flask_mysqldb import MySQL

mysql = MySQL()

app.secret_key = 'uyjyuttg27903b4'

# username puede ser lo que sea
# password = ' OR '1'='1

# MySQL config
db_config = {
    'MYSQL_HOST': 'localhost',
    'MYSQL_USER': 'user',
    'MYSQL_PASSWORD': 'password',
    'MYSQL_DB': 'database'
}

app.config.update(db_config)
mysql.init_app(app)

@app.route('/')
def home():
    if 'username' in session:
        return f'<a href="{url_for("logout")}">Logout</a><h1>Bienvenido, {session["username"]}!</h1><p>Logged in.</p>'
    return f'<a href="{url_for("login")}">Login</a><h1>Bienvenido a mi sitio con flask!</h1><p>En ECS Fargate.</p>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Vulnerable SQL query (no parameterization)
        cur = mysql.connection.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cur.execute(query)
        user = cur.fetchone()
        cur.close()

        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return '<h1>Error al ingresar. Credenciales invalidas.</h1><a href="login">Login</a>'

    return render_template_string('''
        <a href="{{ url_for("home") }}">Home</a>
        <form method="post">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <input type="submit" value="Login">
        </form>
    ''')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)