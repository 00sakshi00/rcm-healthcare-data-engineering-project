# Databricks notebook source
claims_df=spark.read.parquet("/mnt/bronze/claims")
claims_df.createOrReplaceTempView("claims")

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from claims

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Quality check view
# MAGIC CREATE OR REPLACE TEMP VIEW quality_checks AS
# MAGIC SELECT 
# MAGIC   CONCAT(ClaimID, '-', datasource) AS ClaimID,
# MAGIC   ClaimID AS SRC_ClaimID,
# MAGIC   TransactionID,
# MAGIC   PatientID,
# MAGIC   EncounterID,
# MAGIC   ProviderID,
# MAGIC   DeptID,
# MAGIC   CAST(ServiceDate AS DATE) AS ServiceDate,
# MAGIC   CAST(ClaimDate AS DATE) AS ClaimDate,
# MAGIC   PayorID,
# MAGIC   ClaimAmount,
# MAGIC   PaidAmount,
# MAGIC   ClaimStatus,
# MAGIC   PayorType,
# MAGIC   Deductible,
# MAGIC   Coinsurance,
# MAGIC   Copay,
# MAGIC   CAST(InsertDate AS DATE) AS SRC_InsertDate,
# MAGIC   CAST(ModifiedDate AS DATE) AS SRC_ModifiedDate,
# MAGIC   datasource,
# MAGIC   CASE 
# MAGIC     WHEN ClaimID IS NULL OR TransactionID IS NULL OR PatientID IS NULL OR ServiceDate IS NULL THEN TRUE
# MAGIC     ELSE FALSE
# MAGIC   END AS is_quarantined
# MAGIC FROM claims;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Create silver.claims Delta table
# MAGIC
# MAGIC CREATE SCHEMA IF NOT EXISTS silver;
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS silver.claims (
# MAGIC   ClaimID STRING,
# MAGIC   SRC_ClaimID STRING,
# MAGIC   TransactionID STRING,
# MAGIC   PatientID STRING,
# MAGIC   EncounterID STRING,
# MAGIC   ProviderID STRING,
# MAGIC   DeptID STRING,
# MAGIC   ServiceDate DATE,
# MAGIC   ClaimDate DATE,
# MAGIC   PayorID STRING,
# MAGIC   ClaimAmount STRING,
# MAGIC   PaidAmount STRING,
# MAGIC   ClaimStatus STRING,
# MAGIC   PayorType STRING,
# MAGIC   Deductible STRING,
# MAGIC   Coinsurance STRING,
# MAGIC   Copay STRING,
# MAGIC   SRC_InsertDate DATE,
# MAGIC   SRC_ModifiedDate DATE,
# MAGIC   datasource STRING,
# MAGIC   is_quarantined BOOLEAN,
# MAGIC   audit_insertdate TIMESTAMP,
# MAGIC   audit_modifieddate TIMESTAMP,
# MAGIC   is_current BOOLEAN
# MAGIC )
# MAGIC USING DELTA;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- SCD Type 2: Update old records
# MAGIC MERGE INTO silver.claims AS target
# MAGIC USING quality_checks AS source
# MAGIC ON target.ClaimID = source.ClaimID AND target.is_current = TRUE
# MAGIC WHEN MATCHED AND (
# MAGIC   target.SRC_ClaimID != source.SRC_ClaimID OR
# MAGIC   target.TransactionID != source.TransactionID OR
# MAGIC   target.PatientID != source.PatientID OR
# MAGIC   target.EncounterID != source.EncounterID OR
# MAGIC   target.ProviderID != source.ProviderID OR
# MAGIC   target.DeptID != source.DeptID OR
# MAGIC   target.ServiceDate != source.ServiceDate OR
# MAGIC   target.ClaimDate != source.ClaimDate OR
# MAGIC   target.PayorID != source.PayorID OR
# MAGIC   target.ClaimAmount != source.ClaimAmount OR
# MAGIC   target.PaidAmount != source.PaidAmount OR
# MAGIC   target.ClaimStatus != source.ClaimStatus OR
# MAGIC   target.PayorType != source.PayorType OR
# MAGIC   target.Deductible != source.Deductible OR
# MAGIC   target.Coinsurance != source.Coinsurance OR
# MAGIC   target.Copay != source.Copay OR
# MAGIC   target.SRC_InsertDate != source.SRC_InsertDate OR
# MAGIC   target.SRC_ModifiedDate != source.SRC_ModifiedDate OR
# MAGIC   target.datasource != source.datasource OR
# MAGIC   target.is_quarantined != source.is_quarantined
# MAGIC )
# MAGIC THEN UPDATE SET
# MAGIC   target.is_current = FALSE,
# MAGIC   target.audit_modifieddate = current_timestamp();
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC MERGE INTO silver.claims AS target
# MAGIC USING quality_checks AS source
# MAGIC ON target.ClaimID = source.ClaimID AND target.is_current = TRUE
# MAGIC WHEN NOT MATCHED THEN
# MAGIC INSERT (
# MAGIC   ClaimID,
# MAGIC   SRC_ClaimID,
# MAGIC   TransactionID,
# MAGIC   PatientID,
# MAGIC   EncounterID,
# MAGIC   ProviderID,
# MAGIC   DeptID,
# MAGIC   ServiceDate,
# MAGIC   ClaimDate,
# MAGIC   PayorID,
# MAGIC   ClaimAmount,
# MAGIC   PaidAmount,
# MAGIC   ClaimStatus,
# MAGIC   PayorType,
# MAGIC   Deductible,
# MAGIC   Coinsurance,
# MAGIC   Copay,
# MAGIC   SRC_InsertDate,
# MAGIC   SRC_ModifiedDate,
# MAGIC   datasource,
# MAGIC   is_quarantined,
# MAGIC   audit_insertdate,
# MAGIC   audit_modifieddate,
# MAGIC   is_current
# MAGIC )
# MAGIC VALUES (
# MAGIC   source.ClaimID,
# MAGIC   source.SRC_ClaimID,
# MAGIC   source.TransactionID,
# MAGIC   source.PatientID,
# MAGIC   source.EncounterID,
# MAGIC   source.ProviderID,
# MAGIC   source.DeptID,
# MAGIC   source.ServiceDate,
# MAGIC   source.ClaimDate,
# MAGIC   source.PayorID,
# MAGIC   source.ClaimAmount,
# MAGIC   source.PaidAmount,
# MAGIC   source.ClaimStatus,
# MAGIC   source.PayorType,
# MAGIC   source.Deductible,
# MAGIC   source.Coinsurance,
# MAGIC   source.Copay,
# MAGIC   source.SRC_InsertDate,
# MAGIC   source.SRC_ModifiedDate,
# MAGIC   source.datasource,
# MAGIC   source.is_quarantined,
# MAGIC   current_timestamp(),
# MAGIC   current_timestamp(),
# MAGIC   TRUE
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM silver.claims;