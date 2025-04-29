# Databricks notebook source
# MAGIC %sql
# MAGIC
# MAGIC CREATE schema IF NOT EXISTS gold;
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS gold.dim_provider (
# MAGIC   ProviderID STRING,
# MAGIC   FirstName STRING,
# MAGIC   LastName STRING,
# MAGIC   DeptID STRING,
# MAGIC   NPI LONG,
# MAGIC   datasource STRING
# MAGIC );
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- TRUNCATE TABLE gold.dim_provider;

# COMMAND ----------

# MAGIC %sql
# MAGIC INSERT INTO gold.dim_provider
# MAGIC SELECT
# MAGIC   ProviderID,
# MAGIC   FirstName,
# MAGIC   LastName,
# MAGIC   CONCAT(DeptID, '-', datasource) AS DeptID,
# MAGIC   NPI,
# MAGIC   datasource
# MAGIC FROM silver.providers
# MAGIC WHERE is_quarantined = FALSE;
# MAGIC