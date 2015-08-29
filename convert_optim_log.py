#!/usr/bin/env python

#      Author: Parker Norton (pnorton@usgs.gov)
#        Date: 2015-04-23
# Description: Converts the optimization log generated by MOCOM into a useable
#              format for pandas and matplotlib

__version__ = '0.1'

import argparse
import prms_cfg as prms_cfg
import re



# Command line arguments
parser = argparse.ArgumentParser(description='Convert optimization logfile')

parser.add_argument('mocomrun', help='MOCOM run id')
parser.add_argument('configfile', help='Basin config file')
parser.add_argument('optimdir', help='Optimization log directory for calibration')
parser.add_argument('optimfile', help='Optimization log filename')

args = parser.parse_args()

runid = args.mocomrun
workdir = '%s/runs/%s' % (args.optimdir, runid)
opt_file = '%s/%s' % (workdir, args.optimfile)
opt_out = '%s/optim_fixed.log' % workdir
configfile = args.configfile

# Read the optimization log file
infile = open(opt_file, 'r')
rawdata = infile.read().splitlines()
infile.close()
it = iter(rawdata)

outfile = open(opt_out, 'w')

bad_chars = '():='
rgx = re.compile('[%s]' % bad_chars)

for line in it:
    if line[0:34] == 'Determining starting parameters...':
        # This is the group of random starting sets
        next(it)
        gennum = 0
        
        tmp_hdr = next(it).split()
        tmp_hdr.insert(0,'setnum')
        hdr_flag = True
        
        #print "header length: %d" % len(tmp_hdr)
        #tmp = 'setnum ' + next(it) + ' test0 test1 rank soln_num gennum'
        #outfile.write('%s\n' % ','.join(tmp.split()))
        #print tmp.split()
        
        while True:
            x = next(it)
            if x[0:1] == '':
                break

            # Strip out the junk characters ():=
            x = rgx.sub('', x) + ' ' + str(gennum)
            x = x.split()
            if x[1] == 'Bad':
                continue
            
            if hdr_flag:
                # Header info from starting population is incomplete, fill it it out
                # with information inferred from the first line of data
                cfg = prms_cfg.cfg(configfile)
                ofunc = []

                # Get the friendly name for each objective function
                for kk, vv in cfg.get_value('of_link').iteritems():
                    ofunc.append(vv['of_desc'])

                # Populate the test columns with friendly OF names
                for pp in range(0,(len(x) - len(tmp_hdr) - 3)):
                    tmp_hdr.append('OF_%s' % ofunc[pp])
                    # tmp_hdr.append('test%d' % pp)
                tmp_hdr.append('rank')
                tmp_hdr.append('soln_num')
                tmp_hdr.append('gennum')
                
                # Write the header out to the file
                outfile.write('%s\n' % ','.join(tmp_hdr))

                hdr_flag = False
            
            outfile.write('%s\n' % ','.join(x))
            
    if line[0:34] == 'Current generation for generation ':
        gennum = int(line.split(' ')[-1].rstrip(':'))+1
        next(it)    # skip one line
        next(it)    # skip one line
        next(it)    # skip one line
        
        while True:
            x = next(it)
            if x[0:1] == '':
                break
            
            # Strip out the junk characters ():=
            x = rgx.sub('', x) + ' ' + str(gennum)
            
            outfile.write('%s\n' % ','.join(x.split()))
    elif line[0:48] == 'Results for multi-objective global optimization:':
        gennum = int(next(it).split()[1])+1
        next(it)    # skip one line
        next(it)    # skip one line
        next(it)    # skip one line
        
        while True:
            x = next(it)
            if x[0:1] == '':
                break
            
            # Strip out the junk characters ():=
            x = rgx.sub('', x) + ' ' + str(gennum)
            
            outfile.write('%s\n' % ','.join(x.split()))

outfile.close()
print '\tTotal generations:', gennum - 1
