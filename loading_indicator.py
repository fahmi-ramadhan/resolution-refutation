import sys
from itertools import cycle
import threading
import time

class LoadingIndicator:
    """
    A simple loading indicator to show that the program is still running.
    """
    def __init__(self, description="Processing"):
        self.description = description
        self.is_running = False
        self.spinner = cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.spinner_thread = None
        
    def _spin(self):
        """Internal method to update the spinner"""
        while self.is_running:
            sys.stdout.write(f"\r{self.description} {next(self.spinner)} ")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(self.description) + 10) + "\r")
        sys.stdout.flush()
        
    def start(self):
        """Start the loading indicator"""
        self.is_running = True
        self.spinner_thread = threading.Thread(target=self._spin)
        self.spinner_thread.daemon = True
        self.spinner_thread.start()
        
    def stop(self):
        """Stop the loading indicator"""
        self.is_running = False
        if self.spinner_thread is not None:
            self.spinner_thread.join()
