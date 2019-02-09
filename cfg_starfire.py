#!/usr/bin/python3

import socket, threading, time
import nmea

from tkinter import *
from tkinter import ttk

terminate = False


class Connection:
    def __init__(self, ipAddress, port, callback=None):
        try:
            self._sock = socket.create_connection((ipAddress, port), 1.0)

        except socket.error:
            print("Connection Failed")
            self._sock = None
            return

        self._callback = callback
        self._terminate = False
        self._lock = threading.Lock()
        self._th = threading.Thread(target=self._gga, args=(self._lock,))
        self._th.start()

    def is_connected(self):
        return self._sock is not None

    def _gga(self, cv):
        with cv:
            term = self._terminate

        full_string = ""
        while not term:
            try:
                data = self._sock.recv(10)
                full_string += str(data, "utf-8")
                crlf = full_string.find("\r\n")
                if crlf != -1:
                    data_string = full_string[:crlf]
                    full_string = full_string[crlf+2:]

                    if data and self._callback:
                        self._callback(data_string)

            except socket.error:
                if not self._sock:
                    break;

            with cv:
                term = self._terminate

        print("Terminate")
        if self._sock:
            self._sock.close()

    def terminate(self):
        if not self._sock:
            return

        self._sock.close()
        time.sleep(0.1)
        with self._lock:
            self._terminate = True

        self._th.join(timeout=1.0)
        self._sock = None

    def send(self, command):
        if self._sock:
            self._sock.send(bytes(command, encoding="utf-8"))


