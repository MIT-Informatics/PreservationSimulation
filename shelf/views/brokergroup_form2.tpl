<!-- brokergroup_form_insert.j2 file -->
<!-- brokergroup_form_base.j2 -->
<!-- THIS .tpl FORM IS AUTOMATICALLY GENERATED.  DO NOT EDIT. -->
<html>
    <!-- brokergroup_form_base.tpl - template for bottle to present options
        for a broker.py run of hundreds or thousands of individual simulation
        runs using PreservationSimulation/shelf/main.py -->
<head>
    <title>Broker Form</title>
</head>
<body>

<style type="text/css">
    input.largerCheckbox
    {
        width: 18px;
        height: 18px;
    }
</style>

<form action="mainsim" method="post">
    <font size="+1">
        <title>PreservationSimulation broker.py batch run</title>
        <h1>MIT Library Preservation Simulation Project</h1>
        <p><h3>Choose options for a <em>batch of</em> simulation runs</h3></p>
        
        <table border="0" width="50%">
            <tr><td>
                <p>WARNING: this interface is used to choose sets of simulation runs, 
            usually numbering in the hundreds or thousands.  The set of runs 
            is selected as a subset from a very large pile of possible instructions.  
            Be very careful to ask for exactly what you want.  
                <strong>Use the TEST button to see exactly 
                how many cases will be chosen with your parameter choices.
                </strong>
                </p>
                <p>For many options, multiple choices are permitted.  Be careful
                    when selecting multiple choices: the combinations can 
                    generate a very large number of cases.
                </p><br/>
            </td></tr>
            <p></p>
        </table>


    <table cellpadding=6 cellspacing="0" border="0" width="97%">

<!--  c o m m o n   o p t i o n s  -->    
    <tr bgcolor="#ffffbb">
        <td colspan="4">
        <b>Common options</b>
        </td>
    </tr>

<!--  d i r e c t o r i e s ,  d a t a b a s e   n a m e  -->    
    <tr bgcolor="#ffffbb">
               <td>
        <table>
            <tr><td>
                <b>Family Directory
                    <font color="red">* required</font></b>
            </td></tr>
            <tr><td>
                <input type="text" name=sFamilyDir size="15" value=""
                >
            </td></tr>
        </table>
    </td>

               <td>
        <table>
            <tr><td>
                <b>Specific Directory
                    <font color="red">* required</font></b>
            </td></tr>
            <tr><td>
                <input type="text" name=sSpecificDir size="15" value=""
                >
            </td></tr>
        </table>
    </td>

        <td>
            <font size="+2">
                <a href="setup">
                    <b>&nbsp;&nbsp;Go to setup page</b>
                </a>
            </font>
        </td>

               <td>
        <table>
            <tr><td>
                <b>Number of Replications with Random Seeds
                    </b>
            </td></tr>
            <tr><td>
                <input type="text" name=nRandomSeeds size="5" value="21"
                >
            </td></tr>
        </table>
    </td>

    </tr>

