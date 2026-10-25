-- Run this script in a local MySQL 8.0+ session authenticated as an administrator.
-- Replace all example passwords before executing; do not use the MySQL root account
-- in the application .env file.

CREATE DATABASE IF NOT EXISTS medical_report_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

CREATE DATABASE IF NOT EXISTS medical_report_test
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

CREATE USER IF NOT EXISTS 'medical_app'@'127.0.0.1'
  IDENTIFIED BY 'replace_with_your_local_password';
CREATE USER IF NOT EXISTS 'medical_app'@'localhost'
  IDENTIFIED BY 'replace_with_your_local_password';
ALTER USER 'medical_app'@'127.0.0.1'
  IDENTIFIED BY 'replace_with_your_local_password';
ALTER USER 'medical_app'@'localhost'
  IDENTIFIED BY 'replace_with_your_local_password';
CREATE USER IF NOT EXISTS 'medical_migrator'@'127.0.0.1'
  IDENTIFIED BY 'replace_with_a_separate_migration_password';
CREATE USER IF NOT EXISTS 'medical_migrator'@'localhost'
  IDENTIFIED BY 'replace_with_a_separate_migration_password';
ALTER USER 'medical_migrator'@'127.0.0.1'
  IDENTIFIED BY 'replace_with_a_separate_migration_password';
ALTER USER 'medical_migrator'@'localhost'
  IDENTIFIED BY 'replace_with_a_separate_migration_password';
CREATE USER IF NOT EXISTS 'medical_test'@'127.0.0.1'
  IDENTIFIED BY 'replace_with_a_separate_test_password';
CREATE USER IF NOT EXISTS 'medical_test'@'localhost'
  IDENTIFIED BY 'replace_with_a_separate_test_password';
ALTER USER 'medical_test'@'127.0.0.1'
  IDENTIFIED BY 'replace_with_a_separate_test_password';
ALTER USER 'medical_test'@'localhost'
  IDENTIFIED BY 'replace_with_a_separate_test_password';

-- The API account receives only the DML privileges needed by the application.
GRANT SELECT, INSERT, UPDATE, DELETE
  ON medical_report_db.* TO 'medical_app'@'127.0.0.1';
GRANT SELECT, INSERT, UPDATE, DELETE
  ON medical_report_db.* TO 'medical_app'@'localhost';

-- Alembic uses a separate account for the version table and schema migrations.
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES, DROP
  ON medical_report_db.* TO 'medical_migrator'@'127.0.0.1';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES, DROP
  ON medical_report_db.* TO 'medical_migrator'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES, DROP
  ON medical_report_test.* TO 'medical_test'@'127.0.0.1';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES, DROP
  ON medical_report_test.* TO 'medical_test'@'localhost';

FLUSH PRIVILEGES;
