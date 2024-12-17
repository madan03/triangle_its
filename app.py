from flask import Flask, request, render_template
from rdflib import Graph, Namespace
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Load the RDF ontology
g = Graph()
ontology_path = "triangle_area_ontology.rdf"  # Path to your RDF file
ontology_loaded = False

if os.path.exists(ontology_path):
    g.parse(ontology_path)
    ontology_loaded = True
    print(f"RDF ontology loaded successfully with {len(g)} triples.")
else:
    print("Ontology file not found!")

# Define the ontology namespace
ns = Namespace("http://www.semanticweb.org/ermadan/ontologies/2024/11/untitled-ontology-6#")

# Home Route
@app.route("/")
def home():
    return render_template("index.html")

# Input Route: Manual base and height input
@app.route("/input", methods=["GET", "POST"])
def input_triangle():
    if request.method == "POST":
        base = float(request.form["base"])
        height = float(request.form["height"])
        area = 0.5 * base * height

        # Generate visualization
        img_path = "static/triangle.png"
        try:
            plt.figure()
            plt.plot([0, base, 0], [0, 0, height], marker="o", linestyle="-", color="blue")
            plt.fill([0, base, 0], [0, 0, height], color="skyblue", alpha=0.5)
            plt.text(base/2, height/2, f"Area = {area} sq units", fontsize=12, color="red")
            plt.title("Triangle Visualization")
            plt.xlabel("Base")
            plt.ylabel("Height")
            plt.grid(True)
            plt.savefig(img_path)
            plt.close()
        except Exception as e:
            print(f"Error generating image: {e}")

        return render_template("result.html", base=base, height=height, area=area, img_url=f"/{img_path}")
    return render_template("input.html")

# Examples Route: Fetch data from the ontology
@app.route("/examples")
def examples():
    if not ontology_loaded:
        return render_template("examples.html", examples=[], error="Ontology not loaded.")

    # SPARQL query to fetch triangle examples
    query = """
    PREFIX : <http://www.semanticweb.org/ermadan/ontologies/2024/11/untitled-ontology-6#>
    SELECT ?triangle ?baseVal ?heightVal ?area
    WHERE {
        ?triangle a :Triangle .
        ?triangle :hasBase ?base .
        ?triangle :hasHeight ?height .
        ?triangle :valueOfArea ?area .
        ?base :valueOfBase ?baseVal .
        ?height :valueOfHeight ?heightVal .
    }
    """
    results = g.query(query)

    # Process query results
    example_data = [
        {
            "triangle": str(row.triangle).split("#")[-1],
            "base": float(row.baseVal),
            "height": float(row.heightVal),
            "area": float(row.area),
        }
        for row in results
    ]

    print("Fetched Examples:", example_data)  # Debugging output
    return render_template("examples.html", examples=example_data)

# Quiz Route: Dynamic area verification
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        try:
            answer = float(request.form["answer"])

            # Modified SPARQL query to match your ontology structure
            query = """
            PREFIX : <http://www.semanticweb.org/ermadan/ontologies/2024/11/untitled-ontology-6#>
            SELECT ?area
            WHERE {
                ?triangle a :Triangle ;
                         :valueOfArea ?area .
            }
            """
            results = g.query(query)
            results_list = list(results)
            
            if results_list:
                correct_answer_value = float(results_list[0][0])
                is_correct = abs(answer - correct_answer_value) < 0.1
                print(f"User answer: {answer}, Correct answer: {correct_answer_value}")  # Debug line
                
                return render_template("quiz_result.html", 
                                    is_correct=is_correct, 
                                    correct_answer=correct_answer_value,
                                    user_answer=answer)
            else:
                return render_template("quiz_result.html", 
                                    error="No triangle found in the ontology",
                                    user_answer=answer)
        except ValueError as e:
            return render_template("quiz_result.html", 
                                error=f"Invalid input: {str(e)}",
                                user_answer=request.form["answer"])
        except Exception as e:
            return render_template("quiz_result.html", 
                                error=f"An error occurred: {str(e)}",
                                user_answer=request.form["answer"])
            
    return render_template("quiz.html")


if __name__ == "__main__":
    app.run(debug=True)