class GPSFrame(ttk.Frame):

    def __init__(self, master):
        ttk.Frame.__init__(self, master)

        self._cnt = None

        self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)

        # frame for ip address
        Label(self, text="IP address").grid(column=0, row=0, sticky='w')
        Label(self, text="Port").grid(column=0, row=1, sticky='w')

        self._ipAddress = StringVar()
        self._ipAddressEntry = Entry(self, textvariable=self._ipAddress)
        self._ipAddressEntry.grid(column=1, row=0, sticky='nw')

        self._port = IntVar()
        self._portEntry = Entry(self, textvariable=self._port)
        self._portEntry.grid(column=1, row=1, sticky='nw')

        self._connectBtn = Button(self, text="Connect", command=self._connect)
        self._connectBtn.grid(column=2, row=0, rowspan=2, sticky=(E, N))

        # frame for GPS LOG
        self._firstFrame = Frame(self, bg="gray", bd=0)
        self._firstFrame.grid(column=0, row=2, sticky=(W, N, E), columnspan=3)

        self._firstFrame.columnconfigure(0, weight=1)
        self._firstFrame.rowconfigure(0, weight=1)

        self._text_log = Text(self._firstFrame)
        self._vsb = Scrollbar(self._firstFrame, orient="vertical", command=self._text_log.yview)
        self._vsb.pack(side="right", fill="y")
        self._text_log.config(state=DISABLED, background="gray", yscrollcommand=self._vsb)
        self._text_log.pack(side="left", fill='both', expand=True)

        # frame with Input and Button
        self._secondFrame = Frame(self)
        self._secondFrame.grid(column=0, row=3, sticky=(W, N, E, S), columnspan=3)
        self._secondFrame.columnconfigure(0, weight=1)
        self._secondFrame.rowconfigure(3, weight=1)

        self._inputField = StringVar()
        self._inputCommand = ttk.Entry(self._secondFrame,  textvariable=self._inputField)
        self._inputCommand.grid(column=0, row=0, sticky=(W, N, S, E))
        self._inputCommand.columnconfigure(0, weight=1)

        self._sendButton = ttk.Button(self._secondFrame, text="Send", command=self._send)
        self._sendButton.grid(column=1, row=0, sticky=(E, N, S))

        # Command response
        self._commandFrame = Frame(self, bg="gray", bd=0)
        self._commandFrame.grid(column=0, row=4, sticky=(W, N, E, S), columnspan=3)

        self._commandFrame.columnconfigure(0, weight=1)
        self._commandFrame.rowconfigure(0, weight=1)

        self._cmd_log = Text(self._commandFrame, height=10)
        self._cmd_vsb = Scrollbar(self._commandFrame, orient="vertical", command=self._cmd_log.yview)
        self._cmd_vsb.pack(side="right", fill="y")
        # self._cmd_vsb.grid(column=1, row=0, sticky='nes')
        self._cmd_log.config(state=DISABLED, background="gray", yscrollcommand=self._cmd_vsb)
        # self._cmd_log.grid(column=0, row=0, sticky='nws')
        self._cmd_log.pack(side="left", fill='both', expand=True)

        self.bind("<Destroy>", self._delete_window)

        self._latitude = DoubleVar()
        self._lat_label = Label(self, text="Latitude").grid(column=0, row=5, sticky='wn')
        self._lat_entry = Entry(self, state='readonly', bg='gray', textvariable=self._latitude)
        self._lat_entry.grid(column=0, row=6, sticky='wn')

        self._longitude = DoubleVar()
        self._lon_label = Label(self, text="Longitude").grid(column=1, row=5, sticky='wn')
        self._lon_entry = Entry(self, state='readonly', bg='gray', textvariable=self._longitude)
        self._lon_entry.grid(column=1, row=6, sticky='wn')

        self._altitude = DoubleVar()
        self._alt_label = Label(self, text="Altitude").grid(column=2, row=5, sticky='wn')
        self._alt_entry = Entry(self, state='readonly', bg='gray', textvariable=self._altitude)
        self._alt_entry.grid(column=2, row=6, sticky='wn')

        self._gnss = nmea.GNSS()

    def _connect(self):
        if not self._cnt:
            self._cnt = Connection(self._ipAddress.get(), self._port.get(), self._callback)
            if self._cnt.is_connected():
                self._connectBtn['text'] = "Disconnect"
        else:
            self._cnt.terminate()
            if not self._cnt.is_connected():
                self._connectBtn['text'] = "Connect"
                self._cnt = None

    def _callback(self, data_string):
        log_string = re.sub(r'\r\n', r'', data_string)
        log_string += '\n'

        if self._text_log and log_string[0] != '[':
            self._text_log.config(state=NORMAL)
            self._text_log.insert('end', log_string)
            self._text_log.see('end')
            self._text_log.config(state=DISABLED)
            self._gnss.add_nmea_string(data_string)

            self._latitude.set(self._gnss.latitude)
            self._longitude.set(self._gnss.longitude)
            self._altitude.set(self._gnss.altitude)

        elif self._cmd_log and log_string[0] == '[':
            self._cmd_log.config(state=NORMAL)
            self._cmd_log.insert('end', log_string)
            self._cmd_log.see('end')
            self._cmd_log.config(state=DISABLED)

    def _send(self):
        cmd_strings = re.split(r'\s|,', self._inputField.get())
        if cmd_strings.__len__() > 0:
            if cmd_strings[0][0] != '[':
                cmd_strings[0][0].strip()
                cmd_strings[0] = '[' + cmd_strings[0] + ']'

            full_string = cmd_strings[0]
            if cmd_strings.__len__() > 1:
                full_string += ' '
                full_string += cmd_strings[1]

            for x in cmd_strings[2:]:
                full_string += ',' + x

            full_string += '\r\n'
            if self._cnt:
                self._cnt.send(full_string)

    def terminate(self):
        if self._cnt:
            self._cnt.terminate()

        self._cnt = None

    def _delete_window(self, event):
        if self._cnt:
            self._cnt.terminate()


def close_connections():
    if gps1:
        gps1.terminate()

    if gps2:
        gps2.terminate()

    root.destroy()


root = Tk()
root.title("GPS")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

s = ttk.Style()
s.configure('TNotebook', tabposition='nw')

tabs = ttk.Notebook(root)
gps1 = GPSFrame(tabs)
gps2 = GPSFrame(tabs)

tabs.add(gps1, text='GPS Front')
tabs.add(gps2, text='GPS Back')
tabs.pack(expand=1, fill='both')

root.protocol('WM_DELETE_WINDOW', close_connections)

root.mainloop()
