#!/usr/bin/env python3

import os
import sys
import datetime
import logging
import re

zfs_valid_time = 7*86400
zfs_snapshot_fmt = "snapshot-%Y%m%d-%H%M"
zfs_bin = "/sbin/zfs"


def log_init():
    logging.basicConfig(
        filename=os.path.dirname(__file__)+"/logs/zfssnapshot.log",
        filemode="a",
        format="%(asctime)s %(message)s",
        level=logging.INFO
    )


def log(msg):
    logging.info(msg)


class ZfsSnapshot:
    def __init__(self, vol, name, create_time=0.0, expire_time=0.0):
        self.vol = vol
        self.name = name
        self.create_time = create_time
        self.expire_time = expire_time

    def __str__(self):
        return " volume: %s \n name: %s \n create time: %f\n expire time: %f \n" % (self.vol,
                                                                                    self.name,
                                                                                    self.create_time,
                                                                                    self.expire_time)


class ZfsVolume:
    def __init__(self, vol):
        self.zfs_vol = vol
        self.snapshot_list = []

    def snapshot(self):
        now = datetime.datetime.now()
        snapshot_name = now.strftime(zfs_snapshot_fmt)
        zfs_cmd = "%s snapshot %s@%s" % (zfs_bin, self.zfs_vol, snapshot_name)
        if os.system(zfs_cmd) == 0:
            log("command succeeded when exec: %s" % zfs_cmd)
        else:
            log("command failed when exec: %s" % zfs_cmd)

        pass

    def get_snapshot_list(self):
        zfs_dir = "/"+self.zfs_vol+"/.zfs/snapshot"

        if os.path.exists(zfs_dir):
            ss_list = os.listdir(zfs_dir)
        else:
            ss_list = []

        for ss in ss_list:
            snapshot = ZfsSnapshot(self.zfs_vol, ss)
            m = re.search("^snapshot-(\\d{4})(\\d{2})(\\d{2})-(\\d{2})(\\d{2})", ss)
            year = int(m.group(1))
            month = int(m.group(2))
            day = int(m.group(3))
            hour = int(m.group(4))
            minute = int(m.group(5))

            ss_time = datetime.datetime(year, month, day, hour, minute)

            snapshot.create_time = ss_time.timestamp()
            snapshot.expire_time = snapshot.create_time + zfs_valid_time
            self.snapshot_list.append(snapshot)
        return self.snapshot_list

    def show_snapshot_list(self):
        snapshot_list = self.get_snapshot_list()
        if not snapshot_list:
            print("%s contains no zfs snapshot \n" % self.zfs_vol)
            return
        for ss in snapshot_list:
            print(ss)

    def delete_expire_snapshot(self):
        snapshot_list = self.get_snapshot_list()

        for ss in snapshot_list:
            now = datetime.datetime.now()
            if (ss.expire_time <= now.timestamp()):
                # delete this snapshot
                self.remove_snapshot(ss.name)

    def remove_snapshot(self, name):
        assert name
        zfs_cmd = "%s destroy %s@%s" % (zfs_bin, self.zfs_vol, name)

        if os.system(zfs_cmd) == 0:
            log("command succeeded when exec: %s" % zfs_cmd)
        else:
            log("command failed when exec: %s" % zfs_cmd)

        return 0


def main():
    if len(sys.argv) < 3:
        print("ZFS snapshot automation script by hefish@gmail.com\n")
        print("%s usage:  \n" % sys.argv[0])
        print("%s <show|snap> <zfs pool>/<zfs volume> \n" % sys.argv[0])
        sys.exit(0)

    log_init()

    zs = ZfsVolume(sys.argv[2])

    if sys.argv[1] == "show":
        zs.show_snapshot_list()
    elif sys.argv[1] == "snap":
        zs.snapshot()
        zs.delete_expire_snapshot()
    elif sys.argv[1] == "check":
        pass


if __name__ == "__main__":
    main()
