from flask import Flask, jsonify, render_template, request
import google.generativeai as genai
import re

genai.configure(api_key="API-KEY")

model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/submit_ingredients', methods=['POST'])
def submit_ingredients():
    data = request.get_json()
    ingredients = data.get("ingredients", [])
    
    responses = []  # List to hold multiple dish responses

    # Construct the prompt for the API to generate better output
    for _ in range(3):  # Generate three dishes
        inp = (
            "Based on the following ingredients: " + ", ".join(ingredients) + 
            ", please provide a dish name, the ingredients needed (if different), and the steps to prepare it. "
            "Format your response as follows: \n"
            "Dish Name: [Name of the dish] \n"
            "Ingredients: [List of ingredients] \n"
            "Steps: [Step-by-step instructions]"
        )

        # Generate content using Generative AI model
        response = model.generate_content(inp)

        # Extract response text
        response_text = response.text if hasattr(response, 'text') else "No response generated."

        # Clean the response text by removing * and # symbols
        cleaned_text = re.sub(r'[\*#]', '', response_text)

        # Simple parsing: Assuming response follows "Dish Name: ... Ingredients: ... Steps: ..."
        dish_name = ""
        dish_ingredients = []
        dish_steps = []

        # Split and organize the response into sections
        if "Ingredients:" in cleaned_text and "Steps:" in cleaned_text:
            parts = re.split(r'Dish Name:|Ingredients:|Steps:', cleaned_text)
            dish_name = parts[1].strip() if len(parts) > 1 else ""
            # Split ingredients by comma and remove whitespace
            dish_ingredients = [ingredient.strip() for ingredient in parts[2].strip().split(',')] if len(parts) > 2 else []
            # Split steps by newline and remove empty entries
            dish_steps = [step.strip() for step in parts[3].strip().split('\n') if step.strip()] if len(parts) > 3 else []
        
        # Add the dish details to the responses list
        responses.append({
            "DishName": dish_name,
            "DishIngredients": dish_ingredients,
            "DishSteps": dish_steps
        })

    # Send a JSON response back to the client with parsed details
    return jsonify(responses)

@app.route('/aboutus')
def contact_ui():
    return render_template('aboutus.html')

@app.route('/login')
def login_ui():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
