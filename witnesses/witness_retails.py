"""Witness state for the retails task (TPC-H-shaped).

Built from the FROZEN structural requirements in operators/catalog_v1.yaml:
  fan-out            -> customer with multiple orders
  population         -> customer with no orders; nation with no suppliers
  measures           -> repeated grouping value; unequal denominators
  absence            -> genuine zero balance alongside NULL-producing outer joins
  representative val -> exact tie on (o_totalprice, o_orderdate)
  predicates         -> nation names where one is a substring of another
No witness value was chosen in response to an evaluator outcome.
"""
import duckdb

def build(con):
    con.execute("CREATE SCHEMA IF NOT EXISTS retails")
    con.execute("CREATE OR REPLACE TABLE retails.nation(n_nationkey INTEGER, n_name VARCHAR, n_regionkey INTEGER)")
    con.execute("""INSERT INTO retails.nation VALUES
        (1,'United States',10),
        (2,'United States Minor Outlying Islands',10),  -- substring trap for PP2
        (3,'Canada',10),
        (4,'Japan',20)                                   -- no suppliers, no customers
    """)
    con.execute("CREATE OR REPLACE TABLE retails.customer(c_custkey INTEGER, c_name VARCHAR, c_nationkey INTEGER, c_acctbal DOUBLE)")
    con.execute("""INSERT INTO retails.customer VALUES
        (100,'Alpha',1, 5000.0),   -- many orders, above-average balance
        (101,'Beta', 1,    0.0),   -- genuine ZERO balance (absence vs zero)
        (102,'Gamma',2, 3500.0),   -- below 4000, in a 'United States%' nation
        (103,'Delta',3, 9000.0),   -- NO orders at all -> unmatched parent
        (104,'Eps',  1, 3900.0)    -- below 4000, exact-tie orders
    """)
    con.execute("CREATE OR REPLACE TABLE retails.orders(o_orderkey INTEGER, o_custkey INTEGER, o_totalprice DOUBLE, o_orderdate DATE)")
    con.execute("""INSERT INTO retails.orders VALUES
        (900,100,1000.0,DATE '2020-01-01'),
        (901,100,1000.0,DATE '2020-01-01'),   -- exact tie on price AND date
        (902,100, 500.0,DATE '2020-02-01'),
        (903,101, 250.0,DATE '2020-03-01'),
        (904,102, 750.0,DATE '2020-04-01'),
        (905,104, 300.0,DATE '2020-05-01'),
        (906,104, 300.0,DATE '2020-05-01')    -- second exact tie
    """)
    con.execute("CREATE OR REPLACE TABLE retails.supplier(s_suppkey INTEGER, s_nationkey INTEGER, s_acctbal DOUBLE)")
    con.execute("""INSERT INTO retails.supplier VALUES
        (500,1, -100.0),   -- in debt
        (501,1,  200.0),
        (502,1,  300.0),   -- unequal denominators across nations
        (503,2, -50.0),
        (504,3,  0.0)      -- genuine zero
    """)
    return con

def fresh():
    return build(duckdb.connect())
