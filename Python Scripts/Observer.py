
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 16:07:56 2018

@author: victorh
"""

############# Important notes #################################################
# database_config.py must be executed first follow by the file call.py, which 
# contains the required loop to run the calculations constantly.
# File database_config.py contains the initial value configuration for the 
# calculations, creates the database structure (required tables), provides the 
# initial conditions for the observer x0 and the initial Cov. matrix of the
# estimation error P0=Q*200. 
##############################################################################

import numpy as np
import mysql.connector


################  Functions ###################################################

############ Model of the plant ############

def reactor(x,dt,TJina):
    # x = State vector 
    # (x,TJin,h,t_sample)
    # TJina = Input temp. jacket
    # dt = Discrete time approx.
    
    # States (3):
    # x[0]=TR, temp. on the reactor
    # x[1]=TJ, temp. on the jacket
    # x[2]=kA, Heat coeff.

    # Parameters:
    pi = 3.141592653589793
    tdt = dt                    # rename of variable dt -> tdt (INPUT)
    TJin=TJina                  # rename of variable TJina -> TJin (INPUT)
    
    cpR = 4200                  # J/Kg*K, Specific heat capacity of the liquid on R, (WATER)
    d_R = 0.1                   # Diameter of the reactor R (m)
    h_R = 0.115                 # Medium level of reaction liquid in the reactor
    ABase = (pi/4)*((d_R)**2)   # Area Base of reactor
    ACylinder = pi*d_R*h_R      # Area Body Reactor
    Ar=ABase+ACylinder          # Full Area of Reactor, 0.0439822971502571 m2
    VR = ABase*h_R              # M³, volume of reactor
    rhoR = 1000                 # Kg/m3, density of the liquid in the reactor (WATER)
    mR=VR*rhoR                  # Kg, mass of liquid in reactor, 0.9Kg, suggested 1Kg
    
     
    cpJ = 1700                   # J/Kg*K, Specific heat capacity of the liquid on J, (OIL)
    VJ=0.0015                    # m³, volumen of the liquid in the Jacket, 1.5L
    rhoJ = 970                  # Kg/m3, density of liquid in the Jacket
    mJ=VJ*rhoJ                  # Kg, mass of the liquid in the Jacket, 1.35Kg, suggested 1.5Kg
    mJin_dot=0.05               # Mass flow rate enter the jacket

    Te= 285                     # Temperature environment
    kAout=3.5                   # W/K
    # Futher assumptions: TJ=TJout

    
    # STATE SPACE MODEL
    xa = np.array([[x[0,0]+(1/(mR*cpR))*tdt*((x[1,0]-x[0,0]))],
                     [x[1,0]+(1/(mJ*cpJ))*tdt*(mJin_dot*cpJ*(TJin-x[1,0]) - x[2,0]*Ar*(x[1,0]-x[0,0]) -kAout*(x[1,0]-Te) )],
                     [x[2,0]]]) # Estimate the state vector

    x=xa # Update vector of states with the estimated values.
    
    # JACOBIAN OF DISCRETIZED SYSTEM
    A = np.array([[1 - (1/(mR*cpR))*tdt,(1/(mR*cpR))*tdt,0],
                 [(1/(mJ*cpJ))*tdt*x[2,0]*Ar,  1-((1/(mJ*cpJ))*tdt*(mJin_dot*cpJ+x[2,0]*Ar+kAout)), (-1/(mJ*cpJ))*tdt*Ar*(x[1,0]-x[0,0])],
                 [0,0,1]])
    
    return [A,x]

####### Extended Kalman Filter ############
def EKF(data):
    TJin = data[0]              # Temp Jacket In
    Q = data[1]                 # Cov. matrix Model/process noise
    R_o = data[2]               # Cov. matrix of Measurement (sensor) noise 
    C = data[3]                 # Output matrix
    y = data[4]                 # Measurements from the plant, TR and TJ
    tdt = data[5]               # Discretization time
    x = (data[6]).reshape(-1,1) #Initial or previous conditions for Observer
    P = data[7]                 # Cov. matrix of the estimation error
    
    # Measurement update / Correction step
    Ctrans  = np.transpose(C)
    Kaux    = C.dot(P).dot(Ctrans)
    Kinv    = np.linalg.inv( Kaux+ R_o)
    K       = P.dot( Ctrans).dot(Kinv)
    x       = x+(K.dot((y.reshape(-1,1))-C.dot(x)))
    P       = ((np.eye(3)-K.dot(C)).dot(P))
    
    
    # State values of the Observer (Output of EKF)
    ystate=(C.dot(x)).T
    statev=(x).T
    
    # Time update / Prediction step
    L=reactor(x,tdt,TJin)  # Solve xdot=A*x
    A=L[0]
    x=L[1]
    Atrans = np.transpose(A)
    Pprime = (A.dot(P)).dot(Atrans)
    PprimeQ = Pprime + Q
    P = PprimeQ
    #print(x)
    
    # write matrix P on database for later use
    mydb=mysql.connector.Connect(host="localhost", user="root", passwd="admin",database='MySQLDB')
    mycursor=mydb.cursor()
    
    Delete_all_query = """truncate table Ptable """
    mycursor.execute(Delete_all_query)
    mydb.commit()
    
    #mycursor.execute('DROP TABLE IF EXISTS Ptable');
    #mycursor.execute('CREATE TABLE Ptable (col1 FLOAT,col2 FLOAT,col3 FLOAT)')
    result2=P.tolist()
    sql_insert_query = "INSERT INTO Ptable (col1,col2,col3) VALUES (%s,%s,%s)"
    mycursor=mydb.cursor()
    mycursor.executemany(sql_insert_query,result2)
    mydb.commit()
    
    # Save vector "x" from time update step for the next EKF iteration
    mydb=mysql.connector.Connect(host="localhost", user="root", passwd="admin",database='MySQLDB')
    mycursor=mydb.cursor()
    result3=[('TR_Obs',x[0][0].tolist()),('TJ_Obs',x[1][0].tolist()),('kA_Obs',x[2][0].tolist())]
    sql_insert_query = """INSERT INTO OBSEKF (variable,varvalues) VALUES (%s,%s)"""
    mycursor=mydb.cursor()
    mycursor.executemany(sql_insert_query,result3)
    mydb.commit()
    
    # Output of EKF function
    return[ystate,statev]

#### Function to write resulting values from the observer on the database ####

def write_data(TR_Obs,TJ_Obs,kA_Obs):
    mydb=mysql.connector.Connect(host="localhost", user="root", passwd="admin",database='MySQLDB')
   
    result1=[('TR_Obs',TR_Obs - 273), # Change temp. units of TR back to °C
             ('TJ_Obs',TJ_Obs - 273), # Change temp. units of TJ back to °C
             ('kA_Obs',kA_Obs)]
    sql_insert_query = """INSERT INTO Observerf (variable,varvalues) VALUES (%s,%s)"""
    mycursor=mydb.cursor(prepared=True)
    mycursor.executemany(sql_insert_query,result1)
    mydb.commit()    
    
    
###################### End of Auxiliary functions #############################
    
    
############################ Beginning of Main Program ########################

##### Obtain data from the plant #########

mydb = mysql.connector.Connect(host="localhost", user="root", passwd="admin",
                               database='MySQLDB')
#TR
mycursor = mydb.cursor()
mycursor.execute("SELECT varvalues FROM mappedsensors WHERE variable='TR'")
y1 = mycursor.fetchall()
y1=np.asarray(y1)
y1_last=y1[-1] + 273     # Change temp. units to K

#TJ_in
mycursor = mydb.cursor()
mycursor.execute("SELECT varvalues FROM mappedsensors WHERE variable='TJin'")
y2 = mycursor.fetchall()
y2=np.asarray(y2)
y2_last=y2[-1] + 273    # Change temp. units to K

# TJ
mycursor = mydb.cursor()
mycursor.execute("SELECT varvalues FROM mappedsensors WHERE variable='TJ'")
y3 = mycursor.fetchall()
y3=np.asarray(y3)
y3_last=y3[-1] + 273   # Change temp. units to K


y_last=np.concatenate((y1_last,y3_last))

# Rename Measurement of the input as TJin
TJin=y2_last

###### Create Observer Structure ##########

n = 3 #Number of states [TR,TJ,kA]
m = 1 #Number of inputs [TJin]

# Time for model discretization
tdt  = 1  

Caux = np.eye(n) 
C=np.array([Caux[0,:],Caux[1,:]]) #Output read from the plant (2 states TR,TJ)

#Measurement noise matrix
R_o = np.diag(([0.0001**2,0.0001**2])) #Tuned matrix with the best performance tested on a real plant

#Plant noise matrix
Q=np.diag(([10**(-6),10**(-6),10**(-6)])) #Tuned matrix with the best performance tested on a real plant

#P: Matrix of initial error
#P0=Q*200, initially taken from database
mydb = mysql.connector.Connect(host="localhost", user="root", passwd="admin",
                               database='MySQLDB')
mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM Ptable")
col= mycursor.fetchall()
P=np.asarray(col)


#Read initial/previous state values from the Time update / Prediction step of EKF
mydb = mysql.connector.Connect(host="localhost", user="root", passwd="admin",
                               database='MySQLDB')
#TR_Obs initial
mycursor = mydb.cursor()
mycursor.execute("SELECT varvalues FROM OBSEKF WHERE variable='TR_Obs'")
y1_0 = mycursor.fetchall()
y1_0=np.asarray(y1_0)
y1_0_last=y1_0[-1]

#TJ_Obs
mycursor = mydb.cursor()
mycursor.execute("SELECT varvalues FROM OBSEKF WHERE variable='TJ_Obs'")
y2_0 = mycursor.fetchall()
y2_0=np.asarray(y2_0)
y2_0_last=y2_0[-1]

#kA_Obs
mycursor = mydb.cursor()
mycursor.execute("SELECT varvalues FROM OBSEKF WHERE variable='kA_Obs'")
y3_0 = mycursor.fetchall()
y3_0=np.asarray(y3_0)
y3_0_last=y3_0[-1]


# Vector of Initial/previous Conditions
#x0b=[TR,TJ,kA]
x0b=np.array([[y1_0_last,y2_0_last,y3_0_last]])


############ EKF ##########


data=[TJin,Q,R_o,C,y_last,tdt,x0b,P]  #Organize data for EKF
ans=EKF(data)                         # Call EKF Function

# Save answer from EKF
yest=ans[0]
x_st=ans[1]

##### Compare data Plant vs Observer ###
TR_meas=y_last[0]
TR_Obs=x_st[0,0]
TJ_meas=y_last[1]
TJ_Obs=x_st[0,1]
kA_Obs=x_st[0,2]

print("Plant output: ")
print(y_last-273)
print("Obs output: ")
print(x_st[0,0]-273)
print(x_st[0,1]-273)
print(x_st[0,2])

##################

# Save the calculated data for the observer on database for future visualization
write_data(TR_Obs,TJ_Obs,kA_Obs)

################# End of Main program #########################################
