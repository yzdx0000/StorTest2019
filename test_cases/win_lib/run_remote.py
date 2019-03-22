from robotremoteserver import RobotRemoteServer as Rs
from nas_common_win import Smb, Ftp
# from Bao import Bao, Liyao


class RunRemoteServer(Smb, Ftp):
    def __init__(self):
        pass


if __name__ == '__main__':
    instance = RunRemoteServer()
    Rs(instance, host='10.2.41.253', port=8270)
