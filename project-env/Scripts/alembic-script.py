#!"c:\users\jaspe\documents\cornell spring 2021\cs 4300\cs4300sp2021-ag2496-cc972-mb2359-jjz67-jxl8\project-env\scripts\python.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'alembic==1.4.0','console_scripts','alembic'
__requires__ = 'alembic==1.4.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('alembic==1.4.0', 'console_scripts', 'alembic')()
    )
