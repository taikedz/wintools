#!/usr/bin/python

""" PySDL 1.3 - Serial Downloader for Python

Utility for downloading resources from the Internet.

=== PySDL ===

The download() function takes one or multiple fully qualified URLs and writes the file at that location to disk.

To change working directory, use cd(dest_path) which will set the new directory relative to the curent working directory from whence the Python interpreter was called.



There are several other functions that extend the ability of PySDL, for example link serialization and HTML link parsing.

=== STRING SERIALIZER ===

Use the serialization function to download a series of documents with similar paths:

http://www.example.com/reports/report001.pdf
http://www.example.com/reports/report002.pdf
http://www.example.com/reports/report003.pdf
http://www.example.com/reports/report004.pdf
http://www.example.com/reports/report005.pdf
http://www.example.com/reports/report006.pdf

Using a web browser, each of these files would have to be manually downloaded, involving a series of click-and-save operations. This is fine for a small number of documents, but not for anything larger...

The power of the PySDL's string serialization function allows construction of long series of strings.

The above could be done using PySDL:

sdl.download(
	sdl.serialstr("http://www.example.com/reports/report",".pdf","1-6/3")
)

given that there is a simple pattern:
-a prefix indicating the path,
-a number series in the range of 1 to 6, with 3 digits each
-a suffix (the file extension)

Say further there were folders for the months in the above example:

http://example.org/rep/jan/report001.txt
http://example.org/rep/jan/report002.txt
http://example.org/rep/jan/report003.txt
http://example.org/rep/feb/report001.txt
http://example.org/rep/feb/report002.txt
http://example.org/rep/feb/report003.txt

We can use:

sdl.download(
sdl.serialstr(
	"http://example.org/rep/",
	sdl.serialstr(["jan/report","feb/report"],".txt","1-3/3")
	)
)

When a number of files of the same name are downloaded, there is a naming conflict. A policy can be set on download
sdl.download(file,sdl.REPLACE)
The default policy is rename, thus keeping all data.

=== HTML EXTRACTION ===

Extract links from HTML files on the web to build a series of URLs to pass to the download() function.

parsePage(url) will parse a page at the given url for all images embedded in it using the IMG tag.

You may specify an extraction handler for the parsePage() function. The standard handler is extractLinks which by default parses pages for images in HREF references. You may also create your own handler. Extraction handlers must take exactly one compulsory argument, a HTML source code string, and return a list of paths.

parsePage will then automatically resolve the links against either the BASE url as specified in the HTML headers (if any), or the provided initial URL."""

import re
import urllib2
import os
from sys import argv

# errors -- MUST BE UPGRADED as raising <str> is no longer accepted.
BadNumberPattern = "bad number pattern"
BadRange = "bad number range"
BadPolicy = "The selected policy does not exist"

NotBaseError = "Base must specify protocol (eg 'http://','ftp://',...)"
BadAttribute = "The attribute must be 'href' or 'src'"

# VARS
# filename conflict
DISCARD = 0
RENAME = 1
REPLACE = 2

# Download ===============================================================================

def __filenamefor(pathname):
	return pathname[pathname.rfind("/")+1:]

