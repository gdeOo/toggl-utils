import os
import json
import urllib
import requests
import pytz
from datetime import datetime, time
from ConfigParser import ConfigParser


def config():
  """Get parameters from the configuration file.

  Returns:
    A dictionary with the following items:
      api_token: The token used for authentication with the toggl API
      timezone:  A valid pytz timezone name used in toggl API requests
  """
  try:
    return config._config
  except AttributeError:
    config_filename = os.path.splitext(os.path.basename(__file__))[0] + ".config"
    parser = ConfigParser()
    parser.read(config_filename)
    api_token = parser.get("auth", "api_token")
    timezone = parser.get("settings", "timezone")
    config._config = {
      "api_token": api_token,
      "timezone": pytz.timezone(timezone)
    }
    return config._config

class Toggl:
  """Wrapper over the Toggl API."""

  def __init__(self):
    self._auth = (config()["api_token"], "api_token")
    self._headers = { "Content-Type":  "application/json" }
    self._api_base = "https://www.toggl.com/api/v8"
    self._tz = config()["timezone"]

  def _get(self, path):
    """Invokes a GET method of the toggl API."""
    url = self._api_base + path
    r = requests.get(url, auth=self._auth, headers=self._headers)
    r.raise_for_status()
    return r.json()

  def _put(self, path, body):
    """Invokes a PUT method of the toggl API."""
    url = self._api_base + path
    r = requests.put(url, json.dumps(body), auth=self._auth, headers=self._headers)
    r.raise_for_status()
    return r.json()

  def login(self):
    """Invoke the /me API method and return the response."""
    return self._get("/me")

  def get_day_time_entries(self, day):
    """Get the time entries for a given day by invoking the GET /time_entries API method."""
    day_start = datetime.combine(day, time(00, 00, 00, tzinfo=self._tz))
    day_end = datetime.combine(day, time(23, 59, 59, tzinfo=self._tz))
    url = "/time_entries?" + urllib.urlencode({
      "start_date": day_start.isoformat(), "end_date": day_end.isoformat()})
    return self._get(url)

  def update_time_entry_duration(self, id, duration):
    """Update the duration of a time entry by invoking the PUT /time_entries/<id> API method."""
    return self._put("/time_entries/{0}".format(id), {
      "time_entry": {
        "duration": duration
      }})

  def get_project(self, project_id):
    """Gets the properties of the project with a given id."""
    return self._get("/projects/{0}".format(project_id))