<!--  c o p i e s ,   s e c t o r   l i f e  -->
    <tr bgcolor="#ffffbb" colspan="4">
               
    <td>
        <table>
            <tr><th align="left">
                <b>Number of Copies of Documents                    </b>
            </th></tr>
            <tr><td>
                <select name="nCopies" multiple size="6">
                    <option value="1">&nbsp;&nbsp;1&nbsp;</option>
                    <option value="2">&nbsp;&nbsp;2&nbsp;</option>
                    <option value="3" selected>&nbsp;&nbsp;3&nbsp;</option>
                    <option value="4" selected>&nbsp;&nbsp;4&nbsp;</option>
                    <option value="5" selected>&nbsp;&nbsp;5&nbsp;</option>
                    <option value="6">&nbsp;&nbsp;6&nbsp;</option>
                    <option value="7">&nbsp;&nbsp;7&nbsp;</option>
                    <option value="8">&nbsp;&nbsp;8&nbsp;</option>
                    <option value="9">&nbsp;&nbsp;9&nbsp;</option>
                    <option value="10">&nbsp;&nbsp;10&nbsp;</option>
                    <option value="14">&nbsp;&nbsp;14&nbsp;</option>
                    <option value="16">&nbsp;&nbsp;16&nbsp;</option>
                    <option value="20">&nbsp;&nbsp;20&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

                
    <td>
        <table>
            <tr><th align="left">
                <b>Number of Documents in Collection                    </b>
            </th></tr>
            <tr><td>
                <select name="nDocuments">
                    <option value="10">&nbsp;&nbsp;10 (for SHOCKs)&nbsp;</option>
                    <option value="10000" selected>&nbsp;&nbsp;10,000 (baseline)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

               
    <td>
        <table>
            <tr><th align="left">
                <b>Half-life of Storage Logical Blocks (megahours)                    </b>
            </th></tr>
            <tr><td>
                <select name="nLifem" multiple size="6">
                    <option value="1">&nbsp;&nbsp;1&nbsp;</option>
                    <option value="2" selected>&nbsp;&nbsp;2&nbsp;</option>
                    <option value="3" selected>&nbsp;&nbsp;3&nbsp;</option>
                    <option value="5" selected>&nbsp;&nbsp;5&nbsp;</option>
                    <option value="10" selected>&nbsp;&nbsp;10&nbsp;</option>
                    <option value="20" selected>&nbsp;&nbsp;20&nbsp;</option>
                    <option value="30" selected>&nbsp;&nbsp;30&nbsp;</option>
                    <option value="50" selected>&nbsp;&nbsp;50&nbsp;</option>
                    <option value="100" selected>&nbsp;&nbsp;100&nbsp;</option>
                    <option value="200" selected>&nbsp;&nbsp;200&nbsp;</option>
                    <option value="300" selected>&nbsp;&nbsp;300&nbsp;</option>
                    <option value="500" selected>&nbsp;&nbsp;500&nbsp;</option>
                    <option value="1000" selected>&nbsp;&nbsp;1000&nbsp;</option>
                    <option value="2000">&nbsp;&nbsp;2000&nbsp;</option>
                    <option value="3000">&nbsp;&nbsp;3000&nbsp;</option>
                    <option value="5000">&nbsp;&nbsp;5000&nbsp;</option>
                    <option value="10000">&nbsp;&nbsp;10000&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

        <td>&nbsp;</td>        <!-- blank separator -->
    </tr>
 
 <!--  a u d i t i n g  -->   
    <tr bgcolor="#ccffbb">
        <td colspan="4">
        <b>Auditing of collection</b>
        </td>
    </tr>
    
    <tr bgcolor="#ccffbb">
                
    <td>
        <table>
            <tr><th align="left">
                <b>Frequency of Scheduled Audit Cycles (hrs) (0=never)                    </b>
            </th></tr>
            <tr><td>
                <select name="nAuditFreq">
                    <option value="0">&nbsp;&nbsp;0 (never)&nbsp;</option>
                    <option value="1000">&nbsp;&nbsp;1000 (month)&nbsp;</option>
                    <option value="2500">&nbsp;&nbsp;2500 (quarter)&nbsp;</option>
                    <option value="5000">&nbsp;&nbsp;5000 (1/2 year)&nbsp;</option>
                    <option value="10000" selected>&nbsp;&nbsp;10000 (year)&nbsp;</option>
                    <option value="20000">&nbsp;&nbsp;20000 (two years)&nbsp;</option>
                    <option value="50000">&nbsp;&nbsp;50000 (five years)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

                
    <td>
        <table>
            <tr><th align="left">
                <b>Number of Audit Segments per Cycle (assuming annual)                    </b>
            </th></tr>
            <tr><td>
                <select name="nAuditSegments">
                    <option value="1" selected>&nbsp;&nbsp;1 (annual)&nbsp;</option>
                    <option value="2">&nbsp;&nbsp;2 (semi-annual)&nbsp;</option>
                    <option value="4">&nbsp;&nbsp;4 (quarter)&nbsp;</option>
                    <option value="5">&nbsp;&nbsp;5 (1/5 of five year cycle)&nbsp;</option>
                    <option value="10">&nbsp;&nbsp;10 (month)&nbsp;</option>
                    <option value="50">&nbsp;&nbsp;50 (week)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

                
    <td>
        <table>
            <tr><th align="left">
                <b>Auditing Strategy                    </b>
            </th></tr>
            <tr><td>
                <select name="sAuditType">
                    <option value="TOTAL" selected>&nbsp;&nbsp;TOTAL (every doc every cycle)&nbsp;</option>
                    <option value="SYSTEMATIC">&nbsp;&nbsp;SYSTEMATIC (doc subset each segment)&nbsp;</option>
                    <option value="UNIFORM">&nbsp;&nbsp;RANDOM (uniform random subset each segment)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

        <td>&nbsp;</td>
    </tr>

