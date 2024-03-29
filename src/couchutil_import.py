#!/usr/bin/python
import sys, csv, requests, json

##########
## MAIN ##
##########
def main():
	if len(sys.argv) != 3:
		print 'Bad arguments: expected databaseURL and document name, got %s'\
			%len(sys.argv)
		sys.exit(1)
	
	program_name = sys.argv[0]
	database_url = sys.argv[1]
	document_name = sys.argv[2]
	
	#read pipe for CSV data, assume first line is column names
	reader = csv.reader(sys.stdin, delimiter='\t')
	names = None
	
	try:
		names = reader.next()
	except StopIteration:
		print 'error, empty input'
		sys.exit(1)
	
	if names == None:
		print 'error, couldn\'t read names'
		sys.exit(1)
	
	num_rows = 0
	num_errors = 0
	docs = []
	
	for row in reader:
		try:
			if len(names) != len(row):
				raise Exception('row/name len mismatch')
			docs.append({"doc_type": document_name,\
				"data": dict(zip(names, row))})
			num_rows += 1
		except Exception as ex:
			print 'error, skipping row %s %s: '%(num_rows,str(ex)),\
				sys.exc_info()[0]	
			num_errors += 1
	
	headers = {'Content-type':'application/json'}
	docs_data = json.dumps({"docs":docs})
	bulk_url = "%s/_bulk_docs"%database_url
	print "Sending to %s..."%bulk_url
	
	try:
		resp = requests.post(bulk_url, data=docs_data, headers=headers)
	except requests.exceptions.ConnectionError as ex:
		print "Server error: %s"%(ex)
		sys.exit(1)
	
	if resp.status_code != 201:
		print "Request error: %s %s" % (resp.status_code, resp.text)
		sys.exit(1)
	
	try:
		db_response = json.loads(resp.text)
		errors = []
		for resp in db_response:		
			if resp.has_key("ok") and resp["ok"] == True:
				sys.stdout.write('.')
			else:		
				sys.stdout.write('X')
				errors.append(str(resp))
			if len(errors) > 0:
				print str(errors)
	except ValueError:
		print 'error reading response: %s'%resp.text, sys.exc_info()[0]	
		sys.exit(1)
		
	print '\n\ndone. read: %s\terrors:%s'%(num_rows,num_errors)
	sys.exit(0)
## END MAIN ##

if __name__ == "__main__":
	main()

