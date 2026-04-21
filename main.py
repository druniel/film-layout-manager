from flask import Flask, jsonify, render_template
from data_manager import DataManager

app = Flask(__name__) #inicializuje flask

data_manager = DataManager() #vytvoří datovou strukturu

@app.route('/') #načte index.html
def index():
    return render_template('index.html')

@app.route('/launch') #spustí proces unikátních filmů a načte tabulku s unikátními filmy, pokud je nějaký probém, tak vyhodí nějakou chybu
def get_data():
    try:
        result_table, message = data_manager.initialize()
        return jsonify({"table": result_table, "message": message})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/launch_additional') #spustí proces opakovaných filmů a načte tabulku i s nimi, pokud je nějaký problém, vyhodí buď takovou nebo makovou chybu, ale jaké jsou to chyby a proč dvě?
def get_data_additional():
    try:
        result_table, message = data_manager.fill_free_spaces()
        return jsonify({"table": result_table, "message": message})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/reset') #prostě vymaže tabulku a vyhodí o tom okýnko
def reset_data():
    data_manager.reset()
    return jsonify({"status": "OK", "message": "Data byla resetována."})

if __name__ == '__main__': #server se spustí jen když je soubor přímo spuštěn, ne importován
    app.run(debug=True)