__author__ = 'Raquel'

from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from socket import error as SocketError

# <editor-fold desc="Protocol constants">
HTTP = 'http://'
preFTP = 'ftp://'
# </editor-fold>


def check_link(url):
    if url:
        try:
            urlopen(url, timeout=12)
        except HTTPError as e:
            return "{}, {}".format(e.reason, e.code)
        except URLError as e:
            return "{}".format(e.reason)
        except SocketError:
            return "Socket Error"
        except ValueError:
            return "Value Error"
    else:
        return "No link"
    return "working"