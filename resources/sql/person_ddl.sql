-- create TBL_PERSON table

CREATE TABLE TBL_PERSON
(
    ID                 NUMBER(19) NOT NULL PRIMARY KEY,
    FIRST_NAME         VARCHAR2(200) NOT NULL,
    LAST_NAME        VARCHAR2(200) NOT NULL,
    NATIONAL_ID        VARCHAR2(50) NOT NULL,
    PHONE_NUMBER SDO_GEOMETRY,
    MOBILE_NUMBER  VARCHAR2(50),
    FATHER_NAME   VARCHAR2(100),
    BIRTHDAY   TIMESTAMP,
    ADDRESS   VARCHAR2(4000) NOT NULL
);

-- create sequence for TBL_PERSON
declare
v_sql LONG;
begin
    v_sql
:= '
        CREATE SEQUENCE TBL_PERSON_SEQ START WITH 1
    ';
execute immediate v_sql;

EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE = -955 THEN
            NULL; -- suppresses ORA-00955
ELSE
            RAISE;
END IF;
END;


