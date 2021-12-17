import octoprint.plugin
import octoprint.events
import hashlib
import os
import requests
from pygcode import Line

# API Interface function
def cancel_print(self):
    url = "http://192.168.1.48/api/job"
    req = {"command": "cancel"}
    headers = {"Content-Type": "application/json", "X-Api-Key":"21BA190BCA9E49289245D9D0B36C9CE1"}
    resp = requests.post(url, headers = headers, json = req)
    self._logger.info(resp.status_code)

# Hashing function
def hash(filename):

    file = open(filename, "rb")

    # BUF_SIZE is the maximum chunk size being read
    BUF_SIZE = 65536  # 64kb chunks

    sha1 = hashlib.sha1()

    while True:
        data = file.read(BUF_SIZE)
        if not data:
            break
        sha1.update(data)

    return(sha1.hexdigest())

# Plugin Class
class secure(octoprint.plugin.AssetPlugin, octoprint.plugin.EventHandlerPlugin):

    # Event handler
    def on_event(self, event, payload):
        # Handle file upload and create hash
        if event == octoprint.events.Events.FILE_ADDED:
            file_hash = hash("/home/pi/.octoprint/uploads/" + payload["path"])
            self._logger.info(file_hash)
            dir = "/home/pi/.octoprint/"
            try:
                os.mkdir(home + "hashes")
            except:
                pass
            dir += "hashes/"
            hash_file = open(dir + payload["name"] + ".hash", "w")
            hash_file.write(file_hash)
            hash_file.close()
        # Handle file deletion
        if event == octoprint.events.Events.FILE_REMOVED:
            self._logger.info(payload["name"])
            os.remove("/home/pi/.octoprint/hashes/" + payload["name"] + ".hash")
        # Handle printing, check hash
        if event == octoprint.events.Events.PRINT_STARTED:
            ptime_hash = hash("/home/pi/.octoprint/uploads/" + payload["path"])
            hash_file = open("/home/pi/.octoprint/hashes/" + payload["name"] + ".hash", "r")
            orig_hash = hash_file.read()
            hash_file.close()
            if orig_hash == ptime_hash:
                self._logger.info("Print time hash matches upload time hash. Continuing print.")
            else:
                self._logger.info("Hashes do not match, file has been edited. Cancelling print.")
                cancel_print(self)
            # Check gcode syntax
            with open("/home/pi/.octoprint/uploads/" + payload["path"]) as g:
                for raw_line in g.readlines():
                    try:
                        g_line = Line(raw_line)
                    except:
                        self._logger.info("Incorrect gcode syntax. Cancelling print.")
                        cancel_print(self)
                        break

# Plugin information
__plugin_name__ = "SmartEnder3"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = secure()
