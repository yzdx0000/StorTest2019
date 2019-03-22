#!/usr/bin/python
#Display memory usage for ParaStor, input like this
#python parastor_why_oom.py vmcore vmlinux
#OR
#python parastor_why_oom.py vm vmlinux
#Created by yuanqb @ 20161124
#Released 1.0.0    @ 20161126

#----------------------------------
#|Overview    |Total       |60.83GB
#|            |Free        | 1.51GB
#|            |Used        |59.32GB
#----------------------------------
#|User Mode   |oStor       |20.13GB
#|            |oPara       | 1.51GB
#|            |Java        | 9.35GB
#----------------------------------
#|Kernel Mode |Slab        | 0.83GB
#|            |Cache       | 3.51GB
#|            |Buffer      | 0.32GB
#----------------------------------
#|Missing     |All         |30.76GB
#----------------------------------

import os,sys,time

parastorko=""

overview={}
usermode={}
kernelmode={}
shared={}
missing={}
itemlen=24

totalmem=0

#append blank in order to let len(name) == nr
def appendblank(name, nr):
	index=len(name)
	while index < nr:
		name += " "
		index+=1

	return name

def display(dict):
	print "-----------------------------------------------------"
	dict_sorted=sorted(dict.iteritems(), key=lambda asd:asd[1], reverse=True)
	index=0
	dict_name ="|N/A         |"
	dict_blank="|            |"
	if dict == overview:
		dict_name="|Overview    |"
	if dict == usermode:
		dict_name="|User Mode   |"
	if dict == kernelmode:
		dict_name="|Kernel Mode |"
	if dict == missing :
		dict_name="|Missing     |"
	
	while index < len(dict_sorted):
		#page to gb
		if dict_sorted[index][1] == "???.??":
			strsize_gb=dict_sorted[index][1]
		else:
			size_gb=dict_sorted[index][1]*4/1024/1024.0
			size_gb=float('%.2f'%size_gb)
			if (dict == usermode) and (size_gb < 0.1):
				break
			if (dict == kernelmode) and ("SLAB" in dict_sorted[index][0]) and (size_gb < 0.1):
				break
			#append 0. such as 1.1 to 1.10
			strsize_gb=str(size_gb)
			if (len(strsize_gb.split('.')[1]) == 1):
				strsize_gb+="0"
			if (len(strsize_gb.split('.')[0]) == 1):
				strsize_gb="  "+strsize_gb
			elif (len(strsize_gb.split('.')[0]) == 2):
				strsize_gb=" "+strsize_gb
		strsize_gb+=" GB"

		if totalmem != 0 and str(dict_sorted[index][1]).isdigit():
			percent = '%3d'%(dict_sorted[index][1]*100/totalmem)
			strsize_gb+=" "+percent+"%"

		if index == 0:
			print dict_name+dict_sorted[index][0]+strsize_gb
		else:
			print dict_blank+dict_sorted[index][0]+strsize_gb

		index+=1

#input like this
if len(sys.argv) == 4:
	parastorko = sys.argv[3]
elif len(sys.argv) != 3:
	print "python "+sys.argv[0]+" vmcore vmlinux parastor.unstripped.ko"
	exit(-1)

print "Please wait for a moment..."

#create crash script and run
#1-overview script
basename=str(time.time())

overview_script=basename+"overview"
fd=open(overview_script, 'w')
fd.write("kmem -i\nexit\n")
fd.close()

usermode_script=basename+"usermode"
fd=open(usermode_script, 'w')
fd.write("ps -u -G\nexit\n")
fd.close()

kernelmode_script=basename+"kernelmode"
fd=open(kernelmode_script, 'w')
fd.write("kmem -s\nexit\n")
fd.close()

parastorko_script=basename+"parastorko"
fd=open(parastorko_script, 'w')
fd.write("mod\n")
if len(parastorko) != 0:
	fd.write("mod -s parastor "+parastorko+"\n")
	for index in range(8):
		fd.write("p ((fsc_storsys_t *)g_storsys_locklist.list.next)->ss_pgcache.node_data["+str(index)+"]->mgr[0]\n")
		fd.write("p ((fsc_storsys_t *)g_storsys_locklist.list.next)->ss_pgcache.node_data["+str(index)+"]->mgr[1]\n")
