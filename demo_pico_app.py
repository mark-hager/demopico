from ScopeFoundry import BaseMicroscopeApp

class DemoPicoApp(BaseMicroscopeApp):

    name = 'demo_pico_app'

    def setup(self):

        from demo_pico_hw import DemoPicoHW
        self.add_hardware(DemoPicoHW(app=self))

        from demo_pico_datalog_measure import DemoPicoDataLogMeasurement
        self.add_measurement(DemoPicoDataLogMeasurement(app=self))

        # Load settings from an INI file
        self.settings_load_ini("demo_pico_app_defaults.ini")

if __name__ == '__main__':

    app = DemoPicoApp()
    #app.qtapp.setStyle("Fusion")

    app.exec_()