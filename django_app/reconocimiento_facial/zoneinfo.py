
import sys
import backports.zoneinfo

sys.modules['zoneinfo'] = backports.zoneinfo
