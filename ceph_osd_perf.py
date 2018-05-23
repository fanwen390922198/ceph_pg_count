#!/usr/bin/python
# -*- coding:UTF-8 -*-
'''
	Copyright (C) 2018 - All Rights Reserved
	模块名称: ceph_osd_perf.py
	创建日期: 2018/5/15
	代码编写: fanwen
	功能说明:
	    本程序会动态的，间隔性的将osd perf打印到屏幕，并写到日志文件中
'''

import commands
import time
import sys
import getopt
import curses

__RUN_TIME__ = 30    # 默认运行200s
__SHOW_LINES__ = 20   # 默认显示20行, 一屏幕究竟能打印多少条数据，跟分辨率，字体大小有关，其实也可以用scroll刷出滚动条来解决，
					  # 但个人觉得没必要，若屏幕能多打印数据，请自行调整数量，或者自己增加代码刷滚动条。
__FRESH_GAP__ = 3;    # 刷新频率
__LOG__ = './ceph_osd_perf.log'   # 日志文件


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
        self.osd_perf_list = [];
        self.osd_2_host = {};
        self.__get_osd_tree();

    def get_osd_perf(self):
        self.osd_perf_list = [];
        res = run_cmd("ceph osd perf");
        if res[0] <> 0:
            print "get ceph -v failed!";
            return False;
        osd_perf_str = res[1];
        ceph_perf_list = osd_perf_str.split('\n')[1:];
        for line in ceph_perf_list:
            try:
                info = line.split();
                id = eval(info[0]);
                fs_commit_latency = info[1];
                fs_apply_latency = info[2];
                host_name = self.osd_2_host[id];
                self.osd_perf_list.append([info[0], fs_commit_latency, fs_apply_latency, host_name]);
            except Exception as e:
                print e;
                continue;

    def __get_osd_tree(self):
        res = run_cmd("ceph osd tree|grep -E 'host [a-zA-Z]+.*[1-9]+' -A 50");
        if res[0] <> 0:
            print "get ceph osd tree failed!";
            return False;
        ceph_osd_str = res[1];

        ceph_osd_perf_list = ceph_osd_str.split('\n')[0:];
        cur_host = None;    # 当前host
        for line in ceph_osd_perf_list:
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
        # gap_line_width = 24 + 24 + 12 + 8;
        headlinde = ["osd","fs_commit_latency(ms)", "fs_apply_latency(ms)","host_name"];

        all_info = [];
        ss = "".join(mat);
        all_info.append(ss.format(headlinde));

        # gapline = '{:->%d}'%gap_line_width;
        # print gapline.format("---");

        ll = sorted(self.osd_perf_list, key = lambda x:eval(x[2]), reverse = True);
        for l in ll[0:__SHOW_LINES__]:
            all_info.append(ss.format(l));

        return all_info;
            # print gapline.format("---");

def close_curse(c):
	c.keypad(0);
	curses.echo();
	curses.endwin();

			
if __name__ == "__main__":
    run_time = __RUN_TIME__;
    show_line = __SHOW_LINES__;

    opts, args = getopt.getopt(sys.argv[1:], "T:S:", []);
    for opt in opts:
        if opt[0] == '-T':
            run_time = eval(opt[1]) if len(opt[1]) > 0  else __RUN_TIME__;
        elif opt[0] == '-S':
            show_line = eval(opt[1]) if len(opt[1]) > 0  else __SHOW_LINES__;

    cs = cluster();
    try:
        stdscr = curses.initscr();
        # curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.noecho();
    except Exception as e:
        print str(e);
        exit(-1);

    try:
        fh = open(__LOG__, 'a+');
    except Exception as e:
        print str(e);
		close_curse(stdscr);
        exit(-1);

    #-- err info
    err = "";

    try:
        while(run_time > 0):
            cs.get_osd_perf();

            stdscr.clear();
            stdscr.addstr(0, 0, "---->[ceph osd perf] will run %d sec, show top %d latency."%(run_time, show_line));
            fh.write("-------------------------------------------------------------------------------------------\n");
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n');

            line = 1;
            all_info = cs.show_ceph_osd_perf();
            for info in all_info:
                stdscr.addstr(line, 0, info);
                fh.write(info + '\n');
                line += 1;

            stdscr.refresh();
            time.sleep(__FRESH_GAP__);
            run_time -= __FRESH_GAP__;
    except Exception as e:
        err = str(e);
    finally:
        fh.close();
		close_curse(stdscr);
		
    # print last res
    if len(err) == 0:
        for info in all_info:
            print info;
    else:
        print err;
