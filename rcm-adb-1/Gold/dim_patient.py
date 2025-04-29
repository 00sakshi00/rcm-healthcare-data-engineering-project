# Databricks notebook source
# MAGIC %sql
# MAGIC create schema if not exists gold;
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS gold.dim_patient (
# MAGIC   patient_key STRING,
# MAGIC   src_patientid STRING,
# MAGIC   firstname STRING,
# MAGIC   lastname STRING,
# MAGIC   middlename STRING,
# MAGIC   ssn STRING,
# MAGIC   phonenumber STRING,
# MAGIC   gender STRING,
# MAGIC   dob DATE,
# MAGIC   address STRING,
# MAGIC   datasource STRING
# MAGIC );
# MAGIC

# COMMAND ----------

# MAGIC %sql 
# MAGIC -- TRUNCATE TABLE gold.dim_patient;

# COMMAND ----------

# MAGIC %sql
# MAGIC INSERT INTO gold.dim_patient
# MAGIC SELECT
# MAGIC   patient_key,
# MAGIC   src_patientid,
# MAGIC   firstname,
# MAGIC   lastname,
# MAGIC   middlename,
# MAGIC   ssn,
# MAGIC   phonenumber,
# MAGIC   gender,
# MAGIC   dob,
# MAGIC   address,
# MAGIC   datasource
# MAGIC FROM silver.patients
# MAGIC WHERE is_current = TRUE AND is_quarantined = FALSE;
# MAGIC