def download(links,POLICY=RENAME,DEST_DIR='./',VERBOSE=True):
	''' Download a (series of) link(s)
	
	All files are downloaded first to a temporary file before being renamed to their actual name.
	
	Policies:
	RENAME - default policy ; renames the file currently being downloaded to a similar name
	DISCARD - do not download new data, keep the old data
	REPLACE - replace the old data with the new data
	'''
	if not os.path.isdir(DEST_DIR):
		os.makedirs(DEST_DIR) # if there was a non-directory file there before, this raises an exception
	if DEST_DIR[-1] != '/':
		DEST_DIR += '/'
	print "Downloading %i files to: %s" % (len(links),os.path.realpath(DEST_DIR) )
	if not(type(links) == list):
		links = [links] # turn it into a list!
	for lnk in links:
		filename = __filenamefor(lnk)
		destfile = DEST_DIR + filename
		if os.path.exists(destfile): # existing file
			if POLICY == DISCARD:
				print "DISCARD:",lnk,"; EXISTS:",destfile
				continue # don't even bother downloading
			elif POLICY == REPLACE:
				# os.remove(destfile) # delete the file at this location
				# bad implementation - the removal should happen just
				# when the filesystem is ready to replace a file to
				# avoid loss of data
				
				pass
				# commented out because on Mac OS X, rename systematically replaces files.
				# must test on other systems
			elif POLICY != RENAME: # inexistant policy
				raise BadPolicy
			else: # must rename new file
				y = 1
				while os.path.exists(DEST_DIR+"cp"+str(y).zfill(3)+"_of_"+filename):
					y += 1
				destfile = DEST_DIR+"cp"+str(y).zfill(3)+"_of_"+filename
		try:
			if VERBOSE:
				print "Load: %s to %s" % (lnk,destfile)
			conn = urllib2.urlopen(lnk)
			
			tfilename = destfile+".part"
			
			fileh = open(tfilename,'w')
			fileh.write(conn.read() ) # catch other errors
			fileh.close()
			conn.close()
			os.rename(tfilename,destfile)
		except urllib2.URLError, e:
			print e
			#print "Error %i: %s" % e.reason

# Serialization =============================================================

def serialstr(prefix, suffix, numpat=''):
	'''Allows the building of multiple sequences of strings combining prefix and suffixes,
	optionally with a zero-padded number range in between
	
	The prefix and suffix may each be a single string, or a sequence of strings.
	In the case of sequences, each item in the prefix set will be paired with each
	item in the suffix set, each pair with the appropriate inserted number sequence when applicable.
	
	The number range is expressed as
		start_index "-" end_index "/" pad_width
	
	wherein start_index is the lower index of the rage (inclusive)
		end_index is the upper index of the range (inclusive)
		pad is the number of digits the number should hold
	
	If the count of digits in the number is less than the amount
	specified by pad, zeros are added to the left of the number string
	until that count is reached; otherwise the number is left as is.
	
	If the number pattern is omitted, it will be ignored and no numbers will
	be inserted between the prefix and suffix
	
	Examples:
	>>> serialstr('hi','bye','1-2/3')
	['hi001bye','hi002bye']
	>>> serialstr(['hi','hello'],[' madam',' sir'])
	['hi madam', 'hello madam', 'hi sir', 'hello sir']
	'''
	combos = []
	if type(suffix) is list:
		for s in suffix:
			combos += serialstr(prefix,s,numpat)
		return combos
	elif type(prefix) is list:
		for p in prefix:
			combos += serialstr(p,suffix,numpat)
		return combos
	
	# at this point, both prefix and suffix are strings
	
	if numpat == '':
		return [prefix+suffix]
	else:
		mat = re.compile(r'^\s*(\d+)\s*-\s*(\d+)\s*/\s*(\d+)\s*$').match(numpat)
		if not mat:
			raise BadNumberPattern, 'The format is: start_index "-" end_index "/" pad_width (any whitespace)'
		
		start, end, pad = mat.groups()
		pad = int(pad)
		if int(start) > int(end):
			raise BadRange, "Start:%s / End: %s" % (start, end)
		elif int(start) < 0 or int(end) < 0:
			raise BadRange, "All numbers in number range must be positive or nil"
		
		for i in range(int(start), int(end)+1):
			combos.append( "".join([prefix,str(i).zfill(pad),suffix]) )
	
	return combos

# URL Extraction =======================================================

