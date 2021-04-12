#!"c:\users\jaspe\documents\cornell spring 2021\cs 4300\cs4300sp2021-ag2496-cc972-mb2359-jjz67-jxl8\project-env\scripts\python.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'Mako==1.1.1','console_scripts','mako-render'
__requires__ = 'Mako==1.1.1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('Mako==1.1.1', 'console_scripts', 'mako-render')()
    )
