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
angcorr_outdir=os.environ["angcorr_outdir"]


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
        data0 = fits.getdata(shell_outdir+'angcorr0.fits')
        L = len(data0['ra']) 
        ran_L = L*10
        random_state=np.random.RandomState()
        u1,u2= random_state.uniform(size=(2, ran_L) )
        ramin,ramax= 0,90
        dcmin,dcmax= 0,90
        cmin = np.sin(dcmin*np.pi/180)
        cmax = np.sin(dcmax*np.pi/180)
        RA   = ramin + u1*(ramax-ramin)
        DEC  = 90-np.arccos(cmin+u2*(cmax-cmin))*180./np.pi
        lists=list()
        for i in range(tasks):
            lists.append((i,RA,DEC))

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
    (chunk_num,ran_ra,ran_dec)=X
    data = fits.getdata(shell_outdir+'angcorr%d.fits'%chunk_num)
    cat1 = treecorr.Catalog(ra=data['ra'], dec=data['dec'], ra_units='degrees', dec_units='degrees')
    cat2 = treecorr.Catalog(ra=ran_ra, dec=ran_dec, ra_units='degrees', dec_units='degrees')
    thetamin=0.9
    thetamax=9
    nthetabins=10
    bin_slop=0
    bin_type="Log"
    nn = treecorr.NNCorrelation(min_sep=thetamin, max_sep=thetamax, nbins = nthetabins, bin_slop=bin_slop, bin_type=bin_type,sep_units='degrees')
    dr = treecorr.NNCorrelation(min_sep=thetamin, max_sep=thetamax, nbins = nthetabins, bin_slop=bin_slop, bin_type=bin_type,sep_units='degrees')
    rr = treecorr.NNCorrelation(min_sep=thetamin, max_sep=thetamax, nbins = nthetabins, bin_slop=bin_slop, bin_type=bin_type,sep_units='degrees')   
    rd = treecorr.NNCorrelation(min_sep=thetamin, max_sep=thetamax, nbins = nthetabins, bin_slop=bin_slop, bin_type=bin_type,sep_units='degrees')  
    nn.process(cat1)
    dr.process(cat1,cat2)
    rr.process(cat2)
    rd.process(cat2,cat1)
    xi,varxi = nn.calculateXi(rr,dr,rd)
    x = nn.meanr
    y = xi
    np.savetxt(angcorr_outdir+'angcorr_%d.txt'%chunk_num,np.array([x,y,varxi]).transpose())

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
