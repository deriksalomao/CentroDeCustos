# Cost Center Control

## Project Description

"Cost Center Control" is a desktop application developed in Python with `tkinter` and `ttkbootstrap` to assist in financial management, allowing the registration, filtering, and visualization of income and expenses.

## Features

* **Entry Registration:** Add new income and expenses with details such as date, company, cost center, vehicle, category, description, type, and value.

* **Advanced Filters:** Filter entries by period (start and end date), cost center, vehicle, category, type, client, and status.

* **Data Export:** Export filtered entries to an Excel file.

* **Financial Summary:** View a quick summary of income, expenses, and the total balance, with indicative colors (green for positive balance/income, red for expense/negative balance).

* **Quick Registrations:** Quickly add new clients, vehicles, cost centers, categories, and companies.

* **Recurring Transaction Management:** Manage recurring income and expenses.

* **Visual Charts:** View the monthly evolution of revenue vs. expenses and the distribution of expenses by category through charts.

* **Login System:** Secure initial access with a simple login (default credentials: username `admin`, password `admin`).

## Prerequisites

Ensure you have Python installed on your machine (version 3.x recommended).

## Setup and Installation

Follow the steps below to set up and run the project locally:

1. **Clone the repository (or download the files):**

If you are using Git:

``bash

git clone <YOUR_REPOSITORY_URL>

cd ControleDeCustos

``

Otherwise, download and extract the files to a folder.

2. **Create a Virtual Environment (Recommended):**

``bash
python -m venv .venv

``

3. **Activate the Virtual Environment:**

* **Windows:**

``bash
.venv\Scripts\activate

``

* **macOS/Linux:**

``bash
source .venv/bin/activate

``

4. **Install Dependencies:**

With the virtual environment activated, install the necessary libraries:

``bash
pip install -r requirements.txt

``
The `requirements.txt` file should contain:

``
ttkbootstrap
pandas
matplotlib

``

## How to Run the Application

After following the configuration and installation steps:

1. **Activate your virtual environment** (if it is not already active).

2. **Navigate to the project's root folder** (where `main.py` is located).

3. **Run the main file:**

``bash
python main.py
```

A login window will appear. Use `admin` as the username and `admin` as the password to log in.

## Data Structure

Application data is stored in local files for simplicity:

* `data/lancamentos.csv`: Contains all income and expense records.

* `data/*.json`: JSON files (`empresas.json`, `categorias.json`, etc.) store the lookup data for the selection fields.

## Customization (Optional)

* **Change the Theme:** In the `main.py` file, you can change the application's theme by altering the `themename` parameter in the line `root = ttk.Window(themename="litera")`. Explore the themes available in `ttkbootstrap` (e.g., "darkly", "superhero").
* **Adjusting Fonts:** In `main.py`, right below the theme definition, you can configure the font size and style for the widgets using `ttk.Style().configure()`. For example:

``python
style = ttk.Style()
style.configure('TLabel', font=('Segoe UI', 11, 'bold'))
style.configure('TButton', font=('Segoe UI', 11, 'bold'))

# ... and other widgets
``
* **Financial Summary Colors:** The green and red colors for income, expenses, and balance are configured in `app/ui/app_principal.py` within the `update_financial_summary` method.

## Troubleshooting Common Problems

* **Date Format Error on Startup (`ValueError: time data "XX/XX/XXXX" doesn't match format "%m/%d/%Y"`)**:

This error occurs when the `lancamentos.csv` file has dates in the format `DD/MM/YYYY` and `pandas` expects `MM/DD/YYYY`.

**Solution:** In the `app/core/data_manager.py` file, in the `load_all_data` function, change the line that converts the 'Data' column to datetime, adding `dayfirst=True`:

``python
self.df_lancamentos['Data'] = pd.to_datetime(self.df_lancamentos['Data'], dayfirst=True)

``

* **Error `AttributeError: 'AppPrincipal' object has no attribute 'reset_filters'`**:

This indicates that the `reset_filters` method is missing in the `AppPrincipal` class.

**Solution:** Add the `reset_filters` method to the `AppPrincipal` class in `app/ui/app_principal.py`, as per the instructions provided previously.

**Error `AttributeError: 'DateEntry' object has no attribute 'set_date'`:

This error occurs because the `DateEntry` of `ttkbootstrap` does not use `set_date`.

**Solution:** In `app/ui/app_principal.py`, in the `reset_filters` method,
