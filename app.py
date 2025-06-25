from flask import Flask, render_template_string, request, jsonify
import json

# Load the rule dictionary
with open("final_mic_rule_dict.json", "r") as f:
    rule_dict = json.load(f)

app = Flask(__name__)

# Build organism and antibiotic mapping
organisms = list(rule_dict.keys())

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    selected_organism = None
    selected_antibiotic = None
    mic_input = None

    if request.method == 'POST':
        selected_organism = request.form.get('organism')
        selected_antibiotic = request.form.get('antibiotic')
        mic_input = request.form.get('mic')

        try:
            mic_value = float(mic_input)
            rules = rule_dict.get(selected_organism, {}).get(selected_antibiotic, [])
            for rule in rules:
                if rule['min'] <= mic_value <= rule['max']:
                    result = rule['category']
                    break
            if not result:
                result = "Value not defined by CLSI"
        except:
            result = "Invalid MIC input"

    return render_template_string(template, 
        organisms=organisms, 
        rule_dict=rule_dict,
        result=result,
        selected_organism=selected_organism,
        selected_antibiotic=selected_antibiotic,
        mic_input=mic_input
    )

# HTML Template embedded
template = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MIC Categorizer</title>
  <style>
    body {
      background-color: #f4f6f8;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      margin: 0;
      padding: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }
    .container {
      background: #fff;
      padding: 30px 40px;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
      width: 450px;
    }
    h2 {
      text-align: center;
      color: #333;
    }
    label {
      font-weight: 600;
      display: block;
      margin-top: 20px;
      margin-bottom: 8px;
      color: #555;
    }
    select, input[type="text"] {
      width: 100%;
      padding: 10px;
      font-size: 15px;
      border-radius: 6px;
      border: 1px solid #ccc;
      box-sizing: border-box;
    }
    input[type="submit"] {
      margin-top: 25px;
      width: 100%;
      padding: 12px;
      background-color: #007bff;
      color: white;
      border: none;
      font-weight: bold;
      border-radius: 6px;
      cursor: pointer;
      font-size: 16px;
    }
    input[type="submit"]:hover {
      background-color: #0056b3;
    }
    .result {
      margin-top: 25px;
      padding: 12px;
      text-align: center;
      border-radius: 6px;
      font-size: 18px;
      font-weight: bold;
    }
    .susceptible { background-color: #d4edda; color: #155724; }
    .intermediate { background-color: #fff3cd; color: #856404; }
    .resistant { background-color: #f8d7da; color: #721c24; }
    .undefined { background-color: #e2e3e5; color: #383d41; }
  </style>
  <script>
    function updateAntibiotics() {
      const organism = document.getElementById("organism").value;
      const allRules = {{ rule_dict|tojson }};
      const abSelect = document.getElementById("antibiotic");
      abSelect.innerHTML = "";

      if (organism in allRules) {
        const antibiotics = Object.keys(allRules[organism]);
        antibiotics.forEach(ab => {
          const option = document.createElement("option");
          option.text = ab;
          option.value = ab;
          abSelect.add(option);
        });
      }
    }
  </script>
</head>
<body>
  <div class="container">
    <h2>MIC Classifier</h2>
    <form method="POST">
      <label for="organism">Select Organism:</label>
      <select name="organism" id="organism" onchange="updateAntibiotics()" required>
        <option value="">-- Choose Organism --</option>
        {% for org in organisms %}
          <option value="{{ org }}" {% if org == selected_organism %}selected{% endif %}>{{ org }}</option>
        {% endfor %}
      </select>

      <label for="antibiotic">Select Antibiotic:</label>
      <select name="antibiotic" id="antibiotic" required>
        {% if selected_organism and selected_antibiotic %}
          {% for ab in rule_dict[selected_organism].keys() %}
            <option value="{{ ab }}" {% if ab == selected_antibiotic %}selected{% endif %}>{{ ab }}</option>
          {% endfor %}
        {% endif %}
      </select>

      <label for="mic">Enter MIC Value:</label>
      <input type="text" name="mic" id="mic" value="{{ mic_input or '' }}" required>

      <input type="submit" value="Categorize">
    </form>

    {% if result %}
      <div class="result 
        {% if result == 'Susceptible' %}susceptible
        {% elif result == 'Intermediate' %}intermediate
        {% elif result == 'Resistant' %}resistant
        {% else %}undefined
        {% endif %}">
        Result: {{ result }}
      </div>
    {% endif %}
  </div>
</body>
</html>
"""
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # use Render's PORT or fallback to 5000 locally
    app.run(host="0.0.0.0", port=port)

