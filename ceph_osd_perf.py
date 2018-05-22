#!/usr/bin/python
# -*- coding:UTF-8 -*-
'''
	Copyright (C) 2018 - All Rights Reserved
	模块名称: ceph_osd_perf.py
	创建日期: 2018/5/15
	代码编写: fanwen
	功能说明:
'''

import commands
import time

def run_cmd(cmd):
    res = commands.getstatusoutput(cmd);
    if(res[0] != 0):
        print "Run [%s] Failed!"%cmd;
        print "Reason: [%s]" %res[1];
    else:
        # print "--------->>Run [%s] Success!"%cmd;
        pass;
    return res;

class cluster:
    def __init__(self):
        self.osd_list = [];
        self.osd_2_host = {};
        self.__get_osd_tree();

    def get_osd_perf(self):
        # self.__get_osd_tree();

        res = run_cmd("ceph osd perf");
        if res[0] <> 0:
            print "get ceph -v failed!";
            return False;
        osd_perf_str = res[1];
        ceph_perf_list = osd_perf_str.split('\n')[1:];
        for line in ceph_perf_list:
            try:
                info = line.split();
                # print info;
                id = eval(info[0]);
                fs_commit_latency = info[1];
                fs_apply_latency = info[2];
                host_name = self.osd_2_host[id];
                self.osd_list.append([info[0], fs_commit_latency, fs_apply_latency, host_name]);
                # print self.osd_list;
            except Exception as e:
                print e;
                continue;

    def __get_osd_tree(self):
        res = run_cmd("ceph osd tree|grep -E 'host [a-zA-Z]+.*[1-9]+' -A 50");
        if res[0] <> 0:
            print "get ceph osd tree failed!";
            return False;
        ceph_osd_str = res[1];

        ceph_osd_list = ceph_osd_str.split('\n')[0:];
        cur_host = None;    # 当前host
        for line in ceph_osd_list:
            try:
                info = line.split();
                id = eval(info[0]);
                if id < 0 :  # host
                    if info[2] == "host":
                        cur_host = info[3];
                    else:
                        cur_host = None;
                    continue;
                else:
                    if cur_host <> None:
                        self.osd_2_host[id] = cur_host;
            except:
                continue;

    def show_ceph_osd_perf(self):
        mat = ["{0[0]:8}","{0[1]:24}","{0[2]:24}","{0[3]:12}"];
        gap_line_width = 24 + 24 + 12 + 8;
        headlinde = ["osd","fs_commit_latency(ms)", "fs_apply_latency(ms)","hostname"];

        all_info = "";
        ss = "".join(mat);
        # print ss.format(headlinde);
        all_info += ss.format(headlinde);
        all_info += "\n";
        gapline = '{:->%d}'%gap_line_width;
        # print gapline.format("---");

        ll = sorted(self.osd_list, key=lambda x:eval(x[2]), reverse = True);
        for l in ll[0:20]:
            # print ss.format(l);
            all_info += ss.format(l);
            all_info += "\n";

        return all_info;
            # print gapline.format("---");

if __name__ == "__main__":
    cs = cluster();
    cs.get_osd_perf();
    print cs.show_ceph_osd_perf();


