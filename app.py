from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)

# Database Config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///developer.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Model
class Dailylog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_date = db.Column(db.Date, default=date.today)
    learning_hours = db.Column(db.Float, nullable=False)
    coding_hours = db.Column(db.Float, nullable=False)
    project_hours = db.Column(db.Float, nullable=False)
    entertainment_hours = db.Column(db.Float, nullable=False)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/add", methods=["GET", "POST"])
def add_log():
    if request.method == "POST":
        new_log = Dailylog(
            learning_hours=request.form["learning_hours"],
            coding_hours=request.form["coding_hours"],
            project_hours=request.form["project_hours"],
            entertainment_hours=request.form["entertainment_hours"]
        )

        db.session.add(new_log)
        db.session.commit()

        return redirect("/logs")

    return render_template("add_log.html")


@app.route("/logs")
def logs():
    logs = Dailylog.query.all()
    return render_template("logs.html", logs=logs)

@app.route("/edit/<int:id>",methods = ["GET", "POST"])
def edit_log(id):
    
    log = Dailylog.query.get_or_404(id)
    
    if request.method == "POST":
        
        log.learning_hours = float(request.form["learning_hours"])
        log.coding_hours = float(request.form["coding_hours"])
        log.project_hours = float(request.form["project_hours"])
        log.entertainment_hours = float(request.form["entertainment_hours"])
        
        db.session.commit()
        
        return redirect("/logs")
    
    return render_template("edit_log.html", log=log)

@app.route("/delete/<int:id>")
def delete_log(id):
    
    log = Dailylog.query.get_or_404(id)
    
    db.session.delete(log)
    db.session.commit()
    
    return redirect("/logs")

@app.route("/dashboard")
def dashboard():
    logs = Dailylog.query.all()

    total_learning = 0
    total_coding = 0
    total_project = 0
    total_entertainment = 0

    for log in logs:
        total_learning += log.learning_hours
        total_coding += log.coding_hours
        total_project += log.project_hours
        total_entertainment += log.entertainment_hours

    total_logs = len(logs)

    if total_logs > 0:
        average_learning = total_learning / total_logs
    else:
        average_learning = 0
        
    labels = ["Learning", "Coding", "Project", "Entertainment"]

    values = [
    total_learning,
    total_coding,
    total_project,
    total_entertainment
    ]

    plt.figure(figsize=(8, 5))

    plt.bar(labels, values)

    plt.title("Developer Activity Summary",
              fontsize=16,
              fontweight="bold"
              )
    
    plt.xlabel("Activity Type", fontsize=14)
    
    plt.ylabel("Hours", fontsize=14)

    plt.savefig("static/chart.png")

    plt.close()
    
    plt.figure(figsize=(6, 6))
    
    max_index = values.index(max(values))
    
    explode = [0, 0, 0, 0]
    explode[max_index] = 0.1

    plt.pie(
    values,
    labels=labels,
    autopct="%1.1f%%",
    explode=explode,
    shadow=True
    )

    plt.title("Activity Distribution", fontsize=16, fontweight="bold")

    plt.savefig("static/pie_chart.png")

    plt.close()
    


    return render_template(
        "dashboard.html",
        total_learning=total_learning,
        total_coding=total_coding,
        total_project=total_project,
        total_entertainment=total_entertainment,
        total_logs=total_logs,
        average_learning=average_learning
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)