def extractLinks(source,attribute="href",extensions=["jpg","jpeg","png","gif"]):
	'''Given HTML source code, extract all HREF or SRC links pointing to files with the provided extensions.

extensions argument is a list of file name extensions. By default: ["jpg","jpeg","png","gif"]
attribute argument takes a string value of "href" or "src". By default: "href"
	'''
	extensions = "".join(["(?:",r"\."+(r"|\.".join(extensions)),")"])
	if not (attribute == "href" or attribute == "src"):
		raise BadAttribute
	links = re.findall(r'<[^>]+?\s+(?:'+attribute+r')\s*=\s*("[^\r\n"]+?'+extensions+'"|[^\s>]+'+extensions+')',source,re.I)
	for x in range(len(links) ):
		adr = links[x]
		if adr[0] == '"' and adr[-1] == '"':
			links[x] = adr[1:-1]
	return links

def imagePaths(source):
	''' Given HTML source code, extract all paths to images of type JPEG, PNG and GIF in href or src attributes.
	'''
	links = extractLinks(source,attribute="href",extensions=["jpg","jpeg","png","gif"])
	links.append( extractLinks(source,attribute="src",extensions=["jpg","jpeg","png","gif"]) )
	return links

def resolve(base,relative):
	'''Resolve a link relative to an absolute one.

Returns the implied absolute location of the provided relative.

eg resolve("http://www.example.com/me/you.html","us.html") --> http://www.example.com/me/us.html

Does not collapse dot references yet, eg
	http://moo.org/hey/../you.html
should be
	http://moo.org/you.html
to be done for next version
	'''
	if not re.match("(.+)://",base):
		raise NotBaseError,base
	if re.match("(.+)://",relative):
		return relative
	if relative[0] == "/":# root link
		m = re.match("(.+?://.+?)/",base)
		return m.group(1)+relative
	# else is actually relative
	if re.match(r".+\.[^/]+",base):# remove file ref
		return re.match("(.+/)",base).group(1)+relative
	elif base[-1] == "/":
		return base+relative
	else:
		return base+"/"+relative

def readPage(purl):
	if not re.match("[a-z]+://",purl):
		purl = "file://"+os.path.realpath(purl) # turn local path into url
	return urllib2.urlopen(purl).read()

def parsePage(purl,hextract=extractLinks):
	'''Parse a page at a given URL

If purl starts with file:// or does not have a scheme, a local file is opened.
This local file should have a <BASE> tag in its HTML header, otherwise all links will be returned as absolutes of "file://<path to local file>"

If purl starts with an internet scheme (eg http, ftp) then a remote file will be read.

Returns a list of absolute links, consistent with the scheme and path specified, and the declared base in the HTML source.

The default handler is the extractLinks function. You may also create your own handler. Extraction handlers must take exactly one compulsory argument, a HTML source code string, and return a list of str objects (the paths).

For example:
def getOffice(source):
	return sdl.extractLinks(source,attribute="href",extensions=["xls","doc","ppt"])

links = sdl.parsePage("http://www.my.com/reports.html",hextract=getOffice)
	'''
	page = readPage(purl)
	links = hextract(page)
	base = re.findall(r"""<(?:base|BASE)\s[^>]*?href\s*=\s*("[^\r\n"]+"|[^\s])""",page)
	if base:
		base = base[0]
		if base[0] == '"' and base[-1] == '"':
			base = base[1:-1]
		base = resolve(purl,base)
	else:
		base = purl
	for i in range(len(links)):
		links[i] = resolve(base,links[i])
	return links

# Network use optimization ===================================================================

def http11opt_download(links):
	'''!!! This function is unimplemented !!!
	
	This function is designed to make use of the HTTP 1.1 feature in which multiple items
	may be downloaded using the same TCP/IP connection, if all fils are served by the same
	server.
	
	Requirements:
	- URLs must use HTTP as their scheme
	- at connection time, HTTP 1.1 must be identified as the server's protocol
	- links must be divided into groups by server name
	'''
	pass

# MAIN ========

""" This library cannot have a significant main body for execution due to the variety of ways in which download paterns/links may be provided.

To make it a CLI savvy program would require also creating commands for it to map to the functions, and given the use of a Python interpreter, such a feature would be in essence redundant.
"""
