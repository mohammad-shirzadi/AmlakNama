# Real Estate Management System

This project is a comprehensive Real Estate Management System built using Django. It enables users to list properties, manage their listings, and search for properties based on various criteria. The system is designed to provide a seamless experience for both property managers and buyers.

## Features

### 1. **Data Collection**
- Utilizes **Selenium** and **BeautifulSoup** to scrape real estate listings from websites (e.g., Divar).
- Captures key details such as:
  - Property type (residential, commercial, land, etc.)
  - Price, area, year of construction
  - Geographic coordinates (latitude, longitude)
  - Additional metadata (e.g., location description, link to the original listing).

### 2. **Data Storage**
- Stores collected data in an **SQLite database** for easy access and analysis.
- Includes mechanisms to prevent duplicate entries and maintain data integrity.

### 3. **Data Analysis and Visualization**
- Uses **GeoPandas** and **Shapely** to analyze property data spatially.
- Generates interactive maps using property data and overlays regional boundaries.
- Supports filtering by:
  - Property type (buy/rent, residential/commercial)
  - Region
- Outputs visualizations as interactive HTML maps.


## Prerequisites

- Python 3.x
- Django 3.x or later

## Installation

Follow these steps to set up and run the Real Estate Management System:

1. Clone the repository:
   ```bash
   git clone https://github.com/mohammad-shirzadi/AmlakNama.git
   ```

2. Navigate to the project directory:
   ```bash
   cd AmlakNama
   ```

3. Create a virtual environment:
   ```bash
   python -m venv env
   ```

4. Activate the virtual environment:
   - On Windows:
     ```bash
     env\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source env/bin/activate
     ```

5. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. Open `http:/localhost:8000/` in your browser to access the application.

## Usage

- **Admins**: Manage all property listings, users, and system settings.
- **Property Owners**: List and manage properties.
- **Buyers**: Browse and search for properties.

## Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push the branch.
4. Submit a pull request with a description of your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
