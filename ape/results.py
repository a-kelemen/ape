from __future__ import absolute_import, division, generators, print_function, unicode_literals


class Results:
	def __init__(self, process_id=-1, status="", log="", time="", elapsed=""):
		self.process_id = process_id
		self.status = status
		self.log = log
		self.time = time
		self.elapsed = elapsed
