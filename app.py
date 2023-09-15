import json
import mysql.connector as sql
import numpy as np
import warnings
import math
warnings.filterwarnings("ignore")
import warnings
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import mysql.connector
import pandas as pd
warnings.filterwarnings("ignore")
application = Flask(__name__)
def get_db_connection():
    return mysql.connector.connect(
        host='database-1.cbjabnlglbz6.ap-south-1.rds.amazonaws.com',
        database='vehicledb1',
        user='admin',
        password='ingo1234',
        auth_plugin='mysql_native_password'
)
@application.route('/', methods=['POST', 'GET'])
def login1():
    return render_template('dashboard.html',)
@application.route("/dashboard", methods=["GET", "POST"])
def get_odo():
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    cursor.execute("SHOW TABLES")
    table_names = [table[0] for table in cursor.fetchall()]
    return render_template("index.html", table_names=table_names, c1result=None)
@application.route("/dashboard1", methods=["GET", "POST"])
def get_odo1():
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    cursor.execute("SHOW TABLES")
    table_names = [table[0] for table in cursor.fetchall()]
    return render_template("index1.html", table_names=table_names, c1result=None)
@application.route("/range", methods=["POST", "GET"])
def range():
    if request.method == "POST":
        start_date = request.form['start']
        end_date = request.form['end']
        selected_table = request.form.get('table_name')
        db_connection = get_db_connection()
        cur = db_connection.cursor()
        cursor = db_connection.cursor()
        cursor.execute("SHOW TABLES")
        table_names = [table[0] for table in cursor.fetchall()]
        alltables = table_names
        results = []
        my=[]
        for total in alltables:
            query = "SELECT * FROM {} WHERE date_time BETWEEN %s AND %s".format(total)
            cur.execute(query, (start_date, end_date))
            table_data = cur.fetchall()
            dfu = pd.DataFrame(table_data)
            dfu.columns = ['Vehicle', 'IGN', 'Battery %', 'External Voltage', "Location", "Speed","Last Distance (meters)", "Distance", "History Data", "No Of Satellite", "Coordinates","date_time"]
            dfv= dfu[(dfu['IGN'] == 'ON')]
            dfm = dfv.groupby(dfv.date_time.dt.date)['Last Distance (meters)'].sum()
            result = dfm.sum() / len(dfm) * 0.001
            formatted_num = "{:.2f}".format(result)
            results.append((result, total))
            filtered_data = [(value, label) for value, label in results if not math.isnan(value)]

            filtered_data.sort(reverse=True)
            top_3_results = filtered_data[:5]
            data = [
                {"data": item[0], "label": item[1]} for item in top_3_results
            ]
            json_data = json.dumps(data)
        if selected_table == "all":
            cursor = db_connection.cursor()
            cursor.execute("SHOW TABLES")
            selected_tables = [table[0] for table in cursor.fetchall()]
        else:
            selected_tables = [selected_table]
        total_sum = 0
        id_count = 0
        counts = []
        individual_results = []
        for table in selected_tables:
            query = "SELECT * FROM {} WHERE date_time BETWEEN %s AND %s".format(table)
            cur.execute(query, (start_date, end_date))
            table_data = cur.fetchall()
            df = pd.DataFrame(table_data)
            df.columns = ['Vehicle', 'IGN', 'Battery %', 'External Voltage', "Location", "Speed","Last Distance (meters)", "Distance", "History Data", "No Of Satellite", "Coordinates","date_time"]
            dfk = pd.DataFrame(table_data)
            dfo = pd.DataFrame(table_data)
            dfh = pd.DataFrame(table_data)
            dfk.columns = ['Vehicle', 'IGN', 'Battery %', 'External Voltage', "Location", "Speed","Last Distance (meters)", "Distance", "History Data", "No Of Satellite", "Coordinates","date_time"]
            dfo.columns = ['Vehicle', 'IGN', 'Battery %', 'External Voltage', "Location", "Speed","Last Distance (meters)", "Distance", "History Data", "No Of Satellite", "Coordinates","date_time"]
            dfh.columns = ['Vehicle', 'IGN', 'Battery %', 'External Voltage', "Location", "Speed","Last Distance (meters)", "Distance", "History Data", "No Of Satellite", "Coordinates","date_time"]
            dfk = dfk[(dfk['IGN'] == 'ON')]
            df3 = dfk.groupby(dfk.date_time.dt.date)['Last Distance (meters)'].sum()
            result = df3.sum() / len(df3) * 0.001
            formatted_num = "{:.2f}".format(result)
            total_sum += result
            individual_results.append(result)
            counts.append((id_count, table))
            cycle_count = 0
            previous_state = None
            for i, row in dfo.iterrows():
                current_state = row["IGN"]
                if previous_state == "ON" and current_state == "OFF":
                    cycle_count += 1
                previous_state = current_state
            cycle_count1 = 0
            previous_state1 = None
            for i, row in dfo.iterrows():
                current_state1 = row["IGN"]
                if previous_state1 == "OFF" and current_state1 == "ON":
                    cycle_count1 += 1
                previous_state1 = current_state1
            df7 = dfh[dfh['Speed'] != 0]

            grouped = df7.groupby(df7.date_time.dt.date)
            dfn = dfh[dfh['Speed'] <= 35]
            grouped1 = dfn.groupby(dfn.date_time.dt.date)
            top_speed = grouped1["Speed"].max()
            avg_speed = grouped["Speed"].mean()
            df_json = avg_speed.to_json(date_format='iso')
            df1_json = top_speed.to_json(date_format="iso")
            dfo['Time'] = pd.to_datetime(dfo['date_time'], format='%d-%m-%Y %H:%M:%S')
            dfo['Date'] = dfo['Time'].dt.date
            dfo['Time'] = dfo['Time'].dt.time
            dfo['Time'] = pd.to_datetime(dfo.Time, format='%H:%M:%S')
            dfo['Weekday'] = dfo['Time'].dt.strftime('%A')
            dfo['Date'] = dfo['Time'].dt.strftime('%Y-%m-%d')  # Convert date to YYYY-MM-DD format
            dfo['Time'] = pd.to_datetime(dfo['Time'], format='%d-%m-%Y %H:%M:%S')
            dfo['Time'] = dfo['Time'].dt.strftime('%H:00')
            dfo["Last Distance (meters)"] = dfo["Last Distance (meters)"] * 0.001
            dfo['Date_Weekday'] = dfo['Date'].astype(str) + ' (' + dfo['Weekday'] + ')'
            pivot_table = dfo.pivot_table(values='Last Distance (meters)', index='Date_Weekday', columns='Time', aggfunc='sum')
            pivot_table_json = pivot_table.to_json(orient='columns')
            print(pivot_table_json)
        return jsonify({'htmlresponse': render_template('odo.html',data=df_json,data1=df1_json, c1result=formatted_num,count_result=id_count,cycle_count=cycle_count,cycle_count1=cycle_count1,id_count=id_count,json_data=json_data,pivot_table_json=pivot_table_json)})
