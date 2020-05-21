drop database if exists fsqlfly_test cascade;
create database fsqlfly_test;
use fsqlfly_test;
create table all_types
(
    TINYINT_T   TINYINT,
    SMALLINT_T  SMALLINT,
    INT_T       INT,
    BIGINT_T    BIGINT,
    FLOAT_T     FLOAT,
    DOUBLE_T    DOUBLE,
    DECIMAL_T   DECIMAL,
    TIMESTAMP_T TIMESTAMP,
    DATE_T      DATE,
    STRING_T    STRING,
    VARCHAR_T   VARCHAR(1000),
    CHAR_T      CHAR(16),
    BOOLEAN_T   BOOLEAN,
    BINARY_T    BINARY,
    ARRAY_T     ARRAY<STRING>,
    MAP_T       MAP<STRING, STRING>,
    STRUCT_T    STRUCT<col: STRING>,
    UNIONTYPE_T UNIONTYPE<STRING, INT>
) partitioned by (pt STRING);