<!--  s h o c k s  -->
    <tr bgcolor="#ffaaaa">
        <td colspan="5">
            <b>Economic shocks that may affect multiple servers</b> 
            <br/>(May be used to decrease life expectancy or 
            kill multiple servers at once.)
        </td>
    </tr>

    <tr bgcolor="#ffaaaa">
               
    <td>
        <table>
            <tr><th align="left">
                <b>Frequency Half-life of Economic Shocks (hrs) (0=never)                    </b>
            </th></tr>
            <tr><td>
                <select name="nShockFreq" multiple size="6">
                    <option value="0" selected>&nbsp;&nbsp;0 (never)&nbsp;</option>
                    <option value="10000">&nbsp;&nbsp;10000 (1 year)&nbsp;</option>
                    <option value="20000">&nbsp;&nbsp;20000 (2 years)&nbsp;</option>
                    <option value="30000">&nbsp;&nbsp;30000 (3 years)&nbsp;</option>
                    <option value="50000">&nbsp;&nbsp;50000 (5 years)&nbsp;</option>
                    <option value="100000">&nbsp;&nbsp;100000 (10 years)&nbsp;</option>
                    <option value="200000">&nbsp;&nbsp;200000 (20 years)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

               
    <td>
        <table>
            <tr><th align="left">
                <b>Shock Impact, Reduction in Server Expected Lifetime (pct)                    </b>
            </th></tr>
            <tr><td>
                <select name="nShockImpact" multiple size="6">
                    <option value="10">&nbsp;&nbsp;10&nbsp;</option>
                    <option value="20">&nbsp;&nbsp;20&nbsp;</option>
                    <option value="33">&nbsp;&nbsp;33&nbsp;</option>
                    <option value="50" selected>&nbsp;&nbsp;50 (2x error rate)&nbsp;</option>
                    <option value="67">&nbsp;&nbsp;67 (3x error rate)&nbsp;</option>
                    <option value="75">&nbsp;&nbsp;75 (4x error rate)&nbsp;</option>
                    <option value="80">&nbsp;&nbsp;80 (5x error rate)&nbsp;</option>
                    <option value="90">&nbsp;&nbsp;90 (10x error rate)&nbsp;</option>
                    <option value="100">&nbsp;&nbsp;100 (fatal)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

               
    <td>
        <table>
            <tr><th align="left">
                <b>Shock Duration (hrs) (0=infinite)                    </b>
            </th></tr>
            <tr><td>
                <select name="nShockMaxlife" multiple size="6">
                    <option value="0">&nbsp;&nbsp;0 (forever)&nbsp;</option>
                    <option value="5000">&nbsp;&nbsp;5000 (1/2 year)&nbsp;</option>
                    <option value="10000" selected>&nbsp;&nbsp;10000 (1 year)&nbsp;</option>
                    <option value="20000">&nbsp;&nbsp;20000 (2 years)&nbsp;</option>
                    <option value="30000">&nbsp;&nbsp;30000 (3 years)&nbsp;</option>
                    <option value="50000">&nbsp;&nbsp;50000 (5 years)&nbsp;</option>
                    <option value="100000">&nbsp;&nbsp;100000 (10 years)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

               
    <td>
        <table>
            <tr><th align="left">
                <b>How Many Servers Affected by Shock?                    </b>
            </th></tr>
            <tr><td>
                <select name="nShockSpan" multiple size="6">
                    <option value="1" selected>&nbsp;&nbsp;1&nbsp;</option>
                    <option value="2">&nbsp;&nbsp;2&nbsp;</option>
                    <option value="3">&nbsp;&nbsp;3&nbsp;</option>
                    <option value="4">&nbsp;&nbsp;4&nbsp;</option>
                    <option value="5">&nbsp;&nbsp;5&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

               
    <td>
        <table>
            <tr><th align="left">
                <b>Expected Half-life of Servers (hrs) (0=infinite), must be nonzero for shocks                    <font color="red">* required</font></b>
            </th></tr>
            <tr><td>
                <select name="nServerDefaultLife" multiple size="6">
                    <option value="0" selected>&nbsp;&nbsp;0 (infinite)&nbsp;</option>
                    <option value="10000">&nbsp;&nbsp;10000 (1 year)&nbsp;</option>
                    <option value="20000">&nbsp;&nbsp;20000 (2 years)&nbsp;</option>
                    <option value="30000">&nbsp;&nbsp;30000 (3 years)&nbsp;</option>
                    <option value="40000">&nbsp;&nbsp;40000 (4 years)&nbsp;</option>
                    <option value="50000">&nbsp;&nbsp;50000 (5 years)&nbsp;</option>
                    <option value="80000">&nbsp;&nbsp;80000 (8 years)&nbsp;</option>
                    <option value="100000">&nbsp;&nbsp;100000 (10 years)&nbsp;</option>
                    <option value="200000">&nbsp;&nbsp;200000 (20 years)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

    </tr>

    <tr bgcolor="#ffaaaa">
        <td>&nbsp;</td><td>&nbsp;</td>
        <td>&nbsp;</td><td>&nbsp;</td>
        <td>&nbsp;</td>
    </tr>

