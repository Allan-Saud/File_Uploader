from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import UploadedFile
import pandas as pd
import sqlite3
import os


def handle_uploaded_file(uploaded_file):
    file_path = uploaded_file.file.path  # file must be saved before this
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    print(f"Uploaded file extension: {ext}")  # Debug print

    if ext == '.pdf':
        return {'type': 'pdf', 'path': uploaded_file.file.url}
    
    elif ext in ['.xlsx', '.xls']:
        if ext == '.xlsx':
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            df = pd.read_excel(file_path, engine='xlrd')
        return {'type': 'excel', 'data': df.to_html(classes='table table-bordered', index=False)}
    
    elif ext == '.csv':
        df = pd.read_csv(file_path)
        return {'type': 'csv', 'data': df.to_html(classes='table table-bordered', index=False)}

    elif ext == '.db':
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        data = {}

        for table_name_tuple in tables:
            table_name = table_name_tuple[0]

            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [info[1] for info in cursor.fetchall()]
            columns_str = ", ".join(columns)

            df = pd.read_sql_query(f"SELECT {columns_str} FROM {table_name} LIMIT 10", conn)

            data[table_name] = df.to_html(classes='table table-bordered', index=False)

        conn.close()
        return {'type': 'db', 'data': data}


def upload_file(request):
    context = {}
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)

            filename = uploaded_file.file.name
            ext = os.path.splitext(filename)[1].lower()

            if ext == '.pdf':
                uploaded_file.file_type = 'pdf'
            elif ext in ['.xlsx', '.xls']:
                uploaded_file.file_type = 'excel'
            elif ext == '.csv':
                uploaded_file.file_type = 'csv'
            elif ext == '.db':
                uploaded_file.file_type = 'db'
            else:
                uploaded_file.file_type = 'unknown'

            uploaded_file.save()  # ✅ Save first so uploaded_file.file.path is available

            context['uploaded_info'] = handle_uploaded_file(uploaded_file)  # now safe to read
    else:
        form = UploadFileForm()

    context['form'] = form
    return render(request, 'uploads/upload.html', context)
