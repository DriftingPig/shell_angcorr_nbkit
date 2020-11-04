import astropy.io.fits as fits
#import treecorr
import numpy as np
from nbodykit.lab import *
from mpi4py import MPI
import numpy as np
import dask.array as da
import sys

import os
width=float(os.environ['config_width'])
z_ave=float(os.environ['config_redshift'])
delta_z = width*(1+z_ave)
redshift = z_ave
omega_m=float(os.environ['config_omega_m'])
omega_lambda=1.-omega_m
omega_b=float(os.environ['config_omega_b'])
h=float(os.environ['config_h'])
ns=float(os.environ['config_ns'])
sigma8=float(os.environ['config_sigma8'])
b1=float(os.environ['config_bias'])
outdir=os.environ['outdir']
density=float(os.environ['density'])
ntot=int(os.environ['tot_mock'])
seed=int(os.environ['seed'])


def corr_fun():
    
    cosmo = cosmology.cosmology.Cosmology(h=h,Omega0_b=omega_b,Omega0_cdm=omega_m-omega_b,n_s=ns)
    cosmo2=cosmo.match(sigma8=sigma8)
    Plin = cosmology.LinearPower(cosmo2, redshift, transfer='EisensteinHu')

    cat = LogNormalCatalog(Plin=Plin, nbar=density*ntot, BoxSize=1500, Nmesh=512, bias=b1, seed=seed)
    arr_cat = cat.Position().compute()

    

    ra,dec,z = transform.CartesianToSky(cat.Position(),cosmo=cosmo,observer=[0, 0, 0])
    cat['ra'] = ra
    cat['dec'] = dec
    cat['z'] = z
    print(cat.columns)
    cat.save(outdir,columns=cat.columns)
    #ra2,dec2,z2 = transform.CartesianToSky(random_cat,cosmo=cosmo,observer=[0, 0, 0])
    #print(len(ra.compute()))   
    #zmax=redshift + delta_z/2.
    #zmin=redshift - delta_z/2.
    #sel1=(z>zmin)&(z<zmax)
    #sel2=(z2>zmin)&(z2<zmax)
    #ra=ra[sel1]
    #dec=dec[sel1]
    #z=z[sel1]
    #ra2=ra2[sel2]
    #dec2=dec2[sel2]
    #z2=z2[sel2]
    #position1=cat.Position()[sel1]
    #position2=random_cat[sel2]

    

    #print(len(ra.compute()),len(ra2.compute()))
    #np.savetxt('data.txt',np.array([ra.compute(),dec.compute(),z.compute()]))
    #np.savetxt('random.txt',np.array([ra2.compute(),dec2.compute(),z2.compute()]))

    #n,bins,_=plt.hist(z,bins=30,density=True)
    #x=(bins[1:]+bins[:-1])/2
    #plt.show()
    #np.savetxt('./redshift/angshell_%d.txt'%seed_num,np.array([x,n]).transpose())
    #cat1 = treecorr.Catalog(ra=ra.compute(), dec=dec.compute(), ra_units='degrees', dec_units='degrees')
    #cat2 = treecorr.Catalog(ra=ra2.compute(), dec=dec2.compute(), ra_units='degrees', dec_units='degrees')
    #thetamin=0.9
    #thetamax=9
    #nthetabins=64
    #bin_slop=0
    #bin_type="Log"#Log
    #nn = treecorr.NNCorrelation(min_sep=thetamin, max_sep=thetamax, nbins = nthetabins, bin_slop=bin_slop, bin_type=bin_type,sep_units='degrees')
    #dr = treecorr.NNCorrelation(min_sep=thetamin, max_sep=thetamax, nbins = nthetabins, bin_slop=bin_slop, bin_type=bin_type,sep_units='degrees')
    #rr = treecorr.NNCorrelation(min_sep=thetamin, max_sep=thetamax, nbins = nthetabins, bin_slop=bin_slop, bin_type=bin_type,sep_units='degrees')
    #rd = treecorr.NNCorrelation(min_sep=thetamin, max_sep=thetamax, nbins = nthetabins, bin_slop=bin_slop, bin_type=bin_type,sep_units='degrees')
    #nn.process(cat1)
    #dr.process(cat1,cat2)
    #rr.process(cat2)
    #rd.process(cat2,cat1)
    #xi,varxi = nn.calculateXi(rr,dr,rd)
    #x = nn.meanr
    #y = xi
    #np.savetxt('./output/angshell/angcorr_%d.txt'%seed_num,np.array([x,y,varxi]).transpose())

#if __name__ == '__main__':
    #name = MPI.Get_processor_name()
    #rank = MPI.COMM_WORLD.Get_rank()
    #size = MPI.COMM_WORLD.Get_size()
    #seed = rank
    #print(rank)
    #corr_fun()

corr_fun()
