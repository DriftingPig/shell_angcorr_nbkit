import astropy.io.fits as fits
import matplotlib.pyplot as plt
import numpy as np

import os

shell_outdir=os.environ['shell_outdir']
tot_mock=int(os.environ["tot_mock"])
nbins=20

z_bin=np.zeros(nbins)

for i in range(tot_mock):
    dat = fits.getdata(shell_outdir+'/angcorr%d.fits'%i)
    z=dat['z']

    n,bins,_=plt.hist(z,bins=nbins,density=True)
    x=(bins[1:]+bins[:-1])/2
    z_bin+=x
z_bin/=float(nbins)

np.savetxt(shell_outdir+'/redshft.txt',np.array([x,n,n]).transpose())
