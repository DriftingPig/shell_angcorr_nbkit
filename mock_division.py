#make a bunch of angular correlatioon function data for future processing
import bigfile
import random
import treecorr
import numpy as np
from astropy.table import Table
import multiprocessing as mp

import os
outdir=os.environ["outdir"]
shell_outdir=os.environ["shell_outdir"]
tot_mock=int(os.environ["tot_mock"])


def angcorr_data(tot_num,fn=outdir):
    f=bigfile.File(fn)
    data = bigfile.Dataset(f,['z','ra','dec'])
    width=0.03
    z_ave=0.3
    delta_z=width*(1+z_ave)
    zmax=z_ave+delta_z/2.
    zmin=z_ave-delta_z/2.
    
    z=data['z'][:]
    ra=data['ra'][:]
    dec=data['dec'][:]

    sel1=(z>zmin)&(z<zmax)
    
    z=z[sel1]
    ra=ra[sel1]
    dec=dec[sel1]
    
    List=np.arange(len(ra))
    random.shuffle(List)
    lists=np.array_split(List,tot_num)
    
    counter=0
    p = mp.Pool(30)

    t=Table()
    t['ra']=ra
    t['dec']=dec
    t['z']=z
    #make a wrap of all the parameters
    inputs=list()
    counter=0
    for one_list in lists:
        inputs.append((counter,tot_num,t,one_list))
        counter+=1
    p.map(angcorr_data_one,inputs)


def test(X):
    (chunk_num,tot_num,t_array,one_list)=X
    print(chunk_num)

def angcorr_data_one(X):
    (chunk_num,tot_num,t_array,one_list)=X
    print(chunk_num)
    t=Table()
    t['ra']=t_array['ra'][np.array(one_list)]
    t['dec']=t_array['dec'][np.array(one_list)]
    t['z']=t_array['z'][np.array(one_list)]
    t.write(shell_outdir+'/angcorr%d.fits'%chunk_num,overwrite=True)

angcorr_data(tot_mock)
