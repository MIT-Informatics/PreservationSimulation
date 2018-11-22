# howlong.awk
#               RBL 20181121
# Parse out total time from family/specific/act/*_case.log files.

BEGIN           {lowtime = 999999999999; hightime = 0}
/^[0-9]{8}_/    {if (ENVIRON["DEBUG"]) print; 
                sub("[0-9]{8}_","",$1)
                hr = substr($1, 1, 2)
                min = substr($1, 3, 2)
                sec = substr($1, 5, 2)
                msec = substr($1, 8, 3)
                timmsec = (((((hr*60)+min)*60)+sec)*1000)+msec
                if (ENVIRON["DEBUG"]) print $1, hr, min, sec, msec, timmsec
                if (timmsec < lowtime) lowtime = timmsec
                if (timmsec > hightime) hightime = timmsec
                }
END             {if (ENVIRON["DEBUG"]) print lowtime, hightime
                diftime = hightime - lowtime
                if (ENVIRON["DEBUG"]) printf("%s", "======")
                printf("%9.3f %s\n", diftime/1000, FILENAME)
                }


#END             