-- Superuser: qlkcl_superuser
CREATE ROLE qlkcl_superuser WITH
	LOGIN
	SUPERUSER
	CREATEDB
	CREATEROLE
	INHERIT
	NOREPLICATION
	CONNECTION LIMIT -1
	PASSWORD '123456';

-- Database: qlkcl

-- DROP DATABASE qlkcl;

CREATE DATABASE qlkcl
    WITH 
    OWNER = qlkcl_superuser
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;