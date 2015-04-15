# -*- coding: utf-8 -*-

import csv
from datetime import timedelta

import common
from toggl import Toggl


def project_name(toggl, project_id):
  try:
    cache = project_name._cache
  except AttributeError:
    cache = {}
    project_name._cache = cache

  if project_id in cache:
    return cache[project_id]

  project = toggl.get_project(project_id)
  name = project["data"]["name"]
  cache[project_id] = name
  return name

def day_report(toggl, day):
  print "Processing day {0}...".format(day)

  # get the time entries for this day
  time_entries = toggl.get_day_time_entries(day)

  # no time entries
  if len(time_entries) == 0:
    return []

  # make sure that all the entries have exactly one tag
  if any(["tags" not in te or len(te["tags"]) != 1 for te in time_entries]):
    raise Exception("There are time entries that don't have exactly one tag on day {0}!".format(day))

  # make sure that no time entries are currently being tracked
  if any([te["duration"] < 0 for te in time_entries]):
    raise Exception("There is a time entry still being tracked on day {0}!".format(day))

  report = {}
  for time_entry in time_entries:
    proj = project_name(toggl, time_entry["pid"])
    tag = time_entry["tags"][0]
    if (proj, tag) not in report:
      report[(proj, tag)] = time_entry["duration"]
    else:
      report[(proj, tag)] += time_entry["duration"]

  return report

def generate_report(csv_filename, daily_reports):
  with open(csv_filename, "wb") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Day", "Project", "Task", "Time"])
    for day, daily_reports in daily_reports:
      for project_task, time in daily_reports.items():
        project, task = project_task
        writer.writerow([str(day), project, task, common.secs_to_hms_str(time)])

def options():
  try:
    return options._options
  except AttributeError:
    parser = common.get_option_parser()
    parser.add_option("-s", "--start_date", type="date", default=common.last_monday(),
                      help="Day from which to start normalizing (inclusive) [default: last monday]")
    parser.add_option("-e", "--end_date", type="date", default=common.next_friday(),
                      help="Day at which to stop normalizing (inclusive) [default: next friday]")
    parser.add_option("-f", "--csv_file", type="string", default="project-task-report.csv",
                      help="Filename for the csv report [default: \"project-task-report.csv\"]")
    opts, args = parser.parse_args()
    options._options = opts
    return opts

def main():
  try:
    # read and print options
    opts = options()
    print ""
    print "Days: from {0} to {1}.".format(opts.start_date, opts.end_date)
    print "Csv report: \"{0}\"".format(opts.csv_file)

    # test toggl API connection
    toggl = Toggl()
    print ""
    print "Testing toggl connection...",
    toggl.login()
    print "Ok."
    print ""

    # iterate through each day from start_date to end_date and report on each one
    daily_reports = []
    current_day = opts.start_date
    while current_day <= opts.end_date:
      report = day_report(toggl, current_day)
      daily_reports.append((current_day, report))
      current_day += timedelta(days=1)

    # generate the csv report
    print ""
    print "Generating report...",
    generate_report(opts.csv_file, daily_reports)
    print "Ok."

    print ""
    print "Done."

  except:
    print ""
    print "Error:"
    raise

if __name__ == "__main__":
  main()
