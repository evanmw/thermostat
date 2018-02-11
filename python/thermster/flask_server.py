from flask import Flask, render_template, jsonify, request
import logging
import json
from thermostat_scheduler import ThermostatScheduler

class WebServer():
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.app = Flask(__name__)

        self.temps = data.temps
        self.get_setpoint = data.get_setpoint
        self.set_setpoint = data.set_setpoint

        self.scheduler = ThermostatScheduler(data.sheshule,
                                             data.shesh_lock,
                                             data.SCHEDULE_FILE_PATH,
                                             data.set_setpoint)

        # define routes
        self.app.add_url_rule('/', 'home', view_func=self.index)
        self.app.add_url_rule('/_increment_temp', 'asdf', view_func=self.increment_temp)
        self.app.add_url_rule('/_set_temp', 'sasds', view_func=self.set_temp,methods=["GET","POST"])
        self.app.add_url_rule('/_poll_data', 'asdfs', view_func=self.poll_data)
        self.app.add_url_rule('/_update_schedule', 'asasa', view_func=self.update_schedule)

    def index(self):
        temp=0
        if len(self.temps['local']) > 0:
               temp=round(self.temps['local'][-1][1], 1)
        setpoint_temp=round(self.get_setpoint()[0], 1)
        return render_template('index.html',
                               temp=temp,
                               setpoint_temp=setpoint_temp,
                               schedule_entries=self.scheduler.read_schedule())

    def increment_temp(self):
        current_setpoint = self.get_setpoint()
        temp_change = request.args.get('temp', 0, type=int)
        self.set_setpoint(current_setpoint[0]+temp_change, current_setpoint[1])
        return jsonify(setpoint_temp=round(self.get_setpoint()[0], 1))

    def set_temp(self):
        logging.warn("Got command from IFTTT")
        logging.warn(request.get_json())
        current_setpoint = self.get_setpoint()
        data=request.get_json()
        new_temp = int(data["temp"])
        logging.warn("Setting temperature to %i from Google" % new_temp)
        if new_temp > 40:
            new_temp = (new_temp-32)*(5/9)
        self.set_setpoint(new_temp, current_setpoint[1])
        return jsonify(1)

    def poll_data(self):
        current_setpoint = self.get_setpoint()
        if len(self.temps['local']) > 0:
            current_temp = self.temps['local'][-1][1]
        reply=jsonify(setpoint_temp=round(current_setpoint[0], 1),
                      temp=round(current_temp, 1))
        return reply

    def update_schedule(self):
        entries = json.loads(request.args.get('payload'))
        for entry in entries:
            entry['days'] = self.scheduler.check_days(entry['days'])
            entry['time'] = self.scheduler.check_time(entry['time'])
            entry['temp'] = self.scheduler.check_temp(entry['temp'])
            entry['weight']=self.scheduler.check_weight(entry['weight'])
            for key in entry.keys():
                if not entry[key]:
                    reply= "Error: could not parse '%s' field" % key.capitalize()
                    return jsonify(success='false', message=reply)
        self.scheduler.write_file_from_dict(entries)
        return jsonify(success='true', message="Schedule updated")

    def run(self):
        logging.warn("starting flask")
        self.app.run(host='0.0.0.0', port=80, debug=True,
                     use_reloader=False, threaded=True)
        logging.warn("closing flask")


if __name__ == '__main__':
    pass
