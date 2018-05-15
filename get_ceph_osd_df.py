#!/usr/bin/python
# -*- coding:UTF-8 -*-
'''
	Copyright (C) 2018 - All Rights Reserved
	模块名称: get_ceph_osd_df.py
	创建日期: 2018/5/15
	代码编写: fanwen
	功能说明:
	        获取ceph集群osd对应的磁盘空间使用情况
'''

import commands

def run_cmd(cmd):
    res = commands.getstatusoutput(cmd);
    if(res[0] != 0):
        print "Run [%s] Failed!"%cmd;
        print "Reason: [%s]" %res[1];
    else:
        # print "--------->>Run [%s] Success!"%cmd;
        pass;
    return res;


class osd:
    def __init__(self, id, weight, size, used, per_use, hostname, pgs = 0):
        self.id = id;
        self.weight = weight;
        self.size = size;
        self.used = used;
        self.per_use = per_use;
        self.host_name = hostname;
        self.pgs = pgs;

class host:
    def __init__(self, host_name, id, weight, size, used, per_use):
        self.host_name = host_name;
        self.id = id;
        self.weight = weight;
        self.size = size;
        self.used = used;
        self.per_use = per_use;
        self.osd_list = [];


    def add_osd(self, osd):
        self.osd_list.append(osd);

class cluster:
    def __init__(self):
        self.osd_list = [];
        self.host = {};

    def get_ceph_osd_df(self):
        res = run_cmd("ceph osd df tree|grep -E 'host [a-zA-Z]+.*[1-9]+\s' -A 50");
        if res[0] <> 0:
            print "get ceph osd df tree failed!";
            return False;
        ceph_df_str = res[1];

        # f = open('./ceph_df2.txt', 'r+');
        # ceph_df_str = f.read();
        # f.close();
        ceph_df_list = ceph_df_str.split('\n')[0:];
        cur_host = None;    # 当前host
        for line in ceph_df_list:
            try:
                info = line.split();
                id = eval(info[0]);
                name = info[-1];
                weight = info[1];
                size = info[3];
                used = info[4];
                per_use = info[6];
                if id < 0 :  # host
                    if info[-2] == "host":
                        cur_host = host(name, id, weight, size, used, per_use);
                        self.host[name] = cur_host;
                    else:
                        cur_host = None;
                    continue;
                else:
                    if cur_host <> None:
                        _osd = osd(id, weight, size, used, per_use, cur_host.host_name);
                        self.host[cur_host.host_name].add_osd(_osd);
                        self.osd_list.append([name, weight, size, used, per_use, cur_host.host_name]);

            except:
                continue;


    def __get_ceph_version(self):
        res = run_cmd("ceph -v");
        if res[0] <> 0:
            print "get ceph -v failed!";
            return False;
        _ss = res[1];

    def show_ceph_df(self):
        mat = ["{0[0]:10}","{0[1]:10}","{0[2]:10}","{0[3]:10}","{0[4]:13}","{0[5]:10}"];
        headlinde = ["OSD","WEIGHT", "SIZE","USED","PERUSED(%)","HOST"];
        ss = "".join(mat);
        print ss.format(headlinde);
        gap_line_width = len(headlinde)*10 + 3;
        gapline = '{:->%d}'%gap_line_width;
        print gapline.format("---");

        ll = sorted(self.osd_list, key=lambda x:eval(x[4]), reverse = True);
        for l in ll:
            print ss.format(l);
            print gapline.format("---");



if __name__ == "__main__":
    cs = cluster();
    cs.get_ceph_osd_df();
    cs.show_ceph_df();


