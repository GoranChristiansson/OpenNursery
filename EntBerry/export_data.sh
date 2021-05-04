#!/usr/bin/bash
#influx  -database home -format csv -execute "select time,value from \"entomatic_3\" where channel='ch123'" > outtest.csv
#influx  -database home -format csv -execute "select time,value from \"entomatic_3\" where channel='ch123'" > outtest.csv
influx  -database home -format csv -execute "select * from entomatic_3 " > outtest.csv
