# Get the data into the right form for these plots.
alldat <- fndfGetGiantDataRaw("")
newdat <- alldat %>%
group_by(copies, lifem, auditfrequency, audittype, auditsegments
        , glitchfreq, glitchimpact) %>%
summarize(mdmlosspct=round(midmean(lost/docstotal)*100.0, 2), n=n()) %>%
filter(copies==5)

