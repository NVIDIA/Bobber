# Baselines
The results parser included with Bobber is able to compare results against a
pre-defined baseline or a custom baseline passed in as a YAML file. By comparing
results against a baseline, it is possible to easily check if a round of tests
meets the expected performance level or if any tests are underperforming. This
is useful to verify new systems are performing as expected or to view if any
changes to the hardware or software affect stability.

## Running the baseline comparison
There are two main paths to compare baselines in Bobber, either by using a
built-in baseline config or using a custom file.

### Using built-in baselines
To compare against a built-in baseline, use the `--compare-baseline` flag with
the `parse-results` command. To list the possible choices, pass the `--help`
flag as below. The choices are listed in the curly brackets (`{}`):

```
bobber parse-results --help
...
  --compare-baseline {single-dgx-station-baseline}
                        Compare the values produced by a test run against a pre-defined baseline to verify performance meets an acceptable threshold.
```

To run the comparison against existing results, run the following while updating
the baseline and log directory, if applicable.

```
bobber parse-results --compare-baseline single-dgx-station-baseline results_logs/
```

### Using custom baselines
To use a custom baseline, a YAML file needs to be created which specifies the
expected performance for every test. A [sample file](sample_baseline.yaml) has
been created as a guide. Every custom baseline file must have the following
structure:

```
systems:  # This should always be the first line
    1:  # This designates all results in the sub-block are specific to a single compute node
        bandwidth:  # This section is for the FIO bandwidth results in bytes/second
            read: 1200000000  # The FIO bandwidth read results in bytes/second
            write: 1000000000  # The FIO bandwidth write results in bytes/second
        iops:  # This section is for the FIO IOPS results in ops/second
            read: 100000  # The FIO IOPS read speed in ops/second
            write: 100000  # The FIO IOPS write speed in ops/second
        nccl:  # The maximum bus bandwidth in GB/s for NCCL
            max_bus_bw: 230  # The maximum bus bandwidth in GB/s for NCCL
        dali:  # The average speed in images/second from DALI tests
            800x600 standard jpg: 2000  # The speed in images/second for 800x600 standard JPG images in DALI
            3840x2160 standard jpg: 300  # The speed in images/second for 4K standard JPG images in DALI
            800x600 tfrecord: 2000  # The speed in images/second for 800x600 TFRecords in DALI
            3840x2160 tfrecord: 300  # The speed in images/second for 4K TFRecords in DALI
    2: # Continue the same pattern as above for results specific to two compute nodes, if applicable
    ...
```

The custom results parser will only compare against the system counts that are
provided in the YAML file, meaning if only results for 8 compute nodes are
included in the YAML file, only those results will be compared. As many or as
few system counts as desired can be added to the YAML file to more extensively
compare results at all levels.

After saving the YAML file locally, run the comparison as follows while updating
the YAML file location and log directory, if applicable:

```
bobber parse-results --custom-baseline custom_baseline_file.yaml results_log/
```

## Baseline results output
Regardless of which baseline method from above is chosen, the results will
compare the performance from the requested results file with the baseline of
choice. The comparison does a simple PASS/FAIL for every result depending on
whether it surpasses performance or not. If at least one result does not meet
performance expectations, the comparison will be marked as failed.

Example of results that pass every threshold:

```
bobber parse-results --compare-baseline single-dgx-station-baseline log_files/

...

================================================================================
Baseline assessment
Comparing against "single-dgx-station-baseline"
================================================================================
 1 System(s)
--------------------------------------------------------------------------------
  FIO Bandwidth Read (GB/s)
    Expected: 1.2, Got: 1.595, Result: PASS
  FIO Bandwidth Write (GB/s)
    Expected: 1.0, Got: 1.232, Result: PASS
--------------------------------------------------------------------------------
  FIO IOPS Read (k IOPS)
    Expected: 100.0, Got: 136.5, Result: PASS
  FIO IOPS Write (k IOPS)
    Expected: 100.0, Got: 135.0, Result: PASS
--------------------------------------------------------------------------------
  NCCL Max Bus Bandwidth (GB/s)
    Expected: 70, Got: 79.86500000000001, Result: PASS
--------------------------------------------------------------------------------
  DALI 800x600 standard jpg (images/second)
    Expected: 2000, Got: 2694.595, Result: PASS
  DALI 3840x2160 standard jpg (images/second)
    Expected: 300, Got: 430.854, Result: PASS
  DALI 800x600 tfrecord (images/second)
    Expected: 2000, Got: 2665.653, Result: PASS
  DALI 3840x2160 tfrecord (images/second)
    Expected: 300, Got: 376.862, Result: PASS
================================================================================
```

Example of results that fail one or more thresholds:

```
bobber parse-results --custom-baseline sample_baseline.yaml log_files/

...

================================================================================
Baseline assessment
Comparing against a custom config
================================================================================
 1 System(s)
--------------------------------------------------------------------------------
  FIO Bandwidth Read (GB/s)
    Expected: 7.0, Got: 1.595, Result: FAIL
  FIO Bandwidth Write (GB/s)
    Expected: 3.0, Got: 1.232, Result: FAIL
--------------------------------------------------------------------------------
  FIO IOPS Read (k IOPS)
    Expected: 300.0, Got: 136.5, Result: FAIL
  FIO IOPS Write (k IOPS)
    Expected: 200.0, Got: 135.0, Result: FAIL
--------------------------------------------------------------------------------
  NCCL Max Bus Bandwidth (GB/s)
    Expected: 230, Got: 79.86500000000001, Result: FAIL
--------------------------------------------------------------------------------
  DALI 800x600 standard jpg (images/second)
    Expected: 2000, Got: 2694.595, Result: PASS
  DALI 3840x2160 standard jpg (images/second)
    Expected: 300, Got: 430.854, Result: PASS
  DALI 800x600 tfrecord (images/second)
    Expected: 2000, Got: 2665.653, Result: PASS
  DALI 3840x2160 tfrecord (images/second)
    Expected: 300, Got: 376.862, Result: PASS
--------------------------------------------------------------------------------
5 tests did not meet the suggested criteria!
See results above for failed tests and verify setup.
```
