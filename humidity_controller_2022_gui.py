"""
tkinter: See https://www.tutorialspoint.com/python3/python_gui_programming.htm
"""
import tkinter
import pathlib
import logging
import time

import simple_pid
import datafile_csv

logger = logging.getLogger("humidity_controller_2022")

logger.setLevel(logging.DEBUG)

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).absolute().parent

START_TIME = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
FILENAME_LOG = DIRECTORY_OF_THIS_FILE / "log" / f"controller_{START_TIME}.txt"
FILENAME_LOG.parent.mkdir(parents=True, exist_ok=True)


try:
    import mp
    import mp.version
    import mp.micropythonshell
    import mp.pyboard_query
except ModuleNotFoundError as ex:
    raise Exception(
        'The module "mpfshell2" is missing. Did you call "pip -r requirements.txt"?'
    )


class Pico:
    def __init__(self):
        self.board = mp.pyboard_query.ConnectHwtypeSerial(
            product=mp.pyboard_query.Product.RaspberryPico
        )
        assert isinstance(self.board, mp.pyboard_query.Board)
        self.board.systemexit_firmware_required(min="1.19.0", max="1.21.0")

        self.shell = self.board.mpfshell
        self.fe = self.shell.MpFileExplorer
        # Download the source code
        self.shell.sync_folder(DIRECTORY_OF_THIS_FILE / "src_micropython")
        # Start the program
        self.fe.exec_("import micropython_logic")

    def get_status(self) -> str:
        str_status = self.fe.eval("micropython_logic.get_status()")
        return str_status

    def get_measurement(self) -> dict:
        humidityRH = self.fe.eval("micropython_logic.get_measurement()")
        return eval(humidityRH)

    def set_fan_intensity(self, intensity_K: float) -> None:
        assert isinstance(intensity_K, float)
        str_value = self.fe.eval(
            f"micropython_logic.set_fan_intensity({intensity_K:0.2f})"
        )
        #value = float(str_value)
        # return value


class Entry:
    def __init__(self, parent, text):
        frame = tkinter.Frame(parent)
        label = tkinter.Label(frame, text=text)
        label.pack(side=tkinter.LEFT)
        self._var = tkinter.DoubleVar()
        self._entry = tkinter.Entry(frame, textvariable=self._var)
        self._entry.pack(side=tkinter.RIGHT)
        frame.pack(side=tkinter.TOP)

    @property
    def value(self) -> float:
        return self._var.get()

    @value.setter
    def value(self, value: float) -> None:
        assert isinstance(value, float)
        self._var.set(value)

    @value.setter
    def enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "readonly"
        self._entry.config(state=state)


class Window:
    def __init__(self):
        self._root = tkinter.Tk(className="Humidty Controller 2022")
        self._root.maxsize(3000, 2000)
        self._root.geometry('1000x500')
        self.entry_setRH = Entry(self._root, "Set %RH")
        self.entry_kp = Entry(self._root, "Kp")
        self.entry_ki = Entry(self._root, "Ki")
        self.entry_kd = Entry(self._root, "Kd")
        self._var_controller = self.add_check("controller on")
        self._var_circ = self.add_check("circulation on")

        self._text = tkinter.Text(self._root)
        self._text.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def text(self, msg: str):
        self._text.insert("1.0", msg)

    def timer(self, interval_ms, callback):
        """
        The controller registers a callback
        """

        def time_over():
            self._root.after(interval_ms, time_over)
            callback()

        time_over()

    @property
    def controller_on(self) -> bool:
        return self._var_controller.get() == 1

    @property
    def circ_on(self) -> bool:
        return self._var_circ.get() == 1

    def callback_controller(self, callback):
        """
        The controller registers a callback
        """

        def cb(*args):
            callback(on=self.controller_on)

        self._var_controller.trace_add("write", cb)

    def callback_circ(self, callback):
        """
        The controller registers a callback
        """

        def cb(*args):
            callback(on=self.circ_on)

        self._var_circ.trace_add("write", cb)

    def add_check(self, text):
        check_var = tkinter.IntVar()
        check_button = tkinter.Checkbutton(
            self._root, text=text, variable=check_var, onvalue=True, offvalue=False
        )
        check_button.pack(side=tkinter.TOP)
        return check_var

    def mainloop(self):
        self._root.mainloop()


class Controller:
    def __init__(self, pico: Pico, window: Window):
        self._pico = pico
        self._window = window
        self._starttime = time.time()

        self._csv = datafile_csv.Csv(FILENAME_LOG)
        self.fan_intensity=0.0

        window.callback_controller(callback=self._button_pressed_controller)
        window.callback_circ(callback=self._button_pressed_circ)

        self._window.entry_setRH.value = 10.0
        self._window.entry_kp.value = 0.05
        self._window.entry_ki.value = 0.01
        self._window.entry_kd.value = 0.0

        self.pid = simple_pid.PID(sample_time=0.6, output_limits=(
            0.0, 100.0), proportional_on_measurement=False)

        # Start the controller
        window.timer(interval_ms=1000, callback=self._control)

    def _control(self):
        # print(self._window.entry_kd.get())
        #value = self._pico.set_fan_intensity(2.1)
        #print(f"Control 2.1->{value}")
        self._csv.time=int(time.time() - self._starttime)
        _dict = self._pico.get_measurement()
        self._csv.fan=self.fan_intensity
        self._csv.set_humi_pRH=self.pid.setpoint
        self._csv.humi_humi_pRH=float(_dict.get('humi_humi_pRH'))
        self._csv.stage_humi_pRH=float(_dict.get('stage_humi_pRH'))
        self._csv.humi_temp_C=float(_dict.get('humi_temp_C'))
        self._csv.stage_temp_C=float(_dict.get('stage_temp_C'))
        #self._window.text(f"ping {self._counter} {self._csv.rh:0.1f} RH \n")
        self._csv.write()
        self._window.text(f"{self._csv.text}\n")

        if not self._window.controller_on:
            #self.pid.set_auto_mode(False)
            self.fan_intensity=0.0
            self._pico.set_fan_intensity(0.0)
        else:
            #self.pid.set_auto_mode(True, last_output=0.0)
            self.fan_intensity = self.pid(self._csv.humi_humi_pRH)
            print(self.fan_intensity)
            #print(self.pid(self._csv.humi_humi_pRH))
            #print(self.pid)
            #print(self.pid(44.3))
            #print(self._csv.humi_humi_pRH)
            self._pico.set_fan_intensity(self.fan_intensity)


    def _button_pressed_controller(self, on: bool):
        print(f"vent {on}")
        enabled = not on
        if on:
            self._window.entry_setRH.enabled = enabled
            self._window.entry_kd.enabled = enabled
            self._window.entry_ki.enabled = enabled
            self._window.entry_kp.enabled = enabled
            self.pid.Kp=self._window.entry_kp.value
            self.pid.Ki=self._window.entry_ki.value
            self.pid.Kd=self._window.entry_kd.value
            self.pid.setpoint=self._window.entry_setRH.value
            self.pid.reset()
            print('blabliblaenabled')

    def _button_pressed_circ(self, on: bool):
        print(f"circ {on}")


def main():
    pico = Pico()

    window = Window()

    controller = Controller(pico=pico, window=window)

    window.mainloop()


if __name__ == "__main__":
    main()
