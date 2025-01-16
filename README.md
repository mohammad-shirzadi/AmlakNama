# AmlakNama

AmlakNama is a tool for analyzing and visualizing the economic value of real estate and land across different districts of Tehran.



## Features

Economic value visualization for properties across Tehran’s districts and neighborhoods.
Categorization of data by property type (residential, commercial, land).
Separate insights for purchase/sale and rental/lease options.
Interactive map for data visualization and price comparison.

### 1. **Data Collection**
- Utilizes **Selenium** and **BeautifulSoup** to scrape real estate listings from websites (e.g., Divar).
- Captures key details such as:
  - Property type (residential, commercial, land, etc.)
  - Price, area, year of construction
  - Geographic coordinates (latitude, longitude)
  - Additional metadata (e.g., location description, link to the original listing).

### 2. **Data Storage**
- Stores collected data in an **PostgereSQL(postgis) database** for easy access and analysis.
- Includes mechanisms to prevent duplicate entries and maintain data integrity.

### 3. **Data Analysis and Visualization**
- Uses **GeoPandas** and **Shapely** to analyze property data spatially.
- Generates interactive maps using property data and overlays regional boundaries.
- Supports filtering by:
  - Property type (buy/rent, residential/commercial)
  - Region
- Outputs visualizations as interactive HTML maps.

## ScreenShots

![image](https://github.com/user-attachments/assets/e0b2b0eb-e78d-4d14-806d-1ddabd66f907)


## Prerequisites

Languages and Frameworks: Python, Django, HTML, CSS, JavaScript

Libraries and Tools: Pandas, GeoPandas, NumPy, Folium, Selenium, BeautifulSoup


## Installation

Follow these steps to set up and run the AmlakNama System:

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

### Project Objective

The goal of this project is to leverage open data to analyze the economic value of real estate in Tehran, helping users make informed decisions about buying, selling, renting, or leasing properties.

- **Admins**: Manage all property listings, users, and system settings.
- **Property Owners**: List and manage properties.
- **Buyers**: Browse and search for properties. 

## Current Status

The project is in its early development phase. Data has been collected from online sources, with the potential to integrate official datasets in the future.

## Contributing

This repository is open to contributions. To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push the branch.
4. Submit a pull request with a description of your changes.


## License

This project is licensed under the MIT License. For more details, please refer to the LICENSE file.
