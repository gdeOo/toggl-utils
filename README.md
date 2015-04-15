# toggl-utils
A collection of command line utilities that extend [toggl](https://www.toggl.com/) functionality through the toggl API.

## toggl normalize

`toggl-normalize.py` normalizes the entries of one or more days, so that the tracked time per day is fixed.

As an example, if at the end of your work week you have to submit hours in a PSA application and there is a requirement for tracking *exactly* 8 hours per day, you can normalize the days of the previous week to 8 hours and input the resulting durations into the PSA.

### Usage

```
$ python toggl-normalize.py -h
Usage: toggl-normalize.py [options]

Options:
  -h, --help            show this help message and exit
  -s START_DATE, --start_date=START_DATE
                        Day from which to start normalizing (inclusive) [default: last monday]
  -e END_DATE, --end_date=END_DATE
                        Day at which to stop normalizing (inclusive) [default: next friday]
  -d HOURS_PER_DAY, --hours_per_day=HOURS_PER_DAY
                        Number of work hours per day [default: 8.0]
```

## toggl project-task report

`toggl-project-task-report.py` generates a csv report of your tracked time, grouped by two dimensions: the entry's project and the entry's tag (entries must have exactly one tag).

### Usage

```
$ python toggl-project-task-report.py -h
Usage: toggl-project-task-report.py [options]

Options:
  -h, --help            show this help message and exit
  -s START_DATE, --start_date=START_DATE
                        Day from which to start reporting (inclusive) [default: last monday]
  -e END_DATE, --end_date=END_DATE
                        Day at which to stop reporting (inclusive) [default: next friday]
  -f CSV_FILE, --csv_file=CSV_FILE
                        Filename for the csv report [default: "project-task-report.csv"]
```
