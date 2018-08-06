#!/usr/bin/env python
import os, sys, optparse, logging, glob, stat, json
logger = logging.getLogger(__name__)

#set up lists to be looped through later
global dirs
dirs = ["in_container/", "out_container/"]

def main():
    #create a base directory
    os.mkdir("benchmarking_directory/")
    os.chdir("benchmarking_directory/")
    #make directories for in and out of the container
    os.mkdir(dirs[0])
    os.mkdir(dirs[1])
    i = 0
    while(i < 2):
        os.chdir(dirs[i])
        if(dirs[i] == dirs[1]):
            create_submit(False)
        else:
            create_submit(True)
        os.chdir("..")
        i += 1

def create_submit(use_container):
    job_num = 'Container' + str(use_container)

    job_dir = os.getcwd() + '/'

    # create submit file
    queue = 'default'

    submit = submit_template.format(queue=queue,
                                    job_dir=job_dir,
                                    job_num=job_num,
                                    use_container=use_container)
    open(job_dir + '/submit.sh', 'w').write(submit)
    os.chmod(job_dir + '/submit.sh', stat.S_IRWXU | stat.S_IRWXG | stat.S_IXOTH | stat.S_IROTH)
    os.chdir(job_dir)
    os.system('qsub submit.sh')
    os.chdir("..")

submit_template = '''#!/bin/bash
#COBALT -n 512
#COBALT -t 540
#COBALT -q {queue}
#COBALT -A datascience
#COBALT --jobname {job_num}
#COBALT --cwd {job_dir}

RANKS_PER_NODE=1
NUM_NODES=$COBALT_JOBSIZE
TOTAL_RANKS=$(( $COBALT_JOBSIZE * $RANKS_PER_NODE ))


# app build with GNU not Intel
module swap PrgEnv-intel PrgEnv-gnu
USE_CONTAINER={use_container}
if [ "$USE_CONTAINER" = "FALSE" ] || [ "$USE_CONTAINER" = "false" ] || [ "$USE_CONTAINER" = "False" ]; then
   echo RUNNING OUTSIDE OF CONTAINER
   sleep 3
   /home/sgww/crazy_auto_test/firstestout.sh > 128_one.txt 2>$1 &
   sleep 3
   /home/sgww/crazy_auto_test/firstestout.sh > 128_two.txt 2>$1 &
   sleep 3
   /home/sgww/crazy_auto_test/secondtestout.sh > 256_one.txt 2>&1 &
   sleep 3
   wait
fi

# Use Cray's Application Binary Independent MPI build
module swap cray-mpich cray-mpich-abi


# include CRAY_LD_LIBRARY_PATH in to the system library path
export LD_LIBRARY_PATH=$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH
# also need this additional library
export LD_LIBRARY_PATH=/opt/cray/wlm_detect/1.3.2-6.0.6.0_3.8__g388ccd5.ari/lib64/:$LD_LIBRARY_PATH
# in order to pass environment variables to a Singularity container create the variable
# with the SINGULARITYENV_ prefix
export SINGULARITYENV_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
# print to log file for debug
echo $SINGULARITYENV_LD_LIBRARY_PATH


# -n <total MPI ranks>
# -N <MPI ranks per node>
export SINGULARITYENV_LD_LIBRARY_PATH=/lib64:/lib:/usr/lib64:/usr/lib:$SINGULARITYENV_LD_LIBRARY_PATH
# aprun -n 1 -N 1 singularity exec testbuild2.simg /bin/bash -c "echo \$LD_LIBRARY_PATH"

if [ "$USE_CONTAINER" = "TRUE" ] || [ "$USE_CONTAINER" = "true" ] || [ "$USE_CONTAINER" = "True" ]; then
   echo RUNNING INSIDE CONTAINER
   sleep 3
   /home/sgww/crazy_auto_test/firstestin.sh > 128_one.txt 2>$1 &
   sleep 3
   /home/sgww/crazy_auto_test/firstestin.sh > 128_two.txt 2>$1 &
   sleep 3
   /home/sgww/crazy_auto_test/secondtestin.sh > 256_one.txt 2>&1 &
   sleep 3
   wait
fi
'''

if __name__ == "__main__":
    main()
