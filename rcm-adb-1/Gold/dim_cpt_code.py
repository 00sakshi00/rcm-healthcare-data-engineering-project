# Databricks notebook source
# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS gold;
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS gold.dim_cpt_code (
# MAGIC   cpt_codes STRING,
# MAGIC   procedure_code_category STRING,
# MAGIC   procedure_code_descriptions STRING,
# MAGIC   code_status STRING,
# MAGIC   refreshed_at TIMESTAMP
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC -- TRUNCATE TABLE gold.dim_cpt_code;

# COMMAND ----------

# MAGIC %md
# MAGIC ##Step 3: Insert Current Valid Records from Silver Table

# COMMAND ----------

# MAGIC %sql
# MAGIC INSERT INTO gold.dim_cpt_code
# MAGIC SELECT 
# MAGIC   cpt_codes,
# MAGIC   procedure_code_category,
# MAGIC   procedure_code_descriptions,
# MAGIC   code_status,
# MAGIC   current_timestamp() AS refreshed_at
# MAGIC FROM silver.cptcodes
# MAGIC WHERE is_quarantined = FALSE AND is_current = TRUE;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM gold.dim_cpt_code;