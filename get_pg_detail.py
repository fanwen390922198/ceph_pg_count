#!/usr/bin/python
# -*- coding:UTF-8 -*-
'''
	Copyright (C) 2018 - All Rights Reserved
	模块名称: get_pg_detail.py
	创建日期: 2018/5/11
	代码编写: fanwen
	功能说明:
'''

import commands

def run_cmd(cmd):
    res = commands.getstatusoutput(cmd);
    if(res[0] != 0):
        print "Run [%s] Failed!"%cmd;
        print "Reason: [%s]" %res[1];
    else:
        print "--------->>Run [%s] Success!"%cmd;

    return res;

class osd:
    def __init__(self, id):
        self.id = id;
        self.pgs = 0;
        self.primary_pgs = 0;
        self.pool_osd_pgs = {};

    def add_pg(self, pool_id, primary = True):
        self.pgs += 1;

        if primary:
            self.primary_pgs += 1;

        if self.pool_osd_pgs.has_key(pool_id):
            self.pool_osd_pgs[pool_id] += 1;
        else:
            self.pool_osd_pgs[pool_id] = 1;

class cluster:
    def __init__(self):
        self.osd_list = [];
        self.pool_list = [];
        self.osdid_2_pgs = {};
        self.pool_pgs = {};
        self.pgid_2_pgnam = {};

    def get_ceph_pg(self):
        # self.__get_pool_detail();

        res = run_cmd("ceph pg dump pgs_brief");
        if res[0] <> 0:
            print "get pg dump failed!";
            return False;
        pg_dump_str = res[1];

        # f = open('./pgs.txt', 'r+');
        # pg_dump_str = f.read();
        # f.close();
        pg_state_list = pg_dump_str.split('\n')[1:];
        for line in pg_state_list:
            try:
                info = line.split();
                pg_nam = info[0];
                pg_2_osds = eval(info[2]);
                self.add_pg(pg_nam, pg_2_osds);
            except:
                continue;

    def add_pg(self, pg_nam, pg_to_osds):
        pool_id = int(pg_nam.split('.')[0]);
        for i in range(0, len(pg_to_osds)):
            #-- 统计osd
            if not self.osdid_2_pgs.has_key(pg_to_osds[i]):
                self.osdid_2_pgs[pg_to_osds[i]] = osd(pg_to_osds[i]);
                self.osd_list.append(pg_to_osds[i]);

            primary = True if i == 0 else False;

            self.osdid_2_pgs[pg_to_osds[i]].add_pg(pool_id, primary);

        #-- 统计pool
        if not self.pool_pgs.has_key(pool_id):
            self.pool_pgs[pool_id] = 0;
            self.pool_list.append(pool_id);

        self.pool_pgs[pool_id] += 1;


    def __get_pool_detail(self):
        res = run_cmd("ceph osd pool ls detail");
        if res[0] <> 0:
            print "get osd pool failed!";
            return False;
        _ss = res[1];
        pools_detail_list = _ss.split('\n')[0:];
        for line in pools_detail_list:
            try:
                info = line.split();
                pg_id = info[1];
                pg_nam = info[2];
                self.pgid_2_pgnam[pg_id] = pg_nam;
            except:
                continue;

    def show_pgs(self):
        osd_pg_sum = [];
        i = 0;
        mat = ["{0[0]:10}"];
        headlinde = ["pool"];
        for pool_id in sorted(self.pool_list):
            headlinde.append(str(pool_id));
            # headlinde.append(str(self.pgid_2_pgnam[pool_id]));
            i += 1;
            mat.append("{0[%d]:8}"%i);

        i += 1;
        mat.append("{0[%d]:1}" % i);

        i += 1;
        mat.append("{0[%d]:8}"%i);
        headlinde.extend(["┆","all_sum"]);

        ss = "".join(mat);
        print ss.format(headlinde);

        gap_line_width = 10 +  (len(mat)-2)*8 + 1;
        gapline = '{:->%d}'%gap_line_width;

        print gapline.format("---");

        #-- 遍历osd信息
        for osd in sorted(self.osd_list):
            rec = [];
            rec2 = []; # 单个osd统计信息
            osd_obj = self.osdid_2_pgs[osd];

            osd_nam = "osd.%d"%osd;         # osd name
            rec2.append(osd_nam);

            #-- 统计每个osd所属于的pool的pg数量
            for pool_id in sorted(self.pool_list):
                if osd_obj.pool_osd_pgs.has_key(pool_id):
                    rec2.append("%d"%osd_obj.pool_osd_pgs[pool_id]);
                    rec.append(osd_obj.pool_osd_pgs[pool_id]);
                else:
                    rec2.append("0");
                    rec.append(0);

            rec2.append("┆");
            rec2.append(str(sum(rec)));
            print ss.format(rec2);

            osd_pg_sum.append(rec);

        print gapline.format("-");

        # -- SUM line
        sum_line = ["SUM:"];
        for i in range(0, len(self.pool_list)):
            sum_line.append("%d"%(sum([ll[i] for ll in osd_pg_sum])));
        sum_line.extend(["",""]);
        print ss.format(sum_line);

       # -- AVE line
        ave_line = ["AVE:"];
        max_line = ["MAX:"];
        max_osd_line = ["osdid"];
        max_per_line = ["per"];
        min_line = ["MIN:"];
        min_osd_line = ["osdid"];
        min_per_line = ["per"];

        for i in range(0, len(self.pool_list)):
            pool_2_osd_pgs = [ll[i] for ll in osd_pg_sum];
            ave_pgs = sum(pool_2_osd_pgs) / len(self.osd_list);
            ave_line.append(str(ave_pgs));

            osd_list = sorted(self.osd_list);
            max_pgs = max(pool_2_osd_pgs);
            max_line.append(str(max_pgs));
            index = pool_2_osd_pgs.index(max_pgs);
            max_pgs_osd = osd_list[index];
            max_osd_line.append("osd.%d"%max_pgs_osd);
            if ave_pgs <> 0:
                max_per_line.append("%.2f%%"%(float(max_pgs)/float(ave_pgs)*100));
            else:
                max_per_line.append("0");

            if ave_pgs <> 0:
                min_pgs = min(pool_2_osd_pgs);
                min_line.append(str(min_pgs));
                index = pool_2_osd_pgs.index(min_pgs);
                min_pgs_osd = osd_list[index];
                min_osd_line.append("osd.%d"%min_pgs_osd);
                if ave_pgs <> 0:
                    min_per_line.append("%.2f%%" % (float(min_pgs) / float(ave_pgs) * 100));
                else:
                    min_per_line.append("0");
            else:
                min_line.append("0");
                min_osd_line.append("");
                min_per_line.append("0");

        ave_line.extend(["",""]);
        max_line.extend(["",""]);
        max_osd_line.extend(["",""]);
        max_per_line.extend(["",""]);
        min_line.extend(["",""]);
        min_osd_line.extend(["",""]);
        min_per_line.extend(["",""]);

        print ss.format(ave_line);
        print gapline.format("---");
        print ss.format(max_line);
        print ss.format(max_osd_line);
        print ss.format(max_per_line);
        print gapline.format("---");
        print ss.format(min_line);
        print ss.format(min_osd_line);
        print ss.format(min_per_line);



if __name__ == "__main__":
    cs = cluster();
    cs.get_ceph_pg();
    cs.show_pgs();


