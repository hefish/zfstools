#!/usr/bin/env python3

import sys
import getopt
import Mail
import subprocess
import socket


config = {
    'smtp_host' : "smtp.qq.com",
    'smtp_user' : "czlibit@foxmail.com",
    'smtp_pass' : "dngcjckjeylmdfbi",
    'from_email' : "czlibit@foxmail.com",
    'to_email' : ['hefish@qq.com', "hefish@gmail.com"],
    'ip_cmd' : "/usr/sbin/ip",
    'zpool_cmd' : "/usr/sbin/zpool"

}


class ZCheckStat :
    def __init__(self):
        pass

    def usage(self):
        print("ZFS health check tool ")
        print("-----------------------------------------------")
        print("%s -h <pool> " % (sys.argv[0]))
        print("     -h   this message ")
        print("     <pool>   zfs pool name")
        exit(0)

    def check(self, pool):
        print("checking "+ pool)
        cmd = [config['zpool_cmd'], "status", pool]
        output = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT).decode("UTF-8")
        return output

    def notify(self, subject, msg):
        email = Mail.SMTP(config)
        email.subject(subject)
        email.content(msg)
        email.send()

    def parse_output(self, content):
        lines = content.split("\n")
        for l in lines:
            try:
                (k, w) = l.split(": ")
                k = k.strip()
                w = w.strip()
                if k == "state":
                    if w != "ONLINE":
                        return -1
                    else:
                        return 0
            except ValueError as e:
                continue
        return -1

    def get_ip_address(self):
        cmd = [config['ip_cmd'], "addr"]
        output = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT).decode("UTF-8")
        return output
            
            





if __name__ == '__main__':
    o = ZCheckStat()
    if len(sys.argv) < 2:
        o.usage()

    pool = sys.argv[1]
    out = o.check(pool)
    if o.parse_output(out) < 0:
        hostname = socket.gethostname()
        ipaddr = o.get_ip_address()
        o.notify(hostname + " 提醒邮件 zpool: "+pool , out + ipaddr)