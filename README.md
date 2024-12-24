# Real Estate Management System

This project is a comprehensive Real Estate Management System built using Django. It enables users to list properties, manage their listings, and search for properties based on various criteria. The system is designed to provide a seamless experience for both property managers and buyers.

## Features

- **Property Listings**: Add, update, and delete property details with complete information.
- **Advanced Search**: Search properties with filters like location, price range, and more.
- **User Authentication**: Secure login and registration for property managers and buyers.
- **Responsive Design**: Fully responsive interface for optimal use across devices.

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