<!--  g l i t c h e s  -->    
    <tr bgcolor="#ffaaaa">
        <td colspan="5">
            <b>Glitches in operations, e.g, HVAC failures</b>
            <br/>(May be used increase logical block error rate 
            on multiple servers at once.)
        </td>
    </tr>
    
    <tr bgcolor="#ffaaaa">
                
    <td>
        <table>
            <tr><th align="left">
                <b>Frequency Half-life of Glitches (hrs) (0=never)                    </b>
            </th></tr>
            <tr><td>
                <select name="nGlitchFreq" multiple size="6">
                    <option value="0" selected>&nbsp;&nbsp;0 (never)&nbsp;</option>
                    <option value="1000">&nbsp;&nbsp;1000 (month)&nbsp;</option>
                    <option value="2500">&nbsp;&nbsp;2500 (quarter)&nbsp;</option>
                    <option value="3333">&nbsp;&nbsp;3333 (1/3 year)&nbsp;</option>
                    <option value="10000">&nbsp;&nbsp;10000 (year)&nbsp;</option>
                    <option value="20000">&nbsp;&nbsp;20000 (2 years)&nbsp;</option>
                    <option value="30000">&nbsp;&nbsp;30000 (3 years)&nbsp;</option>
                    <option value="50000">&nbsp;&nbsp;50000 (5 years)&nbsp;</option>
                    <option value="100000">&nbsp;&nbsp;100000 (10 years)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

                
    <td>
        <table>
            <tr><th align="left">
                <b>Glitch Impact, Reduction in Logical Block Lifetime (pct)                    </b>
            </th></tr>
            <tr><td>
                <select name="nGlitchImpact" multiple size="6">
                    <option value="10">&nbsp;&nbsp;10&nbsp;</option>
                    <option value="33" selected>&nbsp;&nbsp;33 (1.5x error rate)&nbsp;</option>
                    <option value="50">&nbsp;&nbsp;50 (2x error rate)&nbsp;</option>
                    <option value="67">&nbsp;&nbsp;67 (3x error rate)&nbsp;</option>
                    <option value="75">&nbsp;&nbsp;75 (4x error rate)&nbsp;</option>
                    <option value="80">&nbsp;&nbsp;80 (5x error rate)&nbsp;</option>
                    <option value="90">&nbsp;&nbsp;90 (10x error rate)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

                
    <td>
        <table>
            <tr><th align="left">
                <b>Duration of Glitch (hrs) (0=infinite)                    </b>
            </th></tr>
            <tr><td>
                <select name="nGlitchMaxlife" multiple size="6">
                    <option value="0">&nbsp;&nbsp;0 (forever)&nbsp;</option>
                    <option value="250">&nbsp;&nbsp;250 (week)&nbsp;</option>
                    <option value="1000" selected>&nbsp;&nbsp;1000 (month)&nbsp;</option>
                    <option value="5000">&nbsp;&nbsp;5000 (1/2 year)&nbsp;</option>
                    <option value="10000">&nbsp;&nbsp;10000 (2 years)&nbsp;</option>
                    <option value="30000">&nbsp;&nbsp;30000 (3 years)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

                
    <td>
        <table>
            <tr><th align="left">
                <b>How Many Servers Affected by Glitch?                    </b>
            </th></tr>
            <tr><td>
                <select name="nGlitchSpan">
                    <option value="1">&nbsp;&nbsp;1&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

                
    <td>
        <table>
            <tr><th align="left">
                <b>Decay Half-life of Glitch Impact (hrs) (0=infinite)                    </b>
            </th></tr>
            <tr><td>
                <select name="nGlitchDecay">
                    <option value="0" selected>&nbsp;&nbsp;0 (no decay)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

    </tr>

<!--  l o g g i n g  -->
    <tr bgcolor="#cccccc">
        <td colspan="1">
            <b>Logging: level of detail, and other general parameters.</b>
        </td>
        <td colspan="5">
        <b>Other General Parameters</b>
        <br/><em>General Parameters.  Slightly dangerous.  One probably should 
            not mess with these, except Short Log, unless one is really
            sure and moderately adventurous.  </em>

        </td>
    </tr>

    <tr bgcolor="#cccccc">
        <td>
            <b>Short Log:</b> <br/>
            (includes only params and stats, 
             no details of sector errors, audits, repairs)<br/> 
             <font size="+1">You want this turned on 
            for production runs.</font> <br/>
            <input type="checkbox" name="bShortLog" value="true" checked class="largerCheckbox" >
        </td>

