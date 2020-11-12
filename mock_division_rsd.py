#make a bunch of angular correlatioon function data for future processing
import bigfile
import dask.array as da
import random
import treecorr
import numpy as np
from astropy.table import Table
import multiprocessing as mp
import astropy.io.fits as fits
import os
from nbodykit.lab import *
from astropy.table import Table
import dask.array as da

outdir=os.environ["outdir"]
shell_outdir=os.environ["shell_outdir"]
tot_mock=int(os.environ["tot_mock"])
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
seed=int(os.environ['seed'])  
boxsize=1500
rsd = bool(os.environ['rsd'])

def angcorr_data(tot_num):
    inputs=np.arange(tot_num)
    p = mp.Pool(30)
    p.map(angcorr_data_one,inputs)
    if rsd:
       p.map(rsd_data_one,inputs)



def angcorr_data_one(idx):
    fn=outdir+'mock%d.bigfile'%idx
    f=bigfile.File(fn)
    data = bigfile.Dataset(f,['z','ra','dec','Position','VelocityOffset'])
    zmax=z_ave+delta_z/2.
    zmin=z_ave-delta_z/2.

    z=data['z'][:]
    ra=data['ra'][:]
    dec=data['dec'][:]
    X=data['Position'][:][:,0]
    Y=data['Position'][:][:,1]
    Z=data['Position'][:][:,2]
    sel0=(z>zmin-0.03)&(z<zmax+0.03)
    sel1=(z>zmin)&(z<zmax)
    z1=z[sel1]
    ra1=ra[sel1]
    dec1=dec[sel1]
    X1=X[sel1]
    Y1=Y[sel1]
    Z1=Z[sel1]

    print(idx)
    t=Table()
    t['ra']=ra1
    t['dec']=dec1
    t['z']=z1
    t['X']=X1
    t['Y']=Y1
    t['Z']=Z1
    t.write(shell_outdir+'/angcorr%d.fits'%idx,overwrite=True)
    
    if rsd:
        vx=data['VelocityOffset'][:][:,0]
        vy=data['VelocityOffset'][:][:,1]
        vz=data['VelocityOffset'][:][:,2]
    
        z0=z[sel0]
        ra0=ra[sel0]
        dec0=dec[sel0]
        X0=X[sel0]
        Y0=Y[sel0]
        Z0=Z[sel0]
        vx0=vx[sel0]
        vy0=vy[sel0]
        vz0=vz[sel0]
        t2=Table()
        t2['true_ra']=ra0
        t2['true_dec']=dec0
        t2['true_z']=z0
        t2['true_X']=X0
        t2['true_Y']=Y0
        t2['true_Z']=Z0
        t2['Vx']=vx0
        t2['Vy']=vy0
        t2['Vz']=vz0
        t2.write(shell_outdir+'/rsd_angcorr%d.fits'%idx,overwrite=True)




def rsd_data_one(idx):
    print(idx)
    data = fits.getdata(shell_outdir+'/rsd_angcorr%d.fits'%idx)
    X=data['true_X']
    Y=data['true_Y']
    Z=data['true_Z']
    R = np.sqrt(X**2+Y**2+Z**2)
    mu_x = X/R
    mu_y = Y/R
    mu_z = Z/R
    Vx=data['Vx']
    Vy=data['Vy']
    Vz=data['Vz']

    R_new = mu_x*Vx + mu_y*Vy+ mu_z*Vz + R
    rsdposition_x = R_new*mu_x
    rsdposition_y = R_new*mu_y
    rsdposition_z = R_new*mu_z

    rsdposition = np.array([rsdposition_x,rsdposition_y,rsdposition_z]).transpose()
    rsdposition = da.from_array(rsdposition,chunks=(100,3))
    cosmo = cosmology.cosmology.Cosmology(h=h,Omega0_b=omega_b,Omega0_cdm=omega_m-omega_b,n_s=ns)
    cosmo2=cosmo.match(sigma8=sigma8)
    Plin = cosmology.LinearPower(cosmo2, redshift, transfer='EisensteinHu')

    ra,dec,z = transform.CartesianToSky(rsdposition,cosmo=cosmo2,observer=[0, 0, 0])
    zmax=z_ave+delta_z/2.
    zmin=z_ave-delta_z/2.
    sel1=(z>zmin)&(z<zmax)
    ra=ra[sel1]
    dec=dec[sel1]
    z=z[sel1]
    true_ra = data['true_ra'][sel1]
    true_dec = data['true_dec'][sel1]
    true_z = data['true_z'][sel1]
    t=Table()
    t['ra']=ra
    t['dec']=dec
    t['z']=z
    t['true_ra']=true_ra
    t['true_dec']=true_dec
    t['true_z']=true_z
    t.write(shell_outdir+'/rsd_angcorr%d.fits'%idx,overwrite=True)



def uniform_randoms(seed0): 
    dat = fits.getdata(shell_outdir+'/angcorr0.fits')
    ran_L = len(dat)*10
    random_state=np.random.RandomState(seed)
    u1,u2,u3= random_state.uniform(size=(3, ran_L) )
    X = u1*boxsize
    Y = u2*boxsize
    Z = u3*boxsize
    cosmo = cosmology.cosmology.Cosmology(h=h,Omega0_b=omega_b,Omega0_cdm=omega_m-omega_b,n_s=ns)  
    cosmo2=cosmo.match(sigma8=sigma8)   
    Plin = cosmology.LinearPower(cosmo2, redshift, transfer='EisensteinHu')
    random_cat = da.from_array(np.array([X,Y,Z]).transpose(),chunks=(len(dat),3))
    ra,dec,z = transform.CartesianToSky(random_cat,cosmo=cosmo2,observer=[0, 0, 0])  
    zmax = redshift + delta_z/2.
    zmin = redshift - delta_z/2.
    sel = (z.compute()>zmin)&(z.compute()<zmax)
    x_new = X[sel]
    y_new = Y[sel]
    z_new = Z[sel]
    
    t = Table()
    t['X']=x_new
    t['Y']=y_new
    t['Z']=z_new
    t.write(shell_outdir+'/random.fits',overwrite=True)

    

angcorr_data(tot_mock)
# make uniform distributed random
#uniform_randoms(seed)
