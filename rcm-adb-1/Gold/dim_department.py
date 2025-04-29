# Databricks notebook source
# MAGIC %md
# MAGIC ###Step 1: Create the Gold Table If It Doesn't Exist

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS gold;
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS gold.dim_department (
# MAGIC   Dept_Id STRING,
# MAGIC   SRC_Dept_Id STRING,
# MAGIC   Name STRING,
# MAGIC   datasource STRING
# MAGIC );
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- TRUNCATE TABLE gold.dim_department;

# COMMAND ----------

# MAGIC %md
# MAGIC ###Step 3: Insert Distinct Clean Records from Silver

# COMMAND ----------

# MAGIC %sql
# MAGIC INSERT INTO gold.dim_department
# MAGIC SELECT DISTINCT
# MAGIC   Dept_Id,
# MAGIC   SRC_Dept_Id,
# MAGIC   Name,
# MAGIC   datasource
# MAGIC FROM silver.departments
# MAGIC WHERE is_quarantined = FALSE;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM gold.dim_department;