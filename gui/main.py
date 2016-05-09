from flask import Flask,render_template,session
from app import create_app

if __name__ == '__main__':
    app = create_app('development')
    app.config['SECRET_KEY'] = 'top secret!'
    app.config['CACHE_TYPE'] = 'null'
    app.run(debug=True)

