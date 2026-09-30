"""Semantic mutation operators applied to the shipping.drivers reference.

Each mutant declares exactly ONE semantic property it changes. `find` must occur
exactly once in the reference (checked at apply time) so the edit is localized.
"""
from reference_port import REFERENCE

# (id, family, property_changed, find, replace)
SEMANTIC = [
 ("M01","grain/cardinality","output row multiplicity (duplicate driver rows)",
  "  SELECT DISTINCT driver_id AS driver_id\n  FROM shipping.shipment",
  "  SELECT driver_id AS driver_id\n  FROM shipping.shipment"),

 ("M02","predicates/population","output population (drivers without 2017 shipments dropped)",
  "LEFT JOIN num_shipments_2017_cte T2 ON T1.driver_id = T2.driver_id",
  "INNER JOIN num_shipments_2017_cte T2 ON T1.driver_id = T2.driver_id"),

 ("M03","measures","counting basis (rows -> distinct customers)",
  "SELECT T2.driver_id AS driver_id, COUNT(*) AS num_shipments_2017",
  "SELECT T2.driver_id AS driver_id, COUNT(DISTINCT T1.cust_id) AS num_shipments_2017"),

 ("M04","measures","measure scale (percentage points -> fraction)",
  "AS DOUBLE)\n      * 100 / COUNT(*) AS per",
  "AS DOUBLE)\n      * 1 / COUNT(*) AS per"),

 ("M05","temporal","temporal window (= 2017 -> >= 2017)",
  "WHERE EXTRACT(YEAR FROM T1.ship_date) = 2017",
  "WHERE EXTRACT(YEAR FROM T1.ship_date) >= 2017"),

 ("M06","temporal","tie-break direction within event ordering",
  "rank() OVER (PARTITION BY driver_id ORDER BY ship_date, weight DESC)",
  "rank() OVER (PARTITION BY driver_id ORDER BY ship_date, weight ASC)"),

 ("M07","absence","absence encoding (0 -> NULL for no 2017 shipments)",
  "  CASE WHEN T2.num_shipments_2017 IS NULL THEN 0 ELSE T2.num_shipments_2017 END\n    AS num_shipments_2017",
  "  T2.num_shipments_2017 AS num_shipments_2017"),

 ("M08","absence","absence encoding (NULL -> 0 for undefined percentage)",
  "  T4.per AS per_shipment_placed_by_Autoware_Inc",
  "  COALESCE(T4.per, 0) AS per_shipment_placed_by_Autoware_Inc"),

 ("M09","representative-value","tie resolution (rank keeps ties -> row_number picks one)",
  "    rank() OVER (PARTITION BY driver_id ORDER BY ship_date, weight DESC) AS date_rank",
  "    row_number() OVER (PARTITION BY driver_id ORDER BY ship_date, weight DESC) AS date_rank"),

 ("M10","predicates/population","predicate threshold (95% -> 90% of average weight)",
  "WHERE weight * 100 > (SELECT 95 * AVG(weight) FROM shipping.shipment)",
  "WHERE weight * 100 > (SELECT 90 * AVG(weight) FROM shipping.shipment)"),
]

# Matched conventional program mutants (control arm): standard mutation-testing
# operators (ROR / AOR / CRP / SDL) chosen to perturb the SAME output columns as
# the semantic mutants, but WITHOUT being motivated by a semantic property.
CONVENTIONAL = [
 ("C01","ROR","relational operator replaced (> -> <) in weight predicate",
  "WHERE weight * 100 > (SELECT 95 * AVG(weight) FROM shipping.shipment)",
  "WHERE weight * 100 < (SELECT 95 * AVG(weight) FROM shipping.shipment)"),
 ("C02","AOR","arithmetic operator replaced (* -> +) in percentage",
  "AS DOUBLE)\n      * 100 / COUNT(*) AS per",
  "AS DOUBLE)\n      + 100 / COUNT(*) AS per"),
 ("C03","CRP","constant replaced (2017 -> 2018)",
  "WHERE EXTRACT(YEAR FROM T1.ship_date) = 2017",
  "WHERE EXTRACT(YEAR FROM T1.ship_date) = 2018"),
 ("C04","CRP","constant replaced (rank 1 -> 2)",
  "AND T6.date_rank = 1",
  "AND T6.date_rank = 2"),
 ("C05","SDL","statement deleted (min population subquery -> fixed literal)",
  "WHERE population = (SELECT min(population) FROM shipping.city)",
  "WHERE population = 900000"),
]

def apply(find, repl):
    if REFERENCE.count(find) != 1:
        raise ValueError(f"anchor not unique (count={REFERENCE.count(find)}): {find[:60]!r}")
    return REFERENCE.replace(find, repl)
