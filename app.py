from flask import Flask, request, render_template, url_for, redirect
from db import get_tables, get_table_content, delete_table, delete_row, add_row, add_table
import os


app = Flask(__name__)


# Home Page
@app.route("/", methods=["GET", "POST"])
def get_home():
    if request.method == "GET":
        files = os.listdir("./db")
        return  render_template("index.html", dbFiles=files)
    else:
        return "Method not allowed", 405
    

@app.route("/upload", methods=["POST"])
def uploadFile():
    UPLOAD_FOLDER = "./db"
    if request.method == "POST":
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        if "fileInput" not in request.files:
            return "No file part"
        
        file = request.files["fileInput"]
        existFiles = os.listdir("./db")

        if file.filename == "":
            return "No Selected Files"
        elif file.filename in existFiles:
            return "There is already a file uploded with the same name, please change your file name or upload another one"
        if file and file.filename.endswith(".db"):
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
            return redirect(url_for('get_home'))
        else:
            return "Invalid File Format. Please Upload a .db File"        
    else:
        return "Method not allowed", 405


@app.route("/delete", methods=["POST"])
def delete_db_file():
    if request.method == "POST":
        file_name = request.form['file']
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "db", file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
        return redirect(url_for('get_home'))
    else:
        return "Method not allowed", 405

# Table Functions
@app.route("/<db_name>/table", methods=["GET", "POST", "DELETE"])
def show_table(db_name):
    if request.method == "GET":
        page = int (request.args.get("page",1))
        tables, total_count = get_tables(db_name, 1)
        if tables == "":
            return "Couldn't connect to db. Please be sure the db is exist"
        total_pages = (total_count + 49) // 50
        if(page < 1):
            page = 1
        elif(page > total_pages):
            page = total_pages
        tables, total_count = get_tables(db_name, page=1)
        return render_template("show-tables.html", tables=tables, db_name=db_name, total_pages=total_pages, curr_page=page)
    elif request.method == "POST":
        table_name = request.form.get("table_name")
        columns = request.form.get("columns").split(",")
        add_table(db_name, table_name, columns)
        return ''
    elif request.method == "DELETE":
        table_name = request.form['table_name']  
        delete_table(db_name=db_name, table_name=table_name)
        return ''
    else:
        return "Method not allowed", 405


@app.route("/<db_name>/table/<table_name>", methods=["GET", "POST"])
def show_table_content(db_name, table_name):
    if request.method == "GET":
        page = int (request.args.get("page",1))
        table_content, total_count, columns = get_table_content(table_name=table_name, db_name=db_name, page=1)
        if table_content == "":
            return "Couldn't connect to db. Please be sure the db is exist"
        total_pages = (total_count + 49) // 50 if total_count > 0 else 1
        if(page < 1):
            page = 1
        elif(page > total_pages):
            page = total_pages
        table_content, total_count, columns = get_table_content(table_name=table_name, db_name=db_name, page=page)
        return render_template("table-content.html", table_content = table_content, columns=columns, db_name=db_name, table_name=table_name, total_pages=total_pages, curr_page=page)
    elif request.method == "POST":
        row_data = request.form.to_dict()
        add_row(db_name=db_name, table_name=table_name, row_data=row_data)
        return redirect(url_for("show_table_content",db_name=db_name, table_name=table_name))
    else:
        return "Method not allowed", 405

@app.route("/delete/<db_name>/<table_name>/row", methods=["POST"])
def delete_table_row(db_name, table_name):
    row_data = request.form.to_dict()
    delete_row(db_name=db_name, table_name=table_name, row_data=row_data)
    return redirect(url_for("show_table_content",db_name=db_name, table_name=table_name))