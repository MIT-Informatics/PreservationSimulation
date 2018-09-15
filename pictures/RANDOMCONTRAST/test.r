alldat <- fndfGetGiantDataRaw("")

newdat <- alldat %>%
group_by(copies, lifem, auditfrequency, audittype, auditsegments) %>%
summarize(losspct=round(midmean(lost/docstotal)*100.0, 2), n=n())


