"""Parser tests against report excerpts from Vivado 2026.1 (xc7a100t)."""

import unittest

from vivado_mcp.server import parse_timing_summary, parse_utilization

TIMING = """\
------------------------------------------------------------------------------------------------
| Design Timing Summary
| ---------------------
------------------------------------------------------------------------------------------------

    WNS(ns)      TNS(ns)  TNS Failing Endpoints  TNS Total Endpoints      WHS(ns)      THS(ns)  THS Failing Endpoints  THS Total Endpoints     WPWS(ns)     TPWS(ns)  TPWS Failing Endpoints  TPWS Total Endpoints
    -------      -------  ---------------------  -------------------      -------      -------  ---------------------  -------------------     --------     --------  ----------------------  --------------------
     24.630        0.000                      0               117485       -0.023       -0.046                      2               117485        2.633        0.000                       0                 24322


Timing constraints are not met.
"""

UTILIZATION = """\
+----------------------------+-------+-------+------------+-----------+-------+
|          Site Type         |  Used | Fixed | Prohibited | Available | Util% |
+----------------------------+-------+-------+------------+-----------+-------+
| Slice LUTs                 | 25414 |     0 |          0 |     63400 | 40.09 |
|   LUT as Logic             | 17222 |     0 |          0 |     63400 | 27.16 |
|     LUT as Distributed RAM |  8192 |     0 |            |           |       |
| Slice Registers            | 16238 |     0 |          0 |    126800 | 12.81 |
+----------------------------+-------+-------+------------+-----------+-------+

+-------------------+------+-------+------------+-----------+-------+
|     Site Type     | Used | Fixed | Prohibited | Available | Util% |
+-------------------+------+-------+------------+-----------+-------+
| Block RAM Tile    | 64.5 |     0 |          0 |       135 | 47.78 |
+-------------------+------+-------+------------+-----------+-------+

+----------------+------+-------+------------+-----------+-------+
|    Site Type   | Used | Fixed | Prohibited | Available | Util% |
+----------------+------+-------+------------+-----------+-------+
| DSPs           |    1 |     0 |          0 |       240 |  0.42 |
|   DSP48E1 only |    1 |       |            |           |       |
+----------------+------+-------+------------+-----------+-------+

+-----------------------------+------+-------+------------+-----------+-------+
|          Site Type          | Used | Fixed | Prohibited | Available | Util% |
+-----------------------------+------+-------+------------+-----------+-------+
| Bonded IOB                  |   43 |    43 |          0 |       210 | 20.48 |
+-----------------------------+------+-------+------------+-----------+-------+
"""

# Older layout without the "Prohibited" column
UTILIZATION_OLD = """\
+-------------------------+-------+-------+-----------+-------+
|        Site Type        |  Used | Fixed | Available | Util% |
+-------------------------+-------+-------+-----------+-------+
| CLB LUTs                |   120 |     0 |    230400 |  0.05 |
| CLB Registers           |   200 |     0 |    460800 | <0.01 |
+-------------------------+-------+-------+-----------+-------+
"""


class TimingSummaryTest(unittest.TestCase):
    def test_table_format(self):
        r = parse_timing_summary(TIMING)
        self.assertEqual((r["wns"], r["tns"], r["whs"], r["ths"]), (24.63, 0.0, -0.023, -0.046))
        self.assertEqual((r["wpws"], r["tpws"]), (2.633, 0.0))
        self.assertEqual(r["failing_endpoints"], 2)
        self.assertFalse(r["met"])

    def test_met(self):
        r = parse_timing_summary(TIMING.replace("-0.023", " 0.023").replace("-0.046", " 0.000"))
        self.assertTrue(r["met"])


class UtilizationTest(unittest.TestCase):
    def test_prohibited_column(self):
        r = parse_utilization(UTILIZATION)
        self.assertEqual(r["lut"], {"used": 25414, "available": 63400, "percent": 40.09})
        self.assertEqual(r["ff"], {"used": 16238, "available": 126800, "percent": 12.81})
        self.assertEqual(r["bram"], {"used": 64.5, "available": 135, "percent": 47.78})
        self.assertEqual(r["dsp"], {"used": 1, "available": 240, "percent": 0.42})
        self.assertEqual(r["io"], {"used": 43, "available": 210, "percent": 20.48})

    def test_old_layout(self):
        r = parse_utilization(UTILIZATION_OLD)
        self.assertEqual(r["lut"], {"used": 120, "available": 230400, "percent": 0.05})
        self.assertEqual(r["ff"], {"used": 200, "available": 460800, "percent": 0.01})


if __name__ == "__main__":
    unittest.main()
