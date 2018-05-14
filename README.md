# ceph_pg_count
对ceph集群pg分布进行统计

本模块没有任何依赖，在任意的ceph client端都可以使用

结果大致如下：
pool      35      36      37      38      39      40      41      42      43      44      45      46      47      48      49      ┆all_sum
-------------------------------------------------------------------------------------------------------------------------------------------
osd.0     7       4       4       6       4       5       4       5       4       5       7       7       6       5       3       ┆76
osd.1     4       7       6       6       4       8       5       4       5       5       7       3       6       5       8       ┆83
osd.2     5       5       6       4       8       3       7       7       7       6       2       6       4       6       5       ┆81
-------------------------------------------------------------------------------------------------------------------------------------------
SUM:      16      16      16      16      16      16      16      16      16      16      16      16      16      16      16
AVE:      5       5       5       5       5       5       5       5       5       5       5       5       5       5       5
-------------------------------------------------------------------------------------------------------------------------------------------
MAX:      7       7       6       6       8       8       7       7       7       6       7       7       6       6       8
osdid     osd.0   osd.1   osd.1   osd.0   osd.2   osd.1   osd.2   osd.2   osd.2   osd.2   osd.0   osd.0   osd.0   osd.2   osd.1
per       140.00% 140.00% 120.00% 120.00% 160.00% 160.00% 140.00% 140.00% 140.00% 120.00% 140.00% 140.00% 120.00% 120.00% 160.00%
-------------------------------------------------------------------------------------------------------------------------------------------
MIN:      4       4       4       4       4       3       4       4       4       5       2       3       4       5       3
osdid     osd.1   osd.0   osd.0   osd.2   osd.0   osd.2   osd.0   osd.1   osd.0   osd.0   osd.2   osd.1   osd.2   osd.0   osd.0
per       80.00%  80.00%  80.00%  80.00%  80.00%  60.00%  80.00%  80.00%  80.00%  100.00% 40.00%  60.00%  80.00%  100.00% 60.00%

