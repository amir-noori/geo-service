
-- create TBL_LAND_CLAIM table


CREATE TABLE TBL_LAND_CLAIM (
	id number(10,0) not null,
	claim_trace_id varchar2(2000 char),
	request_timestamp   DATE,
    claimed_file_content_type varchar2(10 char),
    claimed_file_content CLOB,
    claimed_polygon SDO_GEOMETRY
);




-- create PK for TBL_LAND_CLAIM table
declare
    v_sql LONG;
begin

    v_sql := '
ALTER TABLE TBL_LAND_CLAIM ADD (
CONSTRAINT TBL_LAND_CLAIM_PK PRIMARY KEY (ID))
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



-- create seq TBL_LAND_CLAIM table
declare
    v_sql LONG;
begin

    v_sql := '
                CREATE SEQUENCE TBL_LAND_CLAIM_SEQ START WITH 1
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



-- create trigger for TBL_LAND_CLAIM_SEQ
CREATE OR REPLACE TRIGGER TBL_LAND_CLAIM_SEQ_TRIGGER
    BEFORE INSERT
    ON TBL_LAND_CLAIM
    FOR EACH ROW

BEGIN
    SELECT TBL_LAND_CLAIM_SEQ.NEXTVAL
    INTO :new.ID
    FROM dual;
END;


