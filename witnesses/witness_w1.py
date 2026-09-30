"""Witness database for the shipping task (real ELT-Bench reference transformation).

Schema mirrors shipping.airbyte_schema.{driver,shipment,city,customer} as used by
evaluation/shipping/drivers.sql in the ELT-Bench repo. Values are chosen so that
each mutation operator is *exercised*: the witness state is built to make
P(I_w) != P'(I_w) observable for every declared operator.
"""
import duckdb

def build(con):
    con.execute("CREATE SCHEMA IF NOT EXISTS shipping")
    con.execute("""
        CREATE OR REPLACE TABLE shipping.driver(
            driver_id INTEGER, first_name VARCHAR, last_name VARCHAR)""")
    con.execute("""INSERT INTO shipping.driver VALUES
        (1,'Ada','Byron'),      -- has 2017 shipments, mixed customers
        (2,'Grace','Hopper'),   -- no 2017 shipments  -> NULL/0 boundary
        (3,'Alan','Turing'),    -- ties on ship_date  -> ordering/tie-break
        (4,'Edsger','Dijkstra'),-- NO shipments at all -> LEFT JOIN absence
        (5,'Barbara','Liskov'),  -- repeat customer -> COUNT vs COUNT DISTINCT
        (6,'Tony','Hoare')       -- full tie -> rank vs row_number
    """)
    con.execute("""
        CREATE OR REPLACE TABLE shipping.city(
            city_id INTEGER, city_name VARCHAR, population INTEGER)""")
    # two cities tie on the minimum population -> cardinality of "least populated"
    con.execute("""INSERT INTO shipping.city VALUES
        (10,'Smallville',100),(11,'Tinytown',100),(12,'Metropolis',900000)""")
    con.execute("""
        CREATE OR REPLACE TABLE shipping.customer(
            cust_id INTEGER, cust_name VARCHAR)""")
    con.execute("""INSERT INTO shipping.customer VALUES
        (100,'Autoware Inc'),(101,'Other Co')""")
    con.execute("""
        CREATE OR REPLACE TABLE shipping.shipment(
            ship_id INTEGER, driver_id INTEGER, cust_id INTEGER,
            city_id INTEGER, weight DOUBLE, ship_date DATE)""")
    con.execute("""INSERT INTO shipping.shipment VALUES
        (1000,1,100,10, 50.0,DATE '2017-03-01'),
        (1001,1,101,11, 50.0,DATE '2017-06-15'),
        (1002,1,100,12,300.0,DATE '2018-01-10'),
        (1003,2,101,12, 10.0,DATE '2016-05-05'),
        (1004,3,100,10, 20.0,DATE '2017-02-02'),
        (1005,3,101,10, 80.0,DATE '2017-02-02'),
        -- driver 1: second heavy shipment so the >95%-of-average set has TWO
        -- rows for the same driver (discriminates DISTINCT removal)
        (1006,1,101,12,320.0,DATE '2018-02-11'),
        -- driver 5: two 2017 shipments to the SAME customer
        -- (discriminates COUNT(*) vs COUNT(DISTINCT cust_id))
        (1007,5,100,12, 15.0,DATE '2017-04-01'),
        (1008,5,100,12, 15.0,DATE '2017-04-02'),
        -- driver 6: exact tie on BOTH ship_date and weight, so rank() keeps
        -- two rows at date_rank=1 while row_number() keeps one
        -- (discriminates tie-resolution)
        (1009,6,100,12, 42.0,DATE '2017-07-07'),
        (1010,6,101,12, 42.0,DATE '2017-07-07')
    """)
    return con

def fresh():
    con = duckdb.connect()
    return build(con)
