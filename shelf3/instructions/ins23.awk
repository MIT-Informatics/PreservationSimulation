# ins23.awk
# Translate .ins file to .ins3 file, as far as possible.

/^$/                {print}
/^#[0-9]/           {printf("%s,%s,0\n", $1, substr($1,2)); next}
/^#[A-Z]/           {printf("%s,\"%s\",0\n", $1, substr($1,2)); next}
/^\s*#/             {print}
/^[a-z][A-Za-z]+/   {print; print FILENAME; print "value,label,selected"}
/^[0-9]/            {printf("%s,%s,0\n", $1, $1)}
/^[A-Z]/            {printf("%s,\"%s\",0\n", $1, $1)}
