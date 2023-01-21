"""
tkinter: See https://www.tutorialspoint.com/python3/python_gui_programming.htm
"""
import tkinter
import pathlib
import logging

logger = logging.getLogger("humidity_controller_2022")

logger.setLevel(logging.DEBUG)

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).absolute().parent

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

    def set_fan_intensity(self, intensity_K: float) -> None:
        assert isinstance(intensity_K, float)
        str_value = self.fe.eval(
            f"micropython_logic.set_fan_intensity({intensity_K:0.2f})"
        )
        value = float(str_value)
        return value


class Window:
    def __init__(self):
        self._top = tkinter.Tk(className="Humidty Controller 2022")

        # def helloCallBack():
        #     msg = tkinter.messagebox.showinfo("Hello Python", "Hello World")

        # w = tkinter.Button(top, text="On/Off", command=helloCallBack)
        # w.pack()
        self._var_vent = self.add_check("On/Off Ventilation")
        self._var_circ = self.add_check("On/Off Circulation")
        self.entry_kp = self.add_entry("Kp")
        self.entry_ki = self.add_entry("Ki")
        self.entry_kd = self.add_entry("Kd")

        self._text = tkinter.Text(self._top)
        self._text.pack()

    def text(self, msg: str):
        self._text.insert("1.0", msg)

    def timer(self, interval_ms, callback):
        """
        The controller registers a callback
        """

        def time_over():
            self._top.after(interval_ms, time_over)
            callback()

        time_over()

    def callback_vent(self, callback):
        """
        The controller registers a callback
        """

        def cb(*args):
            callback(on=self._var_vent.get() == 1)

        self._var_vent.trace_add("write", cb)

    def callback_circ(self, callback):
        """
        The controller registers a callback
        """

        def cb(*args):
            callback(on=self._var_circ.get() == 1)

        self._var_circ.trace_add("write", cb)

    def add_entry(self, text):
        frame = tkinter.Frame(self._top)
        label = tkinter.Label(frame, text=text)
        label.pack(side=tkinter.LEFT)
        entry = tkinter.Entry(frame)
        entry.pack(side=tkinter.RIGHT)
        frame.pack()
        return entry

    def add_check(self, text):
        check_var = tkinter.IntVar()
        check_button = tkinter.Checkbutton(
            self._top, text=text, variable=check_var, onvalue=True, offvalue=False
        )
        check_button.pack()
        return check_var

    def mainloop(self):
        self._top.mainloop()


class Controller:
    def __init__(self, pico: Pico, window: Window):
        self._pico = pico
        self._window = window

        window.timer(interval_ms=1000, callback=self._control)
        window.callback_vent(callback=self._button_pressed_vent)
        window.callback_circ(callback=self._button_pressed_circ)

    def _control(self):
        value = self._pico.set_fan_intensity(2.1)
        print(f"Control 2.1->{value}")
        self._window.text("ping\n")

    def _button_pressed_vent(self, on: bool):
        print(f"vent {on}")

    def _button_pressed_circ(self, on: bool):
        print(f"circ {on}")


def main():
    pico = Pico()

    window = Window()

    controller = Controller(pico=pico, window=window)

    window.mainloop()


if __name__ == "__main__":
    main()
