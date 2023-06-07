import io
from flask import Flask, jsonify, request, send_file
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import pandas as pd


app = Flask(__name__)
CORS(app)

app.config['MYSQL_HOST'] = 'localhost'  
app.config['MYSQL_USER'] = 'root'       
app.config['MYSQL_PASSWORD'] = ''  
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
            categorie = 'UNKNOWN'
        else:
            categorie = file_data['categorie']
            
        if file_data.get('phone_number') == '':
            phone_number = """SELECT phone_number FROM vicidial WHERE CONCAT(first_name, ' ', middle_name, ' ', last_name) = ( SELECT name FROM files )"""
            cur.execute("INSERT INTO file (phone_number) VALUES (%s)",(phone_number))
        else:
            phone_number = file_data['phone_number']
            
        cur.execute("SELECT id FROM file WHERE path=%s AND date=%s", (path, date))
        existing_file = cur.fetchone()

        if existing_file:
            
            continue  

        cur.execute(
            "INSERT INTO file (path, date, name, adresse, societe, categorie,phone_number) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (path, date, name, adresse, societe, categorie,phone_number)
        )
        mysql.connection.commit()

    cur.close()

    return jsonify({'message': 'Files created successfully'})


@app.route('/files', methods=['GET'])
@cross_origin()
def get_files():
    search_query = request.args.get('query')
    search_categorie = request.args.get('categorie')
    search_societe = request.args.get('societe')
    page = request.args.get('page', default=1, type=int)  # Get the page number, defaulting to 1 if not provided
    per_page = request.args.get('per_page', default=10, type=int)  # Get the number of items per page, defaulting to 10 if not provided

    cur = mysql.connection.cursor()

    # Global Search
    query = "SELECT * FROM file WHERE 1=1"  
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

    response = {
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'data': files
    }

    return jsonify(response)

from io import BytesIO

from io import BytesIO
from flask import make_response

@app.route('/files/exportsheet', methods=['GET'])
@cross_origin()
def export_sheet():
    search_query = request.args.get('query')
    search_categorie = request.args.get('categorie')
    search_societe = request.args.get('societe')

    cur = mysql.connection.cursor()

    # Global Search
    query = "SELECT * FROM file WHERE 1=1"  
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
    cur.close()

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
    app.run()