<!--  g e n e r a l  -->
               
    <td>
        <table>
            <tr><th align="left">
                <b>Length of Simulation (hrs)                    </b>
            </th></tr>
            <tr><td>
                <select name="nSimLength" multiple size="6">
                    <option value="0" selected>&nbsp;&nbsp;0 (default)&nbsp;</option>
                    <option value="100000">&nbsp;&nbsp;100000 (10 years)&nbsp;</option>
                    <option value="200000">&nbsp;&nbsp;200000 (20 years)&nbsp;</option>
                    <option value="300000">&nbsp;&nbsp;300000 (30 years)&nbsp;</option>
                    <option value="500000">&nbsp;&nbsp;500000 (50 years)&nbsp;</option>
                    <option value="1000000">&nbsp;&nbsp;1000000 (100 years)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

<!--
        <td>
            <b>Length of simulated time:</b> <br/>
            (10,000 hours = 1 year)<br/>
            (0 = default = 10 years = 100,000 hrs)<br/>
            <input type="text" name="nSimLength" size="7" value="0">
        </td>
-->

        <td>
            <b>Internet bandwith</b> <br/>
            for auditing (in Mbps): <br/>
             <br />
            <input type="text" name="nBandwidthMbps" value="100">
        </td>
        
                
    <td>
        <table>
            <tr><th align="left">
                <b>Size of Documents (MB)                    </b>
            </th></tr>
            <tr><td>
                <select name="nDocSize">
                    <option value="5">&nbsp;&nbsp;5 (small, text/photo)&nbsp;</option>
                    <option value="50" selected>&nbsp;&nbsp;50 (large, audio)&nbsp;</option>
                    <option value="500">&nbsp;&nbsp;500 (very large, video)&nbsp;</option>
                    <option value="5000">&nbsp;&nbsp;5000 (giant, movie)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

               
    <td>
        <table>
            <tr><th align="left">
                <b>Size of Storage Shelf (TB)                    </b>
            </th></tr>
            <tr><td>
                <select name="nShelfSize">
                    <option value="1" selected>&nbsp;&nbsp;1 (normal)&nbsp;</option>
                    <option value="10">&nbsp;&nbsp;10 (large)&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>


    </tr>

<!-- redo button -->
    <tr bgcolor="#FF6666">
        <td>            <b>Redo</b><br/>
            Force recalculation of these cases
            even if they have been done recently.<br/>
            <input type="checkbox" name="bRedo" value="true" class="largerCheckbox"><br/><br/>
        </td>

<!-- test mode warning button -->
                <td colspan="2" centered><strong><font size="+2">TEST only!</font> </strong>
            Print instructions, but
            <em>do not run</em> simulations.<br />
            <font size="+1">Uncheck me for production run!</font><br/>
            <input type="checkbox" name="bTestOnly" value="true" checked class="largerCheckbox" ><br/><br/>
        </td>

<!-- Checkbox for running detached -->
                <td>
            <strong>Run detached process?</strong><br />
            Results go to logfile, and you may log out.<br />
            <input type="checkbox" name="bRunDetached" value="true" scale=10 class="largerCheckbox" ><br /><br />
        </td>
        
<!-- Logfilename for running detached -->
                <td>
            <strong>Logfile name for detached running</strong><br />
            Data will be appended to an existing file.<br />
            <input type="text" name="sDetachedLogfile", size=15, value="">
        </td>

    </tr>

    </table>

<!--  a c t i o n   b u t t o n  -->
    <p>
        <center>    
            <button type="submit" value="start" bgcolor="#ffaaaa">
                <strong><font face="Arial" size="+3">  Run Me!  </font></strong>
            </button>
        </center>
    </p>
    </font>
</form>

<p>
<font face="Arial" size="-1">      Last edited 20181115.1848 </font>
</p>

</body>


<!-- Edit history:
20170220    RBL Original version cribbed almost entirely from previous
                 hand-wrought form.  Add block invocations so that Jinja 
                 can add the blocks of HTML generated by the child from
                 the instruction files.  Leave all the hand-written blocks
                 for non-instruction parameters that the user may select.  
20170520    RBL Add bRedo checkbox.
                Correct missing </td> for bTestOnly.
20170913    RBL Widen the table w.r.t. the window.  
20171129    RBL Remove min/max vars in favor of multi-select ones.
20171130    RBL Narrow formatting a little.  
20180408    RBL Check on simlen input, widen field, add comment. 
                 Change nSimLength to multi-select pulldown. 
20181115    RBL Add nDocuments block.  Hope it fits.  


-->

</html>
