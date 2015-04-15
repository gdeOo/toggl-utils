# -*- coding: utf-8 -*-

from copy import copy
from optparse import OptionParser, Option, OptionValueError
from datetime import datetime, timedelta

def get_option_parser():
  def date_checker(option, opt, value):
    try:
      return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
      raise OptionValueError("option {0}: invalid date value: {1}".format(opt, value))

  class DateOption(Option):
    TYPES = Option.TYPES + ("date",)
    TYPE_CHECKER = copy(Option.TYPE_CHECKER)
    TYPE_CHECKER["date"] = date_checker

  return OptionParser(option_class=DateOption)

def last_monday():
  today = datetime.today()
  return (today - timedelta(days=today.weekday())).date()

def next_friday():
  today = datetime.today()
  return (today + timedelta(days=4-today.weekday())).date()

def secs_to_hms_str(seconds):
  """Format an amount of seconds as a hh:mm:ss string."""
  return "{0}:{1:02}:{2:02}".format(seconds/60/60, seconds/60%60, seconds%60)
