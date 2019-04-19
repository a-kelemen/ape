from __future__ import absolute_import, division, generators, print_function, unicode_literals

from flask import Flask, render_template, redirect, url_for, send_from_directory
from flask import request
import subprocess
import re
import datetime

import shutil
from shutil import copyfile
from collections import OrderedDict

from .db_methods import *

file_path = os.path.dirname(os.path.abspath(__file__))
workspace = os.path.join(os.path.dirname(file_path), "workspace")
app = Flask(__name__, template_folder='../templates', static_folder="../static")


@app.route('/')
def index():
	return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
	process_dict = all_processes_to_dict()
	return render_template('dashboard.html', msg="", processes=process_dict)


@app.route("/log/<name>/<nr>", methods=['POST'])
def log(name, nr):
	log_dir = os.path.join(workspace, name, nr)
	return send_from_directory(log_dir, "log.html")


@app.route('/delete/<process_id>', methods=['POST'])
def delete(process_id):
	if request.method == 'POST':
		process_name = get_name_by_process_id(process_id)
		delete_process(process_id)
		process_workspace = os.path.join("workspace", process_name)
		# DELETE WORKSPACE
		if os.path.isdir(process_workspace):
			shutil.rmtree(process_workspace)
			#print("Deleted: " + process_workspace)
	return redirect(url_for('dashboard'))


@app.route('/edit/<process_id>', methods=['POST', 'GET'])
def edit(process_id):
	if request.method == 'POST':
		if "edit" in request.form:
			process_path = request.form['path']
			process_name = request.form['name']
			if os.path.isfile(process_path):
				change_path(process_id, process_path)
			else:
				return render_template('edit.html', wrong_path=True)
			if process_name.strip() != "":
				change_name(process_id, process_name)
			process_dict = all_processes_to_dict()
			return render_template('dashboard.html', processes=process_dict)
		elif "delete" in request.form:
			process_name = get_name_by_process_id(process_id)
			delete_process(process_id)
			process_workspace = os.path.join("workspace", process_name)
			# DELETE WORKSPACE
			if os.path.isdir(process_workspace):
				shutil.rmtree(process_workspace)
			return redirect(url_for('dashboard'))
		if "dashboard" in request.form:
			return redirect(url_for('dashboard'))
	return render_template('edit.html', wrong_path=False)

	