@application.route("/count", methods=["POST"])
def count():
    if request.method == "POST":
            start_date = request.form['start']
            end_date = request.form['end']
            selected_table = request.form.get('table_name')
            db_connection = get_db_connection()
            cur = db_connection.cursor()
            cursor = db_connection.cursor()
            cursor.execute("SHOW TABLES")
            table_names = [table[0] for table in cursor.fetchall()]
            alltables = table_names
            results = []
            for total in alltables:
                query = "SELECT * FROM {} WHERE date_time BETWEEN %s AND %s".format(total)
                cur.execute(query, (start_date, end_date))
                table_data = cur.fetchall()
                df = pd.DataFrame(table_data)
                df.columns = ['Vehicle', 'IGN', 'Battery %', 'External Voltage', "Location", "Speed","Last Distance (meters)", "Distance", "History Data", "No Of Satellite", "Coordinates","date_time"]
                op_col = []
                for i in df['Speed']:
                    op_col.append(i)
                np.set_printoptions(threshold=np.inf)
                lower_limit = int(request.form.get('lower_limit', 0))
                upper_limit1 = int(request.form.get('upper_limit1', 0))
                upper_limit2 = int(request.form.get('upper_limit2', 0))
                x = np.array(op_col)
                x1 = x.astype('int32')
                sub_lists = np.split(x1, np.where(np.diff(x1) < 0)[0] + 1)
                id_count = 0
                for unit in sub_lists:
                    if min(unit) <= lower_limit and max(unit) > upper_limit1 and max(unit) < upper_limit2 and len(
                            set(unit)) > 1:
                        id_count += 1
                results.append((id_count, total))
                results.sort(reverse=True)
                top_3_results = results[:3]
                data = [
                    {"data": item[0], "label": item[1]} for item in top_3_results
                ]
                json_data1 = json.dumps(data)
            return jsonify({'htmlresponse': render_template('acceleration.html', id_count=id_count, results=results,json_data1=json_data1)})

if __name__ == '__main__':
 application.run(debug=True, port="3217",threaded=True)