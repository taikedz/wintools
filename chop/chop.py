import sys,re,os

ignorer = []
splitter =  []
sfiles = []

for arg in sys.argv[1:]:
	if arg.startswith("-i"): # defined an ignorer
		arg = arg[2:]
		if arg[0] == '"' and arg[-1] == '"':
			arg = arg[1:-1]
		ignorer += arg
	elif arg.startswith("-s"): # defined splitter
		arg = arg[2:]
		if arg[0] == '"' and arg[-1] == '"':
			arg = arg[1:-1]
		splitter += arg
	else: # defined a file
		sfiles += arg

if len(splitter) == 0 or len(sfiles) == 0:
	print """You have %i files to be split according to lines matching any of %i patterns. You must at least have one of each.

Usage:

chop -iIGNORER ... -sSPLITTER ... FILE ...

Any number of IGNORER patterns can be defined. Any line matching the ignorer regular expression pattern will be discarded.

At least one SPLITTER pattern must be defined. Any line matching the splitter regular expression pattern starts a new file. The line will appear at the start of the new file.

Specify at least one file that needs splitting with these rules. Files will be split into seperate files whose name will carry a numeric prefix of 5 digits before the original file's name.

For example:
	chop -i"comment here" -i"comment there" -s"new section" -s"new file" myfile.txt""" % (len(sfiles),len(splitter) )

else:
	for f in sfiles:
		try:
			chop(f)
		except Exception(e):
			print e

def chop(fname):
	source = open(fname,'rU')
	
	line = source.readline()
	
	idx = 0
	outfile = None
	
	while line != '':
		process = True
		
		# ignorer list serves to discard lines
		for pat in ignorer:
			if re.match(pat,line,flags=re.I):# found a line to ignore
				print "Ignored: ",line
				line = source.readline() # read next line
				process = False # flag not to process
				break # can't continue the parent loop inside this loop
		
		if not process:
			continue
		
		# match a line against a pattern. if there is a match, a new file is started with this line.
		for pat in splitter:
			if re.match(pat,line,flags=re.I):
				if outfile != None:
					outfile.close()
				outfile = open(str(idx).zfill(5)+fname,'w')
				print "Split at: " + line
				idx += 1
				break
		if outfile != None:
			outfile.write(line)
		line = source.readline()