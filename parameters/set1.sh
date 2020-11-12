#!/bin/bash -l

export config_width=0.03
export config_redshift=0.3
export config_omega_m=0.25
export config_omega_b=0.044
export config_h=0.7
export config_ns=0.95
export config_sigma8=0.8
export config_bias=1.0
export outdir="../output/mocks1/mock.bigfile"
export shell_outdir="../output/mocks1/angcorr_data/"
export angcorr_outdir="../output/mocks1/angcorr_result/"
export tot_mock=100
export density=0.003
export seed=0

mkdir -p $shell_outdir
mkdir -p $angcorr_outdir
