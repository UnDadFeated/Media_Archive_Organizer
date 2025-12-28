import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ui.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
