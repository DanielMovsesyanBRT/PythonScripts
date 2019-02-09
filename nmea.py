import re, math


class GNSS:
    def __init__(self):
        self._gp = {
            "$GPAAM": self.aam,
            "$GPALM": self.alm,
            "$GPAPA": self.apa,
            "$GPAPB": self.apa,
            "$GPBOD": self.bod,
            "$GPBWC": self.bwc,
            "$GPGGA": self.gga,
            "$GNGGA": self.gga,
            "$GPGLL": self.gll,
            "$GNGLL": self.gll,
            "$GPGSA": self.gsa
        }

        self._latitude = 0.0
        self._longitude = 0.0
        self._altitude = 0.0

    def add_nmea_string(self, data_string):
        data_array = re.split(',', data_string)
        for x in data_array:
            x.strip()

        if len(data_array) > 0 and data_array[0][0] == '$':
            func = self._gp.get(data_array[0])
            if func:
                func(data_array)

    # AAM - Waypoint Arrival Alarm
    def aam(self, data_array):
        pass

    # ALM - Almanac data
    def alm(self, data_array):
        pass

    # APA, APB Auto Pilot sentence
    def apa(self, data_array):
        pass

    # BOD - Bearing Origin to Destination
    def bod(self, data_array):
        pass

    # BWC - Bearing using Great Circle route
    def bwc(self, data_array):
        pass

    # GGA - Fix information
    def gga(self, data_array):
        try:
            if len(data_array) >= 13:
                # Latitude
                self._latitude = self._deg2num(float(data_array[2]))
                if data_array[3] == 'S':
                    self._latitude = -self._latitude

                # Longitude
                self._longitude = self._deg2num(float(data_array[4]))
                if data_array[5] == 'W':
                    self._longitude = -self._longitude

                self._altitude = float(data_array[9])
        except ValueError:
            pass

    # GLL - Lat/Lon data
    def gll(self, data_array):
        try:
            if len(data_array) >= 5:
                # Latitude
                self._latitude = self._deg2num(float(data_array[1]))
                if data_array[2] == 'S':
                    self._latitude = -self._latitude

                # Longitude
                self._longitude = self._deg2num(float(data_array[3]))
                if data_array[4] == 'W':
                    self._longitude = -self._longitude
        except ValueError:
            pass

    # GSA - Overall Satellite data
    def gsa(self, data_array):
        pass

    # GST - GPS Pseudorange Noise Statistics
    def gst(self, data_array):
        pass

    # GSV - Detailed Satellite data
    def gsv(self, data_array):
        pass

    # MSK - send control for a beacon receiver
    def msk(self, data_array):
        pass

    # MSS - Beacon receiver status information.
    def mss(self, data_array):
        pass

    # VTG - Vector track an Speed over the Ground
    def vtg(self, data_array):
        pass

    def _deg2num(self, value):
        _deg = math.floor(value / 100)
        _min = ((value / 100) - _deg) * 100.0
        return _deg + _min / 60.0

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def altitude(self):
        return self._altitude
