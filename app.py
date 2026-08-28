import os
print("======================================")
print("RUNNING APP FROM:")
print(os.path.abspath(__file__))
print("======================================")
from flask import Flask, render_template

from config import SECRET_KEY
from database import db_setup

from routes.auth import auth
from routes.exam import exam

app = Flask(__name__)

app.secret_key = SECRET_KEY

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(exam)

@app.route("/")
def home():
    return render_template("index.html")

#code to run 

if __name__ == "__main__":
    print("\n========== ROUTES ==========")


    for rule in app.url_map.iter_rules():
        
        print(rule)

    print("============================\n")
    app.run(debug=True, use_reloader=False)
    