fd.write("exit\n")
fd.close()

overview_output=os.popen("crash "+sys.argv[1]+" "+sys.argv[2]+" -i "+overview_script)
for line in overview_output:
	if "TOTAL MEM" in line:
		line_array=line.split()
		if line_array[0] == "TOTAL":
			overview[appendblank("Total",itemlen)+"|"]=int(line_array[2])
			totalmem = int(line_array[2])
		if line_array[0] == "FREE":
			overview[appendblank("Free",itemlen)+"|"]=int(line_array[1])
		if line_array[0] == "USED":
			overview[appendblank("Used",itemlen)+"|"]=int(line_array[1])
		if line_array[0] == "SHARED":
			shared[appendblank("Shared",itemlen)+"|"]=int(line_array[1])
		if line_array[0] == "BUFFERS":
			kernelmode[appendblank("Buffers",itemlen)+"|"]=int(line_array[1])
		if line_array[0] == "CACHED":
			kernelmode[appendblank("Cached",itemlen)+"|"]=int(line_array[1])
		#if line_array[0] == "SLAB":
		#	kernelmode[appendblank("Slab",itemlen)+"|"]=int(line_array[1])
usermode_output=os.popen("crash "+sys.argv[1]+" "+sys.argv[2]+" -i "+usermode_script)
for line in usermode_output:
	if "ffff" in line:
		line_array=line.split()
		if len(line_array) > 5:
			process=line_array[-1]+"_"+line_array[0]
			process=appendblank(process,itemlen)+"|"
			usermode[process]=int(line_array[-2])/4 # transform to PAGES from KB
kernelmode_output=os.popen("crash "+sys.argv[1]+" "+sys.argv[2]+" -i "+kernelmode_script)
for line in kernelmode_output:
	if "ffff" in line:
		line_array=line.split()
		if len(line_array) > 5:
			if "parastor_" in line_array[1]:
				slab="SLAB:"+line_array[1][len("parastor_"):]
			else:
				slab="SLAB:"+line_array[1]
			slab=appendblank(slab,itemlen)+"|"
			kernelmode[slab]=int(line_array[-2])*int(line_array[-1][:-1])/4 # transform to PAGES from KB
parastorko_output=os.popen("crash "+sys.argv[1]+" "+sys.argv[2]+" -i "+parastorko_script)
blocks=0
core_has_parastor=0
for line in parastorko_output:
	if ("parastor" in line) and ("not loaded" in line):
		core_has_parastor=1
	if " blocks_nr" in line:
		blocks+=int(line.split()[-1][:-1])
if len(parastorko) == 0:
	#user do not provide parastor.ko
	if core_has_parastor == 1:
		#vmcore has parastor
		kernelmode[appendblank("parastor.ko",itemlen)+"|"]="???.??"
else:
	kernelmode[appendblank("parastor.ko",itemlen)+"|"]=blocks

os.popen("rm -f "+overview_script)
os.popen("rm -f "+usermode_script)
os.popen("rm -f "+kernelmode_script)
os.popen("rm -f "+parastorko_script)

#check
used_pages=0
know_pages=0
shared_pages=0
for key in overview.keys():
	if "Used" in key:
		used_pages=overview[key]
		break
for key in usermode.keys():
	know_pages+=usermode[key]	
for key in kernelmode.keys():
	if kernelmode[key] == "???.??":
		continue
	know_pages+=kernelmode[key]	
for key in shared.keys():
	shared_pages+=shared[key]	
missing[appendblank("All",itemlen)+"|"]=used_pages-know_pages+shared_pages

#display Overview
display(overview)
display(usermode)
display(kernelmode)
display(missing)
print "-----------------------------------------------------"
if "???.??" in kernelmode.values():
	print "Please provide parastor.ko to get the size of it!"
	print "python "+sys.argv[0]+" vmcore vmlinux parastor.unstripped.ko"
