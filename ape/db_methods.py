from __future__ import absolute_import, division, generators, print_function, unicode_literals

import os
import sqlite3

from .results import Results


def get_max_run_id(process_id):
	conn = sqlite3.connect(r"ape/db/processes.db")
	cur = conn.cursor()
	cur.execute("SELECT MAX(RUN_ID) FROM PROCESS_RESULTS WHERE PROCESS_ID =" + str(process_id))
	max_id = cur.fetchall()[0][0]
	conn.close()
	if max_id is not None:
		return max_id
	else:
		return 0


def insert_process_result(results):
	run_id = get_max_run_id(results.process_id) + 1
	result_values = str(results.process_id) + ", " + str(run_id) + ", '" + results.status + "', '" + results.log + "', '" + results.time + "', '" + results.elapsed + "'"
	conn = sqlite3.connect(r"ape/db/processes.db")
	conn.execute("INSERT INTO PROCESS_RESULTS (PROCESS_ID, RUN_ID,STATUS,LOG,TIME,ELAPSED) \
	  VALUES (" + result_values + ")")
	conn.commit()
	conn.close()


def get_process_results(process_id):
	max_id = get_max_run_id(process_id)
	conn = sqlite3.connect(r"ape/db/processes.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM PROCESS_RESULTS WHERE PROCESS_ID=" + str(process_id) + " AND RUN_ID >" + str(max_id-5) + " ORDER BY RUN_ID DESC")
	last_processes = cur.fetchall()
	conn.close()
	return last_processes


def insert_new_process(insert_values):
	conn = sqlite3.connect(r"ape/db/processes.db")
	conn.execute("INSERT INTO PROCESSES (NAME,PATH,ADDED) \
	VALUES (" + insert_values + ")");
	conn.commit()
	conn.close()


def get_name_by_process_id(process_id):
	conn = sqlite3.connect(r"ape/db/processes.db")
	cur = conn.cursor()
	cur.execute("SELECT NAME FROM PROCESSES WHERE PROCESS_ID=" + str(process_id))
	process_name = cur.fetchall()[0][0]
	conn.close()
	if process_name is not None:
		return process_name
	else:
		# TODO exception
		return ""


def get_path_by_process_id(process_id):
	conn = sqlite3.connect(r"ape/db/processes.db")
	cur = conn.cursor()
	cur.execute("SELECT PATH FROM PROCESSES WHERE PROCESS_ID=" + str(process_id))
	process_path = cur.fetchall()[0][0]
	conn.close()
	if process_path is not None:
		return process_path
	else:
		# TODO exception
		return ""


def get_all_processes():
	conn = sqlite3.connect(r"ape/db/processes.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM PROCESSES")
	processes = cur.fetchall()
	conn.close()
	if processes is not None:
		return processes
	else:
		# TODO 
		return {}


def get_last_status(process_id):
	conn = sqlite3.connect(r"ape/db/processes.db")
	cur = conn.cursor()
	cur.execute("SELECT STATUS FROM PROCESS_RESULTS WHERE PROCESS_ID =" + str(process_id) + " ORDER BY RUN_ID DESC LIMIT 1")
	try:
		status = cur.fetchall()[0][0]
		conn.close()
		return status
	except IndexError:
		conn.close()
		return "N/A"


def get_last_run_date(process_id):
	conn = sqlite3.connect(r"ape/db/processes.db")
	cur = conn.cursor()
	cur.execute("SELECT TIME FROM PROCESS_RESULTS WHERE PROCESS_ID =" + str(process_id) + " ORDER BY RUN_ID DESC LIMIT 1")
	try:
		time = cur.fetchall()[0][0]
		conn.close()
		return time
	except IndexError:
		conn.close()
		return "N/A"


def get_last_passed(process_id):
	conn = sqlite3.connect(r"ape/db/processes.db")
	cur = conn.cursor()
	cur.execute("SELECT TIME FROM PROCESS_RESULTS WHERE PROCESS_ID =" + str(process_id) + " AND STATUS='PASS' ORDER BY RUN_ID DESC LIMIT 1")
	try:
		time = cur.fetchall()[0][0]
		conn.close()
		return time
	except IndexError:
		conn.close()
		return "N/A"


def get_add_date(process_id):
	conn = sqlite3.connect(r"ape/db/processes.db")
	cur = conn.cursor()
	cur.execute("SELECT ADDED FROM PROCESSES WHERE PROCESS_ID =" + str(process_id))
	try:
		time = cur.fetchall()[0][0]
		conn.close()
		return time
	except IndexError:
		conn.close()
		return "N/A"


def get_execution_count(process_id):
	conn = sqlite3.connect(r"ape/db/processes.db")
	cur = conn.cursor()
	cur.execute("SELECT COUNT(*) FROM PROCESS_RESULTS WHERE PROCESS_ID =" + str(process_id))
	try:
		count = cur.fetchall()[0][0]
		conn.close()
		return count
	except IndexError:
		conn.close()
		return 0


