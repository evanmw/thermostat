from flask import Flask, render_template, jsonify, request
import logging

class WebServer():
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.app = Flask(__name__)

        self.temps = data.temps
        self.get_setpoint = data.get_setpoint
        self.set_setpoint = data.set_setpoint
        
        # define routes
        self.app.add_url_rule('/', 'home', view_func=self.index)
        self.app.add_url_rule('/_set_temp', 'asdf', view_func=self.set_temp)
        self.app.add_url_rule('/_poll_data', 'asdfs', view_func=self.poll_data)
        
    def index(self):
        temp=round(self.temps['local'][-1][1], 1)
        setpoint_temp=round(self.get_setpoint()[0], 1)
        return render_template('index.html', temp=temp, setpoint_temp=setpoint_temp)

    def set_temp(self):
        current_setpoint = self.get_setpoint()
        temp_change = request.args.get('temp', 0, type=int)
        self.set_setpoint(current_setpoint[0]+temp_change, current_setpoint[1])
        return jsonify(setpoint_temp=round(self.get_setpoint()[0], 1))

    def poll_data(self):
        current_setpoint = self.get_setpoint()
        current_temp = self.temps['local'][-1][1]
        reply=jsonify(setpoint_temp=round(current_setpoint[0],1),
                      temp=round(current_temp, 1))
        return reply
    
    def run(self):
        logging.warn("starting flask")
        self.app.run(host='0.0.0.0', port=80, debug=True, use_reloader=False)
        logging.warn("closing flask")

        
if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=80, debug=True)
    pass
