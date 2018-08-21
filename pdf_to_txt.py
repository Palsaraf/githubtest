import os
from os import chdir,getcwd,list,path
import pyPdf
from time import strftime


def check_path(prompt):
	abs_path=raw_input(prompt)
	while path.exists(abs_path)!= True:
		print "the does not exist"
		abs_path=raw_input(prompt)
	return abs_path	
print "\n"

folder=check_path('provide the path')

list=[]
directory=folder
for root,dirs,files in os.walk(directory):
	for filename in files:
		t=os.path.join(directory.filename)
		list.append(t)

m=len(list)

i=0

while i<=len(list):
	path-list[i]
	head,tail=os.path.split(path)
	var='\\'
	tail=tail.replace(".pdf",".txt")		
	content=""
	pdf=pyPdf.PdfFileReader(file(path,"rb"))
	for i in range(0,pdf.getNumPages()):
		content+=pdf.getPage(i).extractText()+"\n"
f=open(name,'w')
f.write(content.encode("UTF-8"))
f.close		

