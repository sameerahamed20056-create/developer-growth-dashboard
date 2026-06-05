from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# =========================
# DATABASE CONFIG (FIXED)
# =========================

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'logs.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# MODEL
# =========================

class Dailylog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_date = db.Column(db.Date, default=date.today)
    learning_hours = db.Column(db.Float, nullable=False)
    coding_hours = db.Column(db.Float, nullable=False)
    project_hours = db.Column(db.Float, nullable=False)
    entertainment_hours = db.Column(db.Float, nullable=False)


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("home.html")


# =========================
# ADD LOG
# =========================

@app.route("/add", methods=["GET", "POST"])
def add_log():
    if request.method == "POST":
        new_log = Dailylog(
            learning_hours=float(request.form["learning_hours"]),
            coding_hours=float(request.form["coding_hours"]),
            project_hours=float(request.form["project_hours"]),
            entertainment_hours=float(request.form["entertainment_hours"])
        )

        db.session.add(new_log)
        db.session.commit()

        return redirect("/logs")

    return render_template("add_log.html")


# =========================
# LOGS PAGE
# =========================

@app.route("/logs")
def logs():
    logs = Dailylog.query.all()
    return render_template("logs.html", logs=logs)


# =========================
# EDIT
# =========================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
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


# =========================
# DELETE
# =========================

@app.route("/delete/<int:id>")
def delete_log(id):
    log = Dailylog.query.get_or_404(id)

    db.session.delete(log)
    db.session.commit()

    return redirect("/logs")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():
    logs = Dailylog.query.all()

    total_learning = sum([l.learning_hours for l in logs])
    total_coding = sum([l.coding_hours for l in logs])
    total_project = sum([l.project_hours for l in logs])
    total_entertainment = sum([l.entertainment_hours for l in logs])

    total_logs = len(logs)
    average_learning = total_learning / total_logs if total_logs > 0 else 0

    labels = ["Learning", "Coding", "Project", "Entertainment"]

    values = [
        total_learning,
        total_coding,
        total_project,
        total_entertainment
    ]

    # =========================
    # BAR CHART
    # =========================
    plt.figure(figsize=(8, 5))
    plt.bar(labels, values)
    plt.title("Developer Activity Summary", fontsize=16, fontweight="bold")
    plt.xlabel("Activity Type", fontsize=14)
    plt.ylabel("Hours", fontsize=14)

    os.makedirs("static", exist_ok=True)
    plt.savefig("static/chart.png")
    plt.close()

    # =========================
    # PIE CHART
    # =========================
    plt.figure(figsize=(6, 6))

    if sum(values) > 0:
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


# =========================
# INIT DB (RENDER SAFE)
# =========================

with app.app_context():
    db.create_all()


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run()