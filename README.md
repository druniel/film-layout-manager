# Film Layout Manager (Filmana generátor rozvržení filmů)

## Description

Film Layout Manager is a Python-based desktop application that helps organize films into various categories using a priority-based system. It features a dynamic data table, a modern dark user interface, and graph-based data distribution logic.

## Features

* **Dynamic desktop interface:** Built with `PySide6` and styled with `qdarktheme` for a modern, native look.
* **Collapsible side menu:** Interactive navigation featuring vector icons powered by `qtawesome`.
* **Priority-based film placement:** Uses `networkx` directed flow graphs to optimally distribute films into categories based on priorities and weight rules.
* **Excel integration:** Directly loads and parses film databases from `.xlsx` files using `pandas`.
* **Smart auto-fill:** Capabilities to generate a layout of unique films and subsequently refill any remaining empty spots from a secondary rebuffer.

## Prerequisites

* Python 3.x
* Required Python packages (install via `pip install -r requirements.txt`). Key dependencies include `PySide6`, `pandas`, `networkx`, `openpyxl`, `pyqtdarktheme`, and `QtAwesome`.

## Installation

1. Clone this repository.
2. Install the required dependencies:
```sh
pip install -r requirements.txt
```

## Usage

1. Run the application using the main entry script:
```sh
python main.py
```
2. Once the application opens, click on **Načíst databázi** to load your `.xlsx` film database.
3. Use the action buttons in the side menu to generate and interact with the layout.

## Interface

The desktop GUI provides the following main actions:

* **Načíst databázi** - Opens a file dialog to load the Excel database.
* **Doplnit unikátní filmy** - Triggers the graph flow algorithm to fill the table with unique films.
* **Doplnit prázdná místa** - Fills remaining empty slots in the table using items from the rebuffer.
* **Reset** - Clears the current table layout and restores it to its initial state.
* **Zavřít aplikaci** - Safely exits the program.

## Project Structure

* `main.py` - The main application entry point that initializes the backend processor and the GUI window.
* `gui.py` - Contains the `MainWindow` class, UI logic, custom QSS styling, and the `FilmTableModel` for displaying data.
* `ui_main.py` - The raw, auto-generated UI layout file compiled from Qt Designer.
* `backend.py` - Contains the `FilmProcessor` class acting as the bridge between the GUI and data operations.
* `aux_functions.py` - Core algorithmic logic, including Pandas data cleaning, graph building, and free space calculations.
* `requirements.txt` - List of exact package versions needed to run the application.