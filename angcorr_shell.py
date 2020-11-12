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
    for i in range(ntot):
         cat = LogNormalCatalog(Plin=Plin, nbar=density, BoxSize=1500, Nmesh=512, bias=b1, seed=12345*seed+i)
         arr_cat = cat.Position().compute()
         ra,dec,z = transform.CartesianToSky(cat.Position(),cosmo=cosmo2,observer=[0, 0, 0])
         cat['ra'] = ra
         cat['dec'] = dec
         cat['z'] = z
         print(cat.columns)
         cat.save(outdir+'mock%d.bigfile'%i,columns=cat.columns)

corr_fun()
