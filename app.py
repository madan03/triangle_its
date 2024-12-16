from flask import Flask, request, render_template
from rdflib import Graph
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Load ontology (if available)
g = Graph()
ontology_path = "triangle_area_ontology.rdf"
ontology_loaded = False

if os.path.exists(ontology_path):
    g.parse(ontology_path)
    ontology_loaded = True

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/input", methods=["GET", "POST"])
def input_triangle():
    if request.method == "POST":
        base = float(request.form["base"])
        height = float(request.form["height"])
        area = 0.5 * base * height
        return render_template("result.html", base=base, height=height, area=area)
    return render_template("input.html")

@app.route("/examples")
def examples():
    example_data = [
        {"base": 10, "height": 5, "area": 25},
        {"base": 8, "height": 4, "area": 16},
        {"base": 6, "height": 3, "area": 9}
    ]
    return render_template("examples.html", examples=example_data, error=None)

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        answer = float(request.form["answer"])
        correct = 25  # Correct answer for base=10 and height=5
        is_correct = abs(answer - correct) < 0.1
        return render_template("quiz_result.html", is_correct=is_correct, correct_answer=correct)
    return render_template("quiz.html")

@app.route("/visualize/<float:base>/<float:height>")
def visualize_triangle(base, height):
    img_path = "static/triangle.png"
    plt.figure()
    plt.plot([0, base, 0], [0, 0, height], marker="o")
    plt.text(base / 2, height / 2, f"Area = {0.5 * base * height} sq units")
    plt.savefig(img_path)
    plt.close()
    return render_template("visual.html", img_url=f"/{img_path}")

if __name__ == "__main__":
    app.run(debug=True)
