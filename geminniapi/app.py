from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# 🔑 Put your Gemini API key here
genai.configure(api_key="AIzaSyD4bpPhG3-P6KV--rGrPpxIU1lYKCSg-8A")

# Load Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")


def explain_transaction(transaction):
    try:
        prompt = f"Explain this financial transaction in simple simple words: {transaction}"

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        print("ERROR:", e)
        return "AI error. Check terminal."


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    transaction = data.get("transaction")

    if not transaction:
        return jsonify({"error": "No transaction provided"}), 400

    explanation = explain_transaction(transaction)

    return jsonify({"explanation": explanation})


if __name__ == "__main__":
    app.run(debug=True)