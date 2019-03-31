## Script execution and performance 

After obtaining some measurements from the plant and save them on a database table (e.g. mappedsensors table):
1. Run: database_config.py.
On this script are defined the require database's tables for the observer, namely:
1.1. Observer table (i.e. Observerf): That stores the estimated states values for use.
1.2. P matrix table (i.e. Ptable): Define an initial matrix for the estimate error covariance for the EKF operation.
1.3. Auxiliary table (i.e. OBSEKF): Table that saves the intermediate results of the time update step of the EKF and it is fill at first with the initial (randomly picked) conditions of the system (TRObs=20°C, TJObs=20°C, Kin=5W/K).
2. Once the previous step is done (regarding the configuration of the database tables) execute call.py, which executes on a infinite loop the observer script which takes care of the EKF computation based on the last value of the sensor readings on a database table (mentioned before, e.g. mappedsensors).  
