from mpi4py import MPI
from mpi_master_slave import Master, Slave
from mpi_master_slave import WorkQueue
import time
import numpy as np
import sys
import os
import treecorr
import astropy.io.fits as fits

import os

shell_outdir=os.environ["shell_outdir"]
xicorr_outdir=os.environ["xicorr_outdir"]


class MyApp(object):
    """
    This is my application that has a lot of work to do so it gives work to do
    to its slaves until all the work is done
    """

    def __init__(self, slaves):
        # when creating the Master we tell it what slaves it can handle
        self.master = Master(slaves)
        # WorkQueue is a convenient class that run slaves on a tasks queue
        self.work_queue = WorkQueue(self.master)

    def terminate_slaves(self):
        """
        Call this to make all slaves exit their run loop
        """
        self.master.terminate_slaves()

    def run(self, tasks=None):
        """
        This is the core of my application, keep starting slaves
        as long as there is work to do
        """
        #
        # let's prepare our work queue. This can be built at initialization time
        # but it can also be added later as more work become available
        #
        data = fits.getdata(shell_outdir+'random.fits')
        X=data['X']
        Y=data['Y']
        Z=data['Z']
        lists=list()
        for i in range(tasks):
            lists.append((i,X,Y,Z))

        for i in range(tasks):
            # 'data' will be passed to the slave and can be anything
            self.work_queue.add_work(data=(lists[i], i))
       
        #
        # Keeep starting slaves as long as there is work to do
        #
        while not self.work_queue.done():

            #
            # give more work to do to each idle slave (if any)
            #
            self.work_queue.do_work()

            #
            # reclaim returned data from completed slaves
            #
            for slave_return_data in self.work_queue.get_completed_work():
                done, message = slave_return_data
                if done:
                    print('Master: slave finished is task and says "%s"' % message)

            # sleep some time
            time.sleep(0.3)


class MySlave(Slave):
    """
    A slave process extends Slave class, overrides the 'do_work' method
    and calls 'Slave.run'. The Master will do the rest
    """

    def __init__(self):
        super(MySlave, self).__init__()

    def do_work(self, data):
        import subprocess
        rank = MPI.COMM_WORLD.Get_rank()
        name = MPI.Get_processor_name()
        task, task_arg = data
        corrfun_one(task)
        print(task_arg)
        sys.stdout.flush()
        print('  Slave %s rank %d executing "%s" task_id "%d"' % (name, rank, task, task_arg) )
        return (True, 'I completed my task (%d)' % task_arg)

def corrfun_one(X):
    (chunk_num,pos_x,pos_y,pos_z)=X
    data = fits.getdata(shell_outdir+'angcorr%d.fits'%chunk_num)
    cat1 = treecorr.Catalog(x=data['X'], y=data['Y'], z=data['Z'])
    cat2 = treecorr.Catalog(x=pos_x, y=pos_y, z=pos_z)
    nthetabins=40
    bin_slop=0
    bin_type="Linear"
    nn = treecorr.NNCorrelation(min_sep=1, max_sep=200, nbins = nthetabins, bin_slop=bin_slop, bin_type=bin_type)
    dr = treecorr.NNCorrelation(min_sep=1, max_sep=200, nbins = nthetabins, bin_slop=bin_slop, bin_type=bin_type)
    rr = treecorr.NNCorrelation(min_sep=1, max_sep=200, nbins = nthetabins, bin_slop=bin_slop, bin_type=bin_type)   
    rd = treecorr.NNCorrelation(min_sep=1, max_sep=200, nbins = nthetabins, bin_slop=bin_slop, bin_type=bin_type)  
    nn.process(cat1)
    dr.process(cat1,cat2)
    rr.process(cat2)
    rd.process(cat2,cat1)
    xi,varxi = nn.calculateXi(rr,dr,rd)
    x = nn.meanr
    y = xi
    np.savetxt(xicorr_outdir+'3dcorr_%d.txt'%chunk_num,np.array([x,y,varxi]).transpose())

def main():

    name = MPI.Get_processor_name()
    rank = MPI.COMM_WORLD.Get_rank()
    size = MPI.COMM_WORLD.Get_size()

    print('I am  %s rank %d (total %d)' % (name, rank, size) )

    if rank == 0: # Master

        app = MyApp(slaves=range(1, size))
        app.run(100)
        app.terminate_slaves()

    else: # Any slave

        MySlave().run()

    print('Task completed (rank %d)' % (rank) )

if __name__ == "__main__":
    main()
