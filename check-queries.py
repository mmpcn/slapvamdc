#!/usr/bin/python3
"""
This script extracts the example queries from LineTAP.tex and runs them
against the dc.g-vo.org server using pyVO.

This works by looking for comments including 
please-run-a[-lenient]-test and fetching the next lstlisting environment.

A lenient test here is one that may return empty.
"""

import sys

import pyvo


class ExampleCollector:
	def __init__(self):
		self.state, self.cur_query = "sleeping", []

	def feed(self, line):
		return getattr(self, "_exec_"+self.state)(line)

	def _exec_sleeping(self, line):
		if "please-run-a-test" in line:
			self.opener = line
			self.state = "hunting"

	def _exec_hunting(self, line):
		if "\\begin{lstlisting}" in line:
			self.state = "collecting"
	
	def _exec_collecting(self, line):
		if "\\end{lstlisting}" in line:
			query = "".join(self.cur_query)
			self.state, self.cur_query = "sleeping", []
			if "-lenient" in self.opener:
				return "lenient", query
			else:
				return "strict", query
		else:
			self.cur_query.append(line)


def iter_examples(src_name):
	coll = ExampleCollector()
	with open(src_name, encoding="utf-8") as f:
		for ln in f:
			val = coll.feed(ln)
			if val:
				yield val


def main():
	failures = 0
	svc = pyvo.dal.TAPService("http://dc.g-vo.org/tap")
	for mode, query in iter_examples("LineTAP.tex"):
		try:
			res = svc.run_sync(query)
			if mode=="strict":
				assert len(res)>0
			# else we're happy that the thing didn't crash
		except (pyvo.DALQueryError, AssertionError) as ex:
			print(f"FAILURE ({ex}):\n{query}")
			failures += 1


if __name__=="__main__":
	sys.exit(main())
