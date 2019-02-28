#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
	TODO : Description here
"""
__progname__ = "Google_Hash_Code"
__author__ = ""
__version__ = "0.0.1"
__status__ = "Development"


import logging
import argparse

LOG_FORMAT = '[%(asctime)s]' + '[{}][{}][{}]'.format(__progname__, __version__, __status__) + ' %(message)s'
LOG_VERBOSITY = {
	'DEBUG' : logging.DEBUG,
	'INFO' : logging.INFO,
	'WARNING' : logging.WARNING,
	'ERROR' : logging.ERROR,
	'CRITICAL' : logging.CRITICAL,
}

class HashCode(object):
	"""docstring for Pizza"""
	def __init__(self, file):
		super(HashCode, self).__init__()
		self.file = file

	def print(self):
		logging.debug('print')
		# TODO
		pass

	def process(self):
		logging.debug('process')
		# TODO
		pass

	def parse(self):
		with open(self.file, 'r') as input_file:
			# Read first line
			a, b, c, d = input_file.readline().strip().split(' ')
			self.a = int(a)
			self.b = int(b)
			self.c = int(c)
			self.d = int(d)

			logging.debug('a : {}'.format(self.a))
			logging.debug('b : {}'.format(self.b))
			logging.debug('c : {}'.format(self.c))
			logging.debug('d : {}'.format(self.d))

			# Go over the rest of the file
			for line in input_file:
				line = line.strip()
				logging.debug('Parsing: {}'.format(line))



def run_extract():
	# Handle arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", "--verbosity", help="increase output verbosity", choices = LOG_VERBOSITY)
	parser.add_argument("-i", "--input", required=True, help="input file")
	args = parser.parse_args()

	# configure logging
	logging.basicConfig(format=LOG_FORMAT, level=LOG_VERBOSITY.get(args.verbosity, 'INFO'), datefmt='%Y-%m-%d %I:%M:%S')

	plop = HashCode(args.input)
	plop.parse()
	plop.process()
	plop.print()

if __name__ == '__main__':
	run_extract()
	