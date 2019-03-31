# Extended-Kalman-Filter-Python
Implementation of extended kalman filter to realize an Observer of a chemical reactor.

## Requirements
### 1. Install Python v3
Windows

   Download python from at python.org. and run the installer.

Linux

   First check current installed python version. If the version lower than 3.6, proceed to install.
    
    sudo apt-get update
    sudo apt-get install python3.6

### 2. Install MySQL
First it is necessary to install MySQL to store the data to be manipulated on the EKF algorithm.
Install MySQL (Create password, the one given on the scripts: admin):
1. sudo apt-get update
2. sudo apt-get install mysql-server

### 3. Run the programs
Check the folders on this repository:
1. Plant Information (Theory): Theoretical information of the plant used on the Extended kalman filter implementation (dynamics).
2. Python Scripts: Extended kalman filter scripts to be executed.
