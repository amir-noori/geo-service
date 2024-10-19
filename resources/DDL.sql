-- create message log table
create table GIS.TBL_MESSAGE_LOG
(
  ID                  NUMBER(10),
  tracking_id         VARCHAR2(255 CHAR),
  service_key         VARCHAR2(255 CHAR),
  source_ip           VARCHAR2(255 CHAR),
  method              VARCHAR2(255 CHAR),
  destination_ip      VARCHAR2(255 CHAR),
  request_url         VARCHAR2(1000 CHAR),
  request_timestamp   DATE,
  response_timestamp  DATE,
  request_message     CLOB,
  response_message    CLOB,
  downstream_request  CLOB,
  downstream_response CLOB,
  exception           CLOB
);



-- create PK for message log table
declare
    v_sql LONG;
begin

    v_sql := '
ALTER TABLE GIS.TBL_MESSAGE_LOG ADD (
CONSTRAINT TBL_MESSAGE_LOG_PK PRIMARY KEY (ID))
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
                CREATE SEQUENCE GIS.TBL_MESSAGE_LOG_SEQ START WITH 1
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
CREATE OR REPLACE TRIGGER TBL_MESSAGE_LOG_SEQ_TRIGGER
    BEFORE INSERT
    ON TBL_MESSAGE_LOG
    FOR EACH ROW

BEGIN
    SELECT TBL_MESSAGE_LOG_SEQ.NEXTVAL
    INTO :new.ID
    FROM dual;
END;



----------------------------------------------------------------------------------------

-- create api description table
CREATE TABLE GIS.TBL_API_DESCRIPTION (
    id NUMBER(10),
    api_name varchar2(255 char),
    api_url varchar2(1500 char),
    is_enabled number(1,0),
    is_mocked number(1,0),
    bypass_auth number(1,0),
    api_description varchar2(2000 char),
    mocked_response CLOB
);



-- create PK for message log table
declare
    v_sql LONG;
begin

    v_sql := '
ALTER TABLE GIS.TBL_API_DESCRIPTION ADD (
CONSTRAINT TBL_API_DESCRIPTION_PK PRIMARY KEY (ID))
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
                CREATE SEQUENCE GIS.TBL_API_DESCRIPTION_SEQ START WITH 1
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
CREATE OR REPLACE TRIGGER TBL_API_DESCRIPTION_SEQ_TRIGGER
    BEFORE INSERT
    ON TBL_API_DESCRIPTION
    FOR EACH ROW

BEGIN
    SELECT TBL_API_DESCRIPTION_SEQ.NEXTVAL
    INTO :new.ID
    FROM dual;
END;
