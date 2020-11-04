this code can make hundreds of angular correlation functions 

prep:
mkdir mockcorr
mkdir code
cd code
git clone ....

first, make a parameter set in ./parameter/ folder like set0.sh

then, run (change number of nodes used as you change the size of the mock you make)

sbatch angcorr_shell.sh

after finish,run
(you will need to make a conda environment with nbodykit,astropy,numpy in it, then change that 'cfastpm' to the one you make)

sbatch mock_division.sh

after finish, run
(you will need to make an environment with treecorr,astropy,numpy in it, and it MUST NOT have nbodykit, then change the 'corr' to the one you make)
(the the number of nodes used if size get larger)

sbatch angcorr_cal.sh



