#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 16:50:38 2018

@author: victorh
"""

############# Important notes #################################################
# database_config.py must be executed first follow by the file call.py, which 
# contains the required loop to run the calculations constantly.
# File database_config.py contains the initial value configuration for the 
# calculations, creates the database structure (required tables), provides the 
# initial conditions for the observer x0 and the initial Cov. matrix of the
# estimation error P0=Q*200. 
# Observer.py contains the required observer calculations
##############################################################################

import mysql.connector
import numpy as np

# Create Observer's and matrix P tables
mydb=mysql.connector.Connect(host="localhost", user="root", passwd="admin",database='MySQLDB')
mycursor=mydb.cursor()
mycursor.execute('DROP TABLE IF EXISTS Observerf');
mycursor.execute('DROP TABLE IF EXISTS Ptable');
mycursor.execute('DROP TABLE IF EXISTS OBSEKF');

# Observer table (use for visualization)
mycursor.execute('CREATE TABLE Observerf (id INT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY, variable TEXT, varvalues DOUBLE(10,5) DEFAULT NULL, dt_created timestamp DEFAULT CURRENT_TIMESTAMP)')
# Table for P matrix
mycursor.execute('CREATE TABLE Ptable (col1 FLOAT,col2 FLOAT,col3 FLOAT)')
#  Auxiliar Table that provides the data for EKF calculations
mycursor.execute('CREATE TABLE OBSEKF (id INT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY, variable TEXT, varvalues DOUBLE(10,5) DEFAULT NULL, dt_created timestamp DEFAULT CURRENT_TIMESTAMP)')


# Fill the auxiliar table with some Initial Condition values

mydb=mysql.connector.Connect(host="localhost", user="root", passwd="admin",database='MySQLDB')
result1=[('temp1_Obs',283),('temp3_Obs',283),('kA_Obs',5)] # Temp. in Kelvin
sql_insert_query = """INSERT INTO OBSEKF (variable,varvalues) VALUES (%s,%s)"""
mycursor=mydb.cursor()
mycursor.executemany(sql_insert_query,result1)
mydb.commit()

# Save the initial P matrix
Q=np.diag(([10**(-6),10**(-6),10**(-6)])) #Tuned Matrix with the best performance on a real plant
P0=Q*200
mydb=mysql.connector.Connect(host="localhost", user="root", passwd="admin",database='MySQLDB')
result2=P0.tolist()
sql_insert_query = "INSERT INTO Ptable (col1,col2,col3) VALUES (%s,%s,%s)"
mycursor=mydb.cursor()
mycursor.executemany(sql_insert_query,result2)
mydb.commit()
