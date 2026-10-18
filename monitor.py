"""
SpeedX - Bandwidth Calculation Worker Thread
Samples system-wide network counters every 1.0 second in a dedicated QThread
and calculates high-precision download and upload throughput delta.
"""

import time
import psutil
from PySide6.QtCore import QThread, Signal
import config


class BandwidthMonitor(QThread):
    """
    Dedicated background worker thread for sampling psutil.net_io_counters.
    Calculates: Speed = (bytes_current - bytes_previous) / delta_time.
    """
    # Emits: (dl_bytes_per_sec, ul_bytes_per_sec, dl_val_str, dl_unit_str, ul_val_str, ul_unit_str)
    speed_updated = Signal(float, float, str, str, str, str)

    def __init__(self, interval: float = 1.0, unit_format: str = "bytes", parent=None):
        super().__init__(parent)
        self.interval = max(0.2, interval)
        self.unit_format = unit_format
        self._running = True

    def set_unit_format(self, unit_format: str):
        """Update the active unit format (bytes or bits) without restarting thread."""
        self.unit_format = unit_format

    def stop(self):
        """Gracefully stop the sampling thread."""
        self._running = False

    def run(self):
        try:
            initial_io = psutil.net_io_counters()
            prev_recv = initial_io.bytes_recv
            prev_sent = initial_io.bytes_sent
        except Exception as e:
            print(f"[SpeedX Monitor] Initialization error: {e}")
            prev_recv = 0
            prev_sent = 0

        prev_time = time.perf_counter()

        while self._running:
            # Sleep in small chunks to respond quickly to stop requests
            sleep_chunks = int(self.interval / 0.1)
            for _ in range(max(1, sleep_chunks)):
                if not self._running:
                    return
                time.sleep(0.1)

            curr_time = time.perf_counter()
            delta_time = max(0.001, curr_time - prev_time)
            prev_time = curr_time

            try:
                curr_io = psutil.net_io_counters()
                dl_speed = max(0.0, (curr_io.bytes_recv - prev_recv) / delta_time)
                ul_speed = max(0.0, (curr_io.bytes_sent - prev_sent) / delta_time)

                prev_recv = curr_io.bytes_recv
                prev_sent = curr_io.bytes_sent

                dl_val, dl_unit = config.format_speed(dl_speed, self.unit_format)
                ul_val, ul_unit = config.format_speed(ul_speed, self.unit_format)

                self.speed_updated.emit(dl_speed, ul_speed, dl_val, dl_unit, ul_val, ul_unit)
            except Exception as e:
                print(f"[SpeedX Monitor] Sampling error: {e}")
