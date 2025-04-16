-- create message log table
create table GIS.TBL_PARCEL_REQ_LOG
(
  ID                  NUMBER(10),
  NATIONAL_ID         VARCHAR2(50 CHAR),
  FIRST_NAME         VARCHAR2(400 CHAR),
  LAST_NAME         VARCHAR2(400 CHAR),
  STATE_CODE        VARCHAR2(5 CHAR),
  CMS               VARCHAR2(10 CHAR),
  SEARCH_POINT        MDSYS.SDO_GEOMETRY,
  request_timestamp   DATE,
  PARAMS            CLOB
);



-- create PK for message log table
declare
    v_sql LONG;
begin

    v_sql := '
ALTER TABLE GIS.TBL_PARCEL_REQ_LOG ADD (
CONSTRAINT TBL_PARCEL_REQ_PK PRIMARY KEY (ID))
';
    execute immediate v_sql;

EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE = -2260 THEN
            NULL; -- suppresses ORA-2260
        ELSE
            RAISE;
        END IF;
END;



-- create seq message log table
declare
    v_sql LONG;
begin

    v_sql := '
                CREATE SEQUENCE GIS.TBL_PARCEL_REQ_SEQ START WITH 1
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



-- create trigger for TBL_MESSAGE_LOG_SEQ
CREATE OR REPLACE TRIGGER TBL_PARCEL_REQ_TRIGGER
    BEFORE INSERT
    ON TBL_PARCEL_REQ_LOG
    FOR EACH ROW

BEGIN
    SELECT TBL_PARCEL_REQ_SEQ.NEXTVAL
    INTO :new.ID
    FROM dual;
END;


