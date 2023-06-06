# Flask API Documentation

This is a Flask API that provides endpoints for managing files in a MySQL database. The API allows creating and retrieving files, along with their associated details such as path, date, name, address, company, and category.

## API Endpoints

- `GET /`: Home endpoint that returns a simple message indicating the home page.

- `POST /files`: Endpoint for creating files. It expects a JSON payload containing an array of file objects with properties such as path, date, name, address, company, and category.

- `GET /files`: Endpoint for retrieving a list of all files stored in the database.

## Installation and Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo-url.git

2. Install the required dependencies:

    ```python
    pip install -r requirements.txt

3. Configure the MySQL database connection in app.py:

    ```python
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'classifier'

    You can find sql Code to generate the data base in classifier.sql

4. Run the Flask application:

    ```bash
   python app.py

## Usage

- Make requests to the API endpoints using your preferred HTTP client (e.g., cURL, Postman).
- For creating files, send a POST request to /files with the file details in the request body as a JSON payload.
- To retrieve all files, send a GET request to /files.
  
## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.
