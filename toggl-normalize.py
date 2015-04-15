# -*- coding: utf-8 -*-

from datetime import timedelta

import common
from toggl import Toggl


def normalize_day(toggl, day):
  """Normalize the time entries in a day.

  Modify the time entries in a day so that the sum of their durations matches the target work-hours-per-day value.
  The new duration of each time entry is calculated according to the following formula:
    <new_duration> = <target_total_duration>*<current_duration>/<current_total_duration>

  If an error occurs while the time entries of the day are in an inconsistent state, i.e, partially normalized,
  an automatic rollback is attempted.
  """
  print ""
  print "Normalizing day {0}...".format(day)

  # get the time entries for this day
  time_entries = toggl.get_day_time_entries(day)

  # skip the day if there are no time entries
  if len(time_entries) == 0:
    print "Skipping: there are no time entries for this day."
    return

  current_durations = [te["duration"] for te in time_entries]

  # skip the day if it contains a time_entry being tracked right now!
  if any([d < 0 for d in current_durations]):
    print "Skipping: contains a time entry being tracked..."
    return

  total_duration = sum(current_durations)
  target_duration = int(round(options().hours_per_day*60*60))

  # skip the day if it is already normalized according to our target
  # there is a 5 second tolerance because we're normalizing integers
  if abs(total_duration - target_duration) < 5:
    print "Skipping: already at target {0}.".format(common.secs_to_hms_str(target_duration))
    return

  # ask for user confirmation before making any changes
  print "You logged a total of {0}.".format(common.secs_to_hms_str(total_duration))
  while True:
    response = raw_input("Would you like to normalize to {0}? [y] ".format(
                         common.secs_to_hms_str(target_duration))).lower()
    if response in ("n", "no"):
      print "Skipping: user request."
      break

    if response in ("", "y", "yes"):
      changes = []
      for time_entry in time_entries:
        try:
          # assign a description if there is none
          if not "description" in time_entry:
            time_entry["description"] = "(no description)"

          # compute new duration
          current_duration = time_entry["duration"]
          normalized_duration = int(round(target_duration*current_duration*1.0/total_duration))

          # update the time entry
          print u"Updating entry \"{0}\" from {1} to {2}.".format(
            time_entry["description"], common.secs_to_hms_str(time_entry["duration"]),
            common.secs_to_hms_str(normalized_duration))
          toggl.update_time_entry_duration(time_entry["id"], normalized_duration)

          # keep track of changes already made for rollback purposes
          changes.append((time_entry, current_duration, normalized_duration))

        except:
          # rollback changes if any error occurs
          print "Error updating entry. Trying to rollback..."
          rollback_day(toggl, day, changes)
          raise
      break

def rollback_day(toggl, day, changes):
  """Rollback changes made to the time entries of a given day.

  If the changes cannot be automatically rolledback due to further errors, print the changes so that the user may
  rollback manually.
  """
  try:
    for time_entry, original_duration, normalized_duration in changes:
      print u"Rolling back \"{0}\" to {1} from {2}".format(time_entry["description"],
        common.secs_to_hms_str(original_duration), common.secs_to_hms_str(normalized_duration))
      toggl.update_time_entry_duration(time_entry["id"], original_duration)
    print "Rollback successful."

  except:
    # print the changes if the rollback fails
    print "Rollback failed... you'll have to rollback the following time entries manually:"
    for time_entry, original_duration, normalized_duration in changes:
      print u"  \"{0}\" back to {1} from {2}".format(time_entry["description"],
        common.secs_to_hms_str(original_duration), common.secs_to_hms_str(normalized_duration))


def options():
  """Get command line options.

  Returns:
    An object with the following attributes:
      start_date: Day from which to start normalizing (inclusive)
      end_date: Day at which to stop normalizing (inclusive)
      hours_per_day: Number of work hours per day
  """
  try:
    return options._options
  except AttributeError:
    parser = common.get_option_parser()
    parser.add_option("-s", "--start_date", type="date", default=common.last_monday(),
                      help="Day from which to start normalizing (inclusive) [default: last monday]")
    parser.add_option("-e", "--end_date", type="date", default=common.next_friday(),
                      help="Day at which to stop normalizing (inclusive) [default: next friday]")
    parser.add_option("-d", "--hours_per_day", type="float", default=8.0,
                      help="Number of work hours per day [default: %default]")
    opts, args = parser.parse_args()
    options._options = opts
    return opts

def main():
  # print a banner
  print " _                    _                                      _ _              "
  print "| |_ ___   __ _  __ _| |    _ __   ___  _ __ _ __ ___   __ _| (_)_______ _ __ "
  print "| __/ _ \ / _` |/ _` | |   | '_ \ / _ \| '__| '_ ` _ \ / _` | | |_  / _ \ '__|"
  print "| || (_) | (_| | (_| | |   | | | | (_) | |  | | | | | | (_| | | |/ /  __/ |   "
  print " \__\___/ \__, |\__, |_|   |_| |_|\___/|_|  |_| |_| |_|\__,_|_|_/___\___|_|   "
  print "          |___/ |___/                                                         "
  print ""

  try:
    # read and print options
    opts = options()
    print ""
    print "Days: from {0} to {1}.".format(opts.start_date, opts.end_date)
    print "Hours per day: {0}".format(common.secs_to_hms_str(int(round(opts.hours_per_day*60*60))))
    
    # test toggl API connection
    toggl = Toggl()
    print ""
    print "Testing toggl connection...",
    toggl.login()
    print "Ok."
    print ""

    # iterate through each day from start_date to end_date and normalize each one
    current_day = opts.start_date
    while current_day <= opts.end_date:
      normalize_day(toggl, current_day)
      current_day += timedelta(days=1)

    print ""
    print "Done."

  except Exception, e:
    print ""
    print "Error:", e
    raise



if __name__ == "__main__":
  main()
