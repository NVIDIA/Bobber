# Parsing
Bobber includes a couple different parsers which can be used to easily verify
performance results from a test. By pointing Bobber to the directory where
results were saved, aggregate values per system-count level will be displayed.

The output displays a table with the aggregate results among all iterations per
number of nodes tested. For example, if 10 iterations were run, the 1-node
results will be the average values for all test runs for a single node. As the
node count goes up, the results reflect the aggregate value for all nodes that
were tested. The table is automatically generated based on the values above to
make it possible to view how results scale with additional node counts.

```
+----------------------------------------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+---------+
| Test                                               |   1 Node(s) |   2 Node(s) |   3 Node(s) |   4 Node(s) |   5 Node(s) |   6 Node(s) |   7 Node(s) |   8 Node(s) | Scale   |
+====================================================+=============+=============+=============+=============+=============+=============+=============+=============+=========+
| FIO Read (GB/s) - 1MB BS                           |       7.996 |      18.208 |      22.707 |       23.43 |      34.916 |       37.28 |      44.941 |      45.316 | 1.67X   |
+----------------------------------------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+---------+
| FIO Write (GB/s) - 1MB BS                          |       4.439 |       5.291 |        5.46 |         5.6 |       7.116 |       7.444 |       7.588 |       7.486 | 1.11X   |
+----------------------------------------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+---------+
| FIO Read (k IOPS) - 4K BS                          |       306.9 |       515.2 |       546.9 |       566.1 |         625 |       638.6 |       790.8 |       978.8 | 1.25X   |
+----------------------------------------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+---------+
| FIO Write (k IOPS) - 4K BS                         |       295.5 |       437.9 |       445.5 |         427 |       474.4 |       474.7 |       502.4 |       484.2 | 1.07X   |
+----------------------------------------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+---------+
| NCCL Max BW (GB/s)                                 |     235.253 |     141.883 |     140.335 |     140.731 |     140.083 |     140.966 |     139.593 |     140.715 | N/A     |
+----------------------------------------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+---------+
| DALI Standard 800x600 throughput (images/second)   |     5821.49 |     11849.7 |     17719.4 |     23654.6 |     29508.7 |     35501.1 |     41282.8 |     47250.2 | 2.02X   |
+----------------------------------------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+---------+
```

### Parser Assumptions
The auto-parser makes the following assumptions:
  * The Bobber version must match for all files in a directory so results aren't
getting mixed. This can be overriden with `--override-version-check` while
calling the script.
  * If a result file is invalid or missing data, it is skipped and not included
with the results. The average results will reflect the limited number of valid
results.
  * The lowest N-results in DALI tests are dropped for N-nodes. These results
are part of a known warm-up period for DALI and do not indicate actual
performance.
  * The scale 

## Parsing MLPerf
This repository includes a Python package that can quickly and easily parse
MLPerf results. Note that MLPerf is **not** included in Bobber though results
from the ResNet50 image classification benchmarks can be parsed here.

```bash
$ python3 bobber/lib/analysis/parse-mlperf.py path_to_results/
MLPerf Results:
Directory name: path_to_results/
Number of iterations: 5
Nodes tested: 8
Epoch 0:
    Speed: 80113.842 images/second
    Average time: 15.901 seconds
Overall:
    Speed: 148134.457 images/second
    Average time: 7.116 minutes
```

The output displays the aggregate results among all MLPerf test passes and finds
the average speed and times for all runs. Results for both Epoch 0 and overall
numbers are displayed to provide different insights. Epoch 0 is helpful to best
identify the storage performance as images are likely not to be cached in the
system.

### Parser Assumptions
The parser makes the following assumptions:
  * The parser assumes the directory only contains results for a single test
sweep for a set number of nodes (ie. all results are from a 10-iteration test
for 4 nodes and no results from different node counts are included).
  * The elapsed time is found by taking the difference between the start time
for the first epoch (Epoch 0) and the stop time for the last epoch.
  * All results are averaged together based on the number of results in the
directory.