@app.route('/run/<variable>', methods=['POST'])
def run(variable):
	if request.method == 'POST':
		start_time = datetime.datetime.now()
		process_path = get_path_by_process_id(variable)
		output = "-d " + workspace
		# TODO -- pybot
		run_command = "roboproc " + process_path
		print(run_command)
		output = subprocess.Popen(run_command , stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		output_msg = str(output.communicate())
		elapsed_time = datetime.datetime.now() - start_time
		elapsed_millisecs = round(elapsed_time.total_seconds(), 1)
		results = Results()
		results.process_id = variable
		if "PASS" in output_msg:
			status = "PASS"
			results.status="PASS"
		elif "FAIL" in output_msg:
			status = "FAIL"
			results.status = "FAIL"
		else:
			status = "ERROR"
			results.status = "ERROR"

		if "Log:" in output_msg:

			result = re.search('Log:(.*)html', output_msg)
			log_file = result.group(1).strip().replace("\\r\\n", "") + "html"
			process_name = get_name_by_process_id(variable)
			run_nr = get_max_run_id(variable) + 1
			if os.path.isfile(log_file):
				process_workspace = os.path.join(workspace, process_name, str(run_nr))
				if run_nr > 5:
					delete_workspace = os.path.join(workspace, process_name, str(run_nr-5))
					if os.path.isdir(delete_workspace):
						shutil.rmtree(delete_workspace, ignore_errors=True)
				new_log_path = os.path.join(process_workspace, "log.html") 
				if not os.path.isdir(process_workspace):
					os.makedirs(process_workspace)
				shutil.move(log_file, new_log_path)
				#ape_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
				#log_relative_path = os.path.join("..", "workspace", process_name, str(run_nr), "log.html")
				results.log = str(new_log_path)
		else:
			results.log = ""
		time = datetime.datetime.now().replace(microsecond=0)
		results.time = str(time)
		results.elapsed = str(elapsed_millisecs)
		insert_process_result(results)
		
	return redirect(url_for('dashboard'))
	#process_dict = all_processes_to_dict()
	#return render_template('dashboard.html', msg="", processes=process_dict)


@app.route('/results/<process_id>', methods=['GET'])
def results(process_id):
	result_dict = last_five_results_to_dict(process_id)
	stats = get_process_stats(process_id)
	return render_template('results.html', proc_dict=result_dict, proc_stats=stats)

	
def last_five_results_to_dict(process_id):
	results = get_process_results(process_id)
	result_dict = {}
	for i in results:
		pr_id, run_id, status, pr_log, time, elapsed = i
		result_dict[run_id] = {}
		result_dict[run_id]["name"] = get_name_by_process_id(process_id)
		result_dict[run_id]["status"] = status
		result_dict[run_id]["log"] = pr_log
		result_dict[run_id]["time"] = time
		result_dict[run_id]["elapsed"] = elapsed
	return OrderedDict(reversed(list(result_dict.items())))


def all_processes_to_dict():
	processes = get_all_processes()
	process_dict = {}
	for i in processes:
		process_id, name, path, added = i
		process_dict[process_id] = {}
		process_dict[process_id]["name"] = name
		process_dict[process_id]["path"] = path
		process_dict[process_id]["added"] = added
		process_dict[process_id]["last_status"] = get_last_status(process_id)
		process_dict[process_id]["last_run"] = get_last_run_date(process_id)
		exec_num = get_execution_count(process_id)
		pass_num = get_pass_count(process_id)
		if exec_num != 0:
			rate = str(int(round(pass_num/exec_num * 100))) + "%"
		else:
			rate = "N/A"
		process_dict[process_id]["pass_rate"] = rate
		
	return process_dict


def get_process_stats(process_id):
	stats = {}
	stats["added"] = get_add_date(process_id)
	stats["path"] = get_path_by_process_id(process_id)
	stats["proc_name"] = get_name_by_process_id(process_id)
	stats["executed_num"] = get_execution_count(process_id)
	stats["pass_num"] = get_pass_count(process_id)
	stats["fail_num"] = get_fail_count(process_id)
	stats["last_run"] = get_last_run_date(process_id)
	stats["last_passed"] = get_last_passed(process_id)
	stats["last_status"] = get_last_status(process_id)
	#print(stats)
	return stats


# @app.route('/upload', methods=['GET', 'POST'])
# def upload():
# 	if request.method == 'POST':
# 		file_path = request.form['text']
# 		print(file_path)
# 		if os.path.isfile(file_path):
# 			file_name = os.path.splitext(os.path.basename(file_path))[0]
# 			time_added = datetime.datetime.now()
# 			time_added = time_added.strftime('%Y-%m-%d %H:%M')
# 			#time_added = datetime.datetime.strptime(datetime.datetime.now(), '%Y-%m-%d %H:%M')
# 			insert_new_process("'" + file_name + "', '" + file_path + "', '" + str(time_added) + "'")
# 			# TODO kulon "a feltoltes sikeres, back" oldal
# 			process_dict = all_processes_to_dict()
#
# 			return render_template('dashboard.html', msg="Sikeres feltoltes", processes=process_dict)
# 		else:
# 			return render_template('upload.html', msg=":(")
# 	return render_template('upload.html', msg="")
#

@app.route('/new', methods=['GET', 'POST'])
def new():
	if request.method == 'POST':
		time_added = datetime.datetime.now()
		time_added = time_added.strftime('%Y-%m-%d %H:%M')
		#time_added = datetime.datetime.strptime(datetime.datetime.now(), '%Y-%m-%d %H:%M')
		process_name = "Process_" + datetime.datetime.now().strftime('%m%d%H%M%S%f')[:-3]
		process_path = "Please set path before run!"
		insert_new_process("'" + process_name + "', '" + process_path + "', '" + str(time_added) + "'")
	process_dict = all_processes_to_dict()
	return render_template('dashboard.html', processes=process_dict)


if __name__ == "__main__":
	app.run()