# Databricks notebook source
# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMP VIEW hosa_encounters
# MAGIC USING parquet
# MAGIC OPTIONS (path "dbfs:/mnt/bronze/hosa/encounters");
# MAGIC
# MAGIC CREATE OR REPLACE TEMP VIEW hosb_encounters
# MAGIC USING parquet
# MAGIC OPTIONS (path "dbfs:/mnt/bronze/hosb/encounters");
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMP VIEW encounters AS
# MAGIC SELECT * FROM hosa_encounters
# MAGIC UNION ALL
# MAGIC SELECT * FROM hosb_encounters;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMP VIEW quality_checks AS
# MAGIC SELECT 
# MAGIC   CONCAT(EncounterID, '-', datasource) AS EncounterID,
# MAGIC   EncounterID AS SRC_EncounterID,
# MAGIC   PatientID,
# MAGIC   EncounterDate,
# MAGIC   EncounterType,
# MAGIC   ProviderID,
# MAGIC   DepartmentID,
# MAGIC   ProcedureCode,
# MAGIC   InsertedDate AS SRC_InsertedDate,
# MAGIC   ModifiedDate AS SRC_ModifiedDate,
# MAGIC   datasource,
# MAGIC   CASE 
# MAGIC     WHEN EncounterID IS NULL OR PatientID IS NULL THEN TRUE
# MAGIC     ELSE FALSE
# MAGIC   END AS is_quarantined
# MAGIC FROM encounters;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC CREATE SCHEMA IF NOT EXISTS silver;
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS silver.encounters (
# MAGIC   EncounterID STRING,
# MAGIC   SRC_EncounterID STRING,
# MAGIC   PatientID STRING,
# MAGIC   EncounterDate DATE,
# MAGIC   EncounterType STRING,
# MAGIC   ProviderID STRING,
# MAGIC   DepartmentID STRING,
# MAGIC   ProcedureCode INTEGER,
# MAGIC   SRC_InsertedDate DATE,
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
# MAGIC MERGE INTO silver.encounters AS target
# MAGIC USING quality_checks AS source
# MAGIC ON target.EncounterID = source.EncounterID AND target.is_current = TRUE
# MAGIC WHEN MATCHED AND (
# MAGIC   target.SRC_EncounterID != source.SRC_EncounterID OR
# MAGIC   target.PatientID != source.PatientID OR
# MAGIC   target.EncounterDate != source.EncounterDate OR
# MAGIC   target.EncounterType != source.EncounterType OR
# MAGIC   target.ProviderID != source.ProviderID OR
# MAGIC   target.DepartmentID != source.DepartmentID OR
# MAGIC   target.ProcedureCode != source.ProcedureCode OR
# MAGIC   target.SRC_InsertedDate != source.SRC_InsertedDate OR
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
# MAGIC MERGE INTO silver.encounters AS target
# MAGIC USING quality_checks AS source
# MAGIC ON target.EncounterID = source.EncounterID AND target.is_current = TRUE
# MAGIC WHEN NOT MATCHED THEN
# MAGIC INSERT (
# MAGIC   EncounterID,
# MAGIC   SRC_EncounterID,
# MAGIC   PatientID,
# MAGIC   EncounterDate,
# MAGIC   EncounterType,
# MAGIC   ProviderID,
# MAGIC   DepartmentID,
# MAGIC   ProcedureCode,
# MAGIC   SRC_InsertedDate,
# MAGIC   SRC_ModifiedDate,
# MAGIC   datasource,
# MAGIC   is_quarantined,
# MAGIC   audit_insertdate,
# MAGIC   audit_modifieddate,
# MAGIC   is_current
# MAGIC )
# MAGIC VALUES (
# MAGIC   source.EncounterID,
# MAGIC   source.SRC_EncounterID,
# MAGIC   source.PatientID,
# MAGIC   source.EncounterDate,
# MAGIC   source.EncounterType,
# MAGIC   source.ProviderID,
# MAGIC   source.DepartmentID,
# MAGIC   source.ProcedureCode,
# MAGIC   source.SRC_InsertedDate,
# MAGIC   source.SRC_ModifiedDate,
# MAGIC   source.datasource,
# MAGIC   source.is_quarantined,
# MAGIC   current_timestamp(),
# MAGIC   current_timestamp(),
# MAGIC   TRUE
# MAGIC );
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT SRC_EncounterID, datasource, COUNT(PatientID) AS patient_count
# MAGIC FROM silver.encounters
# MAGIC GROUP BY SRC_EncounterID, datasource
# MAGIC ORDER BY patient_count DESC;
# MAGIC