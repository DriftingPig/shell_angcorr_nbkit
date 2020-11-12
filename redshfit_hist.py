import astropy.io.fits as fits
import matplotlib.pyplot as plt
import numpy as np

import os

shell_outdir=os.environ['shell_outdir']
tot_mock=int(os.environ["tot_mock"])
nbins=50

z_bin=np.zeros(nbins)

for i in range(tot_mock):
    dat = fits.getdata(shell_outdir+'/angcorr%d.fits'%i)
    z=dat['z']
    n,bins,_=plt.hist(z,bins=nbins,range=(0.27,0.33),density=True)
    x=(bins[1:]+bins[:-1])/2
    z_bin+=x
z_bin/=float(tot_mock)

np.savetxt(shell_outdir+'/redshft.txt',np.array([z_bin,n]).transpose())


z_bin=np.zeros(nbins)
for i in range(tot_mock):
    dat = fits.getdata(shell_outdir+'/rsd_angcorr%d.fits'%i)
    z=dat['z']
    n,bins,_=plt.hist(z,bins=nbins,range=(0.27,0.33),density=True)
    x=(bins[1:]+bins[:-1])/2
    z_bin+=x
z_bin/=float(tot_mock)

np.savetxt(shell_outdir+'/rsd_redshft.txt',np.array([z_bin,n]).transpose())
