from flask import Flask, jsonify, request, make_response
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import re
import pandas as pd
from io import BytesIO
import io
from datetime import datetime, timedelta


app = Flask(__name__)
CORS(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Vaerdia2023'
app.config['MYSQL_DB'] = 'classifier'
mysql = MySQL(app)


@app.route('/')
@cross_origin()
def Home():
    return "Home"


@app.route('/files', methods=['POST'])
@cross_origin()
def create_files():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({'message': 'Invalid data format. Expected a list of objects.'})

    cur = mysql.connection.cursor()

    for file_data in data:
        path = file_data['path']
        date = file_data['date']
        name = file_data['name']
        adresse = file_data['adresse']
        societe = file_data['societe']

        if file_data.get('categorie') == '':
            categorie = 'inconnue'
        else:
            categorie = file_data['categorie']
        phone_number = ''
        reName = re.sub(r"[^a-zA-ZÀ-ÿ]", "", name)
        if file_data.get('phone') == '':
            phone_query = f"SELECT phone_number FROM clients WHERE name = '{reName}'"
            cur.execute(phone_query)
            result = cur.fetchone()
            if result:
                phone_number = result[0]
        else:
            phone_number = file_data['phone']

        cur.execute(
            "SELECT id FROM file WHERE path=%s AND date=%s", (path, date))
        existing_file = cur.fetchone()

        if existing_file:

            continue
        cur.execute(
            "INSERT INTO file (path, date, name, adresse, societe, categorie,phone_number) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (path, date, name, adresse, societe, categorie, phone_number)
        )
        mysql.connection.commit()

    cur.close()

    return jsonify({'message': 'Files created successfully'})


@app.route('/new-execution', methods=['GET'])
@cross_origin()
def setNewHistory():
    cur = mysql.connection.cursor()
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(today)
    cur.execute(
        "INSERT INTO history (date) VALUES (%s)",
        [today]
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Files created successfully'})


@app.route('/latest-execution', methods=['GET'])
@cross_origin()
def getLatestExecution():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM history ORDER BY date DESC LIMIT 1"
    )
    row = cur.fetchone()
    cur.close()

    if row is None:
        return jsonify({'message': 'No execution history found'}), 404

    execution = {
        'date': row[1].strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify(execution)


@app.route('/files', methods=['GET'])
@cross_origin()
def get_files():
    search_query = request.args.get('query')
    search_categorie = request.args.get('categorie')
    search_societe = request.args.get('societe')
    excel = request.args.get('excel')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    # Get the page number, defaulting to 1 if not provided
    page = request.args.get('page', default=1, type=int)
    # Get the number of items per page, defaulting to 10 if not provided
    per_page = request.args.get('per_page', default=10, type=int)

    cur = mysql.connection.cursor()

    # Global Search
    query = "SELECT * FROM file WHERE 1=1"
    if not excel:
        query += " AND excel = 0"

    params = []

    if search_query:
        query += " AND (path LIKE %s OR name LIKE %s OR adresse LIKE %s OR societe LIKE %s OR categorie LIKE %s or phone_number LIKE %s)"
        params.extend(['%{}%'.format(search_query)] * 7)

    # Categorie Filter
    if search_categorie:
        query += " AND categorie = %s"
        params.append(search_categorie)

    # Societe Filter
    if search_societe:
        query += " AND societe = %s"
        params.append(search_societe)

    if start_date and end_date:
        start_date_obj = datetime.strptime(start_date, '%m-%d-%Y')
        end_date_obj = datetime.strptime(end_date, '%m-%d-%Y')
        # Add one day to end_date
        end_date_obj += timedelta(days=1)
        # Format start_date and end_date to string
        start_date_str = start_date_obj.strftime('%Y-%m-%d %H:%M:%S')
        end_date_str = end_date_obj.strftime('%Y-%m-%d %H:%M:%S')
        query += " AND date BETWEEN %s AND %s"
        params.extend([start_date_str, end_date_str])
    # Get the total count of rows matching the query
    cur.execute(query, params)
    total_count = cur.rowcount

    # Apply pagination to the query
    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, (page - 1) * per_page])

    # Execute the modified query
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()

    files = []
    for row in rows:
        # Convert string to datetime
        # date = datetime.strptime(row[2], '%m/%d/%Y %H:%M')
        formatted_date = ''
        if row[2]:
            formatted_date = row[2].strftime('%d-%m-%Y %H:%M:%S')
        file = {
            'path': row[1],
            'date': formatted_date,
            'name': row[3],
            'adresse': row[4],
            'societe': row[5],
            'categorie': row[6],
            'phone_number': row[7]
        }
        files.append(file)
    if (not rows):
        total_count = 0
        page = 1
        per_page = 0
    response = {
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'data': files
    }

    return jsonify(response)


@app.route('/files/exportsheet', methods=['GET'])
@cross_origin()
def export_sheet():
    search_query = request.args.get('query')
    search_categorie = request.args.get('categorie')
    search_societe = request.args.get('societe')
    cur = mysql.connection.cursor()

    # Global Search
    query = "SELECT * FROM file WHERE 1=1 AND excel = 0"

    params = []

    if search_query:
        query += " AND (path LIKE %s OR date LIKE %s OR name LIKE %s OR adresse LIKE %s OR societe LIKE %s OR categorie LIKE %s or phone_number LIKE %s)"
        params.extend(['%{}%'.format(search_query)] * 7)

    # Categorie Filter
    if search_categorie:
        query += " AND categorie = %s"
        params.append(search_categorie)

    # Societe Filter
    if search_societe:
        query += " AND societe = %s"
        params.append(search_societe)

    # Get the rows matching the query
    cur.execute(query, params)
    rows = cur.fetchall()

    files = []
    for row in rows:
        file = {
            'path': row[1],
            'date': row[2],
            'name': row[3],
            'adresse': row[4],
            'societe': row[5],
            'categorie': row[6],
            'phone_number': row[7]
        }
        files.append(file)

    # Convert the files list to a pandas DataFrame
    df = pd.DataFrame(files)

    # Save the DataFrame to an in-memory Excel file
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)  # Move the file pointer to the beginning of the file

    # Create a Flask response with the Excel file
    response = make_response(excel_file.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=files_export.xlsx'
    query = "UPDATE file SET excel = 1 WHERE 1=1 AND excel = 0"
    params = []

    if search_query:
        query += " AND (path LIKE %s OR date LIKE %s OR name LIKE %s OR adresse LIKE %s OR societe LIKE %s OR categorie LIKE %s or phone_number LIKE %s)"
        params.extend(['%{}%'.format(search_query)] * 7)

    # Categorie Filter
    if search_categorie:
        query += " AND categorie = %s"
        params.append(search_categorie)

    # Societe Filter
    if search_societe:
        query += " AND societe = %s"
        params.append(search_societe)
    cur.execute(query, params)
    cur.close()
    return response


@app.route('/categories', methods=['GET'])
@cross_origin()
def get_categories():
    cur = mysql.connection.cursor()
    cur.execute("SELECT categorie FROM file")
    rows = cur.fetchall()
    cur.close()

    categories = set()

    for row in rows:
        categories.add(row[0])

    return jsonify(list(categories))


@app.route('/societes', methods=['GET'])
@cross_origin()
def get_societes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT societe FROM file")
    rows = cur.fetchall()
    cur.close()

    societes = set()

    for row in rows:
        societes.add(row[0])

    return jsonify(list(societes))


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
