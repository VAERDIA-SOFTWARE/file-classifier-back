from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin

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
            

        cur.execute("SELECT id FROM file WHERE path=%s AND date=%s", (path, date))
        existing_file = cur.fetchone()

        if existing_file:
            
            continue  

        
        cur.execute(
            "INSERT INTO file (path, date, name, adresse, societe, categorie) VALUES (%s, %s, %s, %s, %s, %s)",
            (path, date, name, adresse, societe, categorie)
        )
        mysql.connection.commit()

    cur.close()

    return jsonify({'message': 'Files created successfully'})


@app.route('/files', methods=['GET'])
@cross_origin()
def get_files():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM file")
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
            'categorie': row[6]
        }
        files.append(file)

    return jsonify(files)

if __name__ == '__main__':
    app.run()