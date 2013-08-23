#! /bin/sh
VE=env
PREFIX=$HOME/Documents/01-Downloads_Tracker/dvd-1.0/$VE

# Set environtment variables for compilation
# export PYTHONPATH=$PREFIX/lib/python2.7/site-packages
# export LD_LIBRARY_PATH=$PREFIX/lib64


# Recreate the virtualenv & activate it
rm -fr $PREFIX
virtualenv $VE
. $PREFIX/bin/activate

# Install bdb
cd pkg

V=6.0.20
tar -xzvf db-$V.tar.gz
cd db-$V
cd build_unix
../dist/configure --prefix=$PREFIX
make && make install
cd ../..
rm -fr db-$V

cd ..

BERKELEYDB_DIR=$PREFIX pip install bsddb3

pip install numpy
pip install matplotlib

#pip install http://downloads.sourceforge.net/project/matplotlib/matplotlib-toolkits/basemap-1.0.6/basemap-1.0.6.tar.gz
#pip install pygeoip

pip install pyzmq
pip install tornado
pip install ipython
