import sys
import os
from pathlib import Path

from ..singleton import Singleton


class PathBuilder(metaclass=Singleton):

    def __init__(self):
        """
        Build absolute project path.
        """

        # First script called
        self.invoker = Path(os.getcwd()) / Path(sys.argv[0])

        # Project folder (root)
        sufix = 'src' + os.sep + str(__name__).replace('.', os.sep) + '.py'
        self.project = Path(__file__.replace(sufix, ''))

        # Log folder
        self.log = self.project / 'log'

        # SQL scripts folder
        self.sql = self.project / 'sql'

        # Database file
        self.db_file = self.project / 'database.db'

        # Config JSON file
        self.config_file = self.project / 'config.json'
