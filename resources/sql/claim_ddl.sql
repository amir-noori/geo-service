-- create TBL_LAND_CLAIM table


CREATE TABLE TBL_LAND_CLAIM
(
    id                        number(10,0) not null,
    claim_trace_id            varchar2(200 char),
    request_timestamp         DATE,
    claimed_file_content_type varchar2(10 char),
    claimed_file_content      CLOB,
    claimed_polygon           SDO_GEOMETRY
);


-- create PK for TBL_LAND_CLAIM table
declare
v_sql LONG;
begin

    v_sql
:= '
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

    v_sql
:= '
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
CREATE
OR REPLACE TRIGGER TBL_LAND_CLAIM_SEQ_TRIGGER
    BEFORE INSERT
    ON TBL_LAND_CLAIM
    FOR EACH ROW

BEGIN
SELECT TBL_LAND_CLAIM_SEQ.NEXTVAL
INTO :new.ID
FROM dual;
END;


-----------------------------------------------------------------


-- create TBL_PARCEL_CLAIM table

CREATE TABLE TBL_PARCEL_CLAIM
(
    ID                  NUMBER(19) NOT NULL PRIMARY KEY,
    REQUEST_ID          VARCHAR2(200) NOT NULL,
    CLAIM_TRACING_ID    VARCHAR2(200 char),
    SURVEYOR_ID         VARCHAR2(200),
    CLAIMANT_ID         VARCHAR2(200) NOT NULL,
    cms                 VARCHAR2(10 CHAR),
    NEIGHBOURING_POINT  SDO_GEOMETRY,
    REQUEST_TIMESTAMP   TIMESTAMP,
    MODIFY_TIMESTAMP    TIMESTAMP,
    PROCESS_INSTANCE_ID VARCHAR2(200) NOT NULL
);

-- create sequence for TBL_PARCEL_CLAIM
declare
v_sql LONG;
begin
    v_sql
:= '
        CREATE SEQUENCE TBL_PARCEL_CLAIM_SEQ START WITH 1
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

-- create TBL_REGISTERED_CLAIM table

CREATE TABLE TBL_REGISTERED_CLAIM
(
    ID                      NUMBER(19) NOT NULL PRIMARY KEY,
    REQUEST_ID              VARCHAR2(200) NOT NULL,
    CLAIM_TRACING_ID            varchar2(200 char),
    SURVEYOR_ID             VARCHAR2(200) NOT NULL,
    CREATE_TIMESTAMP        TIMESTAMP,
    MODIFY_TIMESTAMP        TIMESTAMP,
    STATUS                  NUMBER(10),
    CMS                     VARCHAR2(10),
    AREA                    FLOAT,
    COUNTY                  VARCHAR2(300),
    STATE_CODE              VARCHAR2(10),
    MAIN_PLATE_NUMBER       VARCHAR2(100),
    SUBSIDIARY_PLATE_NUMBER VARCHAR2(100),
    SECTION                 VARCHAR2(300),
    DISTRICT                VARCHAR2(300),
    POLYGON                 SDO_GEOMETRY,
    EDGES                   CLOB,
    BENEFICIARY_RIGHTS      VARCHAR2(4000),
    ACCOMMODATION_RIGHTS    VARCHAR2(4000),
    IS_APARTMENT            NUMBER(1),
    FLOOR_NUMBER            FLOAT,
    UNIT_NUMBER             FLOAT,
    ORIENTATION             NUMBER(10),
    ATTACHMENTS             CLOB
);

-- create sequence for TBL_REGISTERED_CLAIM
declare
v_sql LONG;
begin
    v_sql
:= '
        CREATE SEQUENCE TBL_REGISTERED_CLAIM_SEQ START WITH 1
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

-- create TBL_CLAIM_PARCEL_EDGE table

CREATE TABLE TBL_CLAIM_PARCEL_EDGE
(
    ID                          NUMBER(19) NOT NULL PRIMARY KEY,
    REQUEST_ID                  VARCHAR2(200),
    LINE_INDEX                  NUMBER(10) NOT NULL,
    LENGTH                      FLOAT,
    ORIENTATION                 NUMBER(10),
    STARTING_POINT              SDO_GEOMETRY,
    ENDING_POINT                SDO_GEOMETRY,
    IS_ADJACENT_TO_PLATE_NUMBER NUMBER(1),
    IS_ADJACENT_TO_PASSAGE      NUMBER(1),
    PASSAGE_NAME                VARCHAR2(300),
    PASSAGE_WIDTH               FLOAT,
    BOUNDARY                    VARCHAR2(4000)
);

-- create sequence for TBL_CLAIM_PARCEL_EDGE
declare
v_sql LONG;
begin
    v_sql
:= '
        CREATE SEQUENCE TBL_CLAIM_PARCEL_EDGE_SEQ START WITH 1
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



-- create TBL_CLAIM_PARCEL_ATTACHMENT table
CREATE TABLE TBL_CLAIM_PARCEL_ATTACHMENT
(
    ID          NUMBER(19) NOT NULL PRIMARY KEY,
    REQUEST_ID  VARCHAR2(200),
    TITLE       VARCHAR2(500),
    AREA        FLOAT,
    DESCRIPTION VARCHAR2(4000)
);

-- create sequence for TBL_CLAIM_PARCEL_ATTACHMENT
declare
v_sql LONG;
begin
    v_sql
:= '
        CREATE SEQUENCE TBL_CLAIM_PARCEL_ATTACH_SEQ START WITH 1
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







