# Film Layout Manager

An application for managing and organizing films into different categories with a dynamic table layout system.

## Description

Film Layout Manager is a Flask-based web application that helps organize films into various categories using a priority-based system. It features a dynamic table that can be filled with unique films and additional entries based on specific rules and categories.

## Features

- Dynamic film categorization
- Priority-based film placement
- Interactive web interface
- Category-specific row limits
- Automatic film distribution across categories
- Reset functionality

## Prerequisites

- Python 3.x
- Required Python packages (install via `pip install -r requirements.txt`):

## Installation

1. Clone this repository
2. Install required dependencies:
```sh
pip install -r requirements.txt
```

## Usage

1. Place your film database Excel file (`databaze_filmu.xlsx`) in the root directory
2. Run the application using:
```sh
python app.py
```
Or use the provided batch file:
```sh
run.bat
```
3. Open your web browser and navigate to `http://localhost:5000`

## Interface

The web interface provides three main actions:
- **Doplň unikátní filmy** - Fills the table with unique films based on priorities
- **Doplň zbytek filmů** - Completes the table with additional film entries
- **Resetovat data** - Resets the table to its initial state

## Project Structure

- `main.py` - Main Flask application
- `main_functions.py` - Core film distribution logic
- `aux_functions.py` - Helper functions for film management
- `data_manager.py` - Data management class
- `templates/index.html` - Web interface template
- `run.bat` - Windows batch file for easy startup