def get_pass_count(process_id):
	conn = sqlite3.connect(r"ape/db/processes.db")
	cur = conn.cursor()
	cur.execute("SELECT COUNT(*) FROM PROCESS_RESULTS WHERE PROCESS_ID =" + str(process_id) + " AND STATUS='PASS'")
	try:
		count = cur.fetchall()[0][0]
		conn.close()
		return count
	except IndexError:
		conn.close()
		return 0


def get_fail_count(process_id):
	conn = sqlite3.connect(r"ape/db/processes.db")
	cur = conn.cursor()
	cur.execute("SELECT COUNT(*) FROM PROCESS_RESULTS WHERE PROCESS_ID =" + str(process_id) + " AND STATUS='FAIL'")
	try:
		count = cur.fetchall()[0][0]
		conn.close()
		return count
	except IndexError:
		conn.close()
		return 0


def delete_process(process_id):
	conn = sqlite3.connect(r"ape/db/processes.db")
	conn.execute("DELETE FROM PROCESS_RESULTS WHERE PROCESS_ID=" + str(process_id));
	conn.commit()
	conn.execute("DELETE FROM PROCESSES WHERE PROCESS_ID=" + str(process_id));
	conn.commit()
	conn.close()


def change_name(process_id, new_name):
	conn = sqlite3.connect(r"ape/db/processes.db")
	conn.execute("UPDATE PROCESSES SET NAME = '" + new_name + "' WHERE PROCESS_ID=" + str(process_id));
	conn.commit()
	conn.close()


def change_path(process_id, new_path):
	conn = sqlite3.connect(r"ape/db/processes.db")
	conn.execute("UPDATE PROCESSES SET PATH = '" + new_path + "' WHERE PROCESS_ID=" + str(process_id));
	conn.commit()
	conn.close()


#
# conn = sqlite3.connect(r"ape/db/processes.db")
# conn.execute('''DROP TABLE IF EXISTS PROCESS_RESULTS''')
# conn.execute('''CREATE TABLE PROCESS_RESULTS
# 	 (PROCESS_ID    INTEGER  NOT NULL,
# 	 RUN_ID         INTEGER  NOT NULL,
# 	 STATUS         VARCHAR(255)      NOT NULL,
# 	 LOG            VARCHAR(255),
# 	 TIME           VARCHAR(255)      NOT NULL,
# 	 ELAPSED        VARCHAR(255)      NOT NULL,
# 	 PRIMARY KEY (PROCESS_ID, RUN_ID));''')
#
#
# # # CREATING   Prosecces
# conn.execute('''DROP TABLE IF EXISTS PROCESSES''')
# conn.execute('''CREATE TABLE PROCESSES
# 	 (PROCESS_ID INTEGER   PRIMARY KEY  AUTOINCREMENT,
# 	 NAME         VARCHAR(255)    NOT NULL,
# 	 PATH         VARCHAR(255)    NOT NULL,
# 	 ADDED        VARCHAR(255)    NOT NULL);''')
#
#



# proc_val_1 = "'" + "a.txt" + "', '" + "C:\\szakdoga\\ape\\a.txt" + "', '" + "2019.04.10 12:39" + "'"
# insert_new_process(proc_val_1)
# proc_val_2 = "'" + "b.txt" + "', '" + "C:\\szakdoga\\ape\\b.txt" + "', '" + "2019.04.10 13:23" + "'"
# insert_new_process(proc_val_2)
# proc_val_3 = "'" + "flaskrobot" + "', '" + "C:\\szakdoga\\processes\\flaskrobot.robot" + "', '" + "2019.04.12 14:10" + "'"
# insert_new_process(proc_val_3)
# m1 = Results(process_id=1, status="PASS", log="C:\\log\\log.html", time="2019.04.10 12:39:12", elapsed="4,7")
# insert_process_result(m1)
# m2 = Results(process_id=2, status="PASS", log="C:\\log\\log.html", time="2019.04.11 12:00:43", elapsed="0,3")
# insert_process_result(m2)
# m3 = Results(process_id=1, status="PASS", log="C:\\log\\log.html", time="2019.04.12 12:01:31", elapsed="2")
# insert_process_result(m3)
# name = get_name_by_process_id(1)
# print("NAME: "+ name)
# name = get_name_by_process_id(2)
# print("NAME: "+ name)
# change_name(2,"new_namehaha")
# change_path(2,"new_pat ez asd /sda ")
# print(get_pass_count(1) == 2)
# print(get_fail_count(1) == 0)
# print(get_add_date(1) == "2019.04.10 12:39")
# print(get_last_passed(1) == "2019.04.12 12:01")
# conn.close()