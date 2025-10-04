from flask import Flask, jsonify, render_template
from data_manager import DataManager

app = Flask(__name__)

data_manager = DataManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spustit')
def get_data():
    try:
        tabulka = data_manager.inicializuj()
        return jsonify(tabulka)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/spustit_doplneni')
def get_data_doplneni():
    try:
        tabulka = data_manager.dopln()
        return jsonify(tabulka)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/reset')
def reset_data():
    data_manager.reset()
    return jsonify({"status": "OK", "message": "Data byla resetována."})

if __name__ == '__main__':
    app.run(debug=True)