#!/usr/bin/env python

import os
import sys

#dir containing app's .bc file
bcdir = os.getcwd()

#.bc file generated by gllvm's 'get-bc' from final linked exe
for file in os.listdir(bcdir):
	if file.endswith(".bc"):
		app_bc = file
		break

#dir containing all files wrt invariant generation
invdir = sys.argv[0][0:sys.argv[0].rfind("/")]

if("daikon-output" not in os.listdir(bcdir)):
	os.system("mkdir daikon-output")

#clang compile custom IO call wrapper file
os.system("clang -c -emit-llvm "+invdir+"/dtrace_gen/io_wrappers.c")

#link app's .bc file with io_wrapper.bc
os.system("llvm-link io_wrappers.bc "+app_bc+" -S -o=app1.bc")

#llvm transformation pass to add instrumentation to generate .dtrace files
os.system("opt -load "+invdir+"/dtrace_gen/build/proj/libdtrace.so -dtrace <app1.bc> app2.bc")

#run lli on bitcode + each input arg file to generate dtrace files
dtrace_count = 0
for file in os.listdir(bcdir+"/args"):
	os.system("cp "+invdir+"/dtrace_gen/daikon-header.txt f.dtrace")
	os.system("lli app2.bc ./args/"+file)
	dtrace_count = dtrace_count + 1
	os.system("mv f.dtrace daikon-output/"+str(dtrace_count)+".dtrace")

#run Daikon on dtrace files
os.system("java -cp $DAIKONDIR/java:$DAIKONDIR/java/lib/* daikon.Daikon --config "+invdir+"/dtrace_gen/daikon-conf.txt daikon-output/*.dtrace > invar.txt")

#llvm analysis pass to extract io specialization info
#os.system("opt -load "+invdir+"/io_spec/build/proj/libiospec.so -iospec <"+app_bc+"> /dev/null")

#llvm analysis pass + llvm transformation pass for file lifting
os.system("opt -load "+invdir+"/file_lift/build/proj/libfilelift.so -filelift <"+app_bc+"> fin_app.bc")