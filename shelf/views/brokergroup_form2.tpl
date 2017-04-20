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
                </p><br/>
            </td></tr>
            <p></p>
        </table>


    <table cellpadding=6 cellspacing="0" border="0" width="90%">

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
                <input type="text" name=sFamilyDir size="10" value= 
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
                <input type="text" name=sSpecificDir size="10" value= 
                >
            </td></tr>
        </table>
    </td>

               <td>
        <table>
            <tr><td>
                <b>Database Name
                    </b>
            </td></tr>
            <tr><td>
                <input type="text" name=sDatabaseName size="10" value=brokeradmin 
                disabled>
            </td></tr>
        </table>
    </td>

               <td>
        <table>
            <tr><td>
                <b>Number of Replications with Random Seeds
                    </b>
            </td></tr>
            <tr><td>
                <input type="text" name=nRandomSeeds size="5" value=21 
                >
            </td></tr>
        </table>
    </td>

    </tr>

<!--  c o p i e s ,   s e c t o r   l i f e  -->
    <tr bgcolor="#ffffbb">
               
    <td>
        <table>
            <tr><th align="left">
                <b>Minimum Number of Copies of Documents                    </b>
            </th></tr>
            <tr><td>
                <select name="nCopiesMin">
                    <option value="1" selected>&nbsp;&nbsp;1&nbsp;</option>
                    <option value="2">&nbsp;&nbsp;2&nbsp;</option>
                    <option value="3">&nbsp;&nbsp;3&nbsp;</option>
                    <option value="4">&nbsp;&nbsp;4&nbsp;</option>
                    <option value="5">&nbsp;&nbsp;5&nbsp;</option>
                    <option value="8">&nbsp;&nbsp;8&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

               
    <td>
        <table>
            <tr><th align="left">
                <b>Maximum Number of Copies of Documents                    </b>
            </th></tr>
            <tr><td>
                <select name="nCopiesMax">
                    <option value="1">&nbsp;&nbsp;1&nbsp;</option>
                    <option value="2">&nbsp;&nbsp;2&nbsp;</option>
                    <option value="3">&nbsp;&nbsp;3&nbsp;</option>
                    <option value="4">&nbsp;&nbsp;4&nbsp;</option>
                    <option value="5" selected>&nbsp;&nbsp;5&nbsp;</option>
                    <option value="8">&nbsp;&nbsp;8&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

               
    <td>
        <table>
            <tr><th align="left">
                <b>Minimum Half-life of Storage Logical Blocks (megahours)                    </b>
            </th></tr>
            <tr><td>
                <select name="nLifemMin">
                    <option value="2">&nbsp;&nbsp;2&nbsp;</option>
                    <option value="3">&nbsp;&nbsp;3&nbsp;</option>
                    <option value="5">&nbsp;&nbsp;5&nbsp;</option>
                    <option value="10">&nbsp;&nbsp;10&nbsp;</option>
                    <option value="20">&nbsp;&nbsp;20&nbsp;</option>
                    <option value="30">&nbsp;&nbsp;30&nbsp;</option>
                    <option value="50">&nbsp;&nbsp;50&nbsp;</option>
                    <option value="100" selected>&nbsp;&nbsp;100&nbsp;</option>
                    <option value="200">&nbsp;&nbsp;200&nbsp;</option>
                    <option value="300">&nbsp;&nbsp;300&nbsp;</option>
                    <option value="500">&nbsp;&nbsp;500&nbsp;</option>
                    <option value="1000">&nbsp;&nbsp;1000&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

               
    <td>
        <table>
            <tr><th align="left">
                <b>Maximum Half-life of Storage Logical Blocks (megahours)                    </b>
            </th></tr>
            <tr><td>
                <select name="nLifemMax">
                    <option value="2">&nbsp;&nbsp;2&nbsp;</option>
                    <option value="3">&nbsp;&nbsp;3&nbsp;</option>
                    <option value="5">&nbsp;&nbsp;5&nbsp;</option>
                    <option value="10">&nbsp;&nbsp;10&nbsp;</option>
                    <option value="20">&nbsp;&nbsp;20&nbsp;</option>
                    <option value="30">&nbsp;&nbsp;30&nbsp;</option>
                    <option value="50">&nbsp;&nbsp;50&nbsp;</option>
                    <option value="100">&nbsp;&nbsp;100&nbsp;</option>
                    <option value="200">&nbsp;&nbsp;200&nbsp;</option>
                    <option value="300">&nbsp;&nbsp;300&nbsp;</option>
                    <option value="500">&nbsp;&nbsp;500&nbsp;</option>
                    <option value="1000" selected>&nbsp;&nbsp;1000&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

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
                    <option value="0">&nbsp;&nbsp;0&nbsp;</option>
                    <option value="1000">&nbsp;&nbsp;1000&nbsp;</option>
                    <option value="2500">&nbsp;&nbsp;2500&nbsp;</option>
                    <option value="5000">&nbsp;&nbsp;5000&nbsp;</option>
                    <option value="10000" selected>&nbsp;&nbsp;10000&nbsp;</option>
                    <option value="20000">&nbsp;&nbsp;20000&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

                
    <td>
        <table>
            <tr><th align="left">
                <b>Number of Audit Segments per Cycle                    </b>
            </th></tr>
            <tr><td>
                <select name="nAuditSegments">
                    <option value="1" selected>&nbsp;&nbsp;1&nbsp;</option>
                    <option value="2">&nbsp;&nbsp;2&nbsp;</option>
                    <option value="4">&nbsp;&nbsp;4&nbsp;</option>
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
                    <option value="TOTAL" selected>&nbsp;&nbsp;TOTAL&nbsp;</option>
                    <option value="SYSTEMATIC">&nbsp;&nbsp;SYSTEMATIC&nbsp;</option>
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
                <select name="nShockFreq">
                    <option value="0">&nbsp;&nbsp;0&nbsp;</option>
                    <option value="10000">&nbsp;&nbsp;10000&nbsp;</option>
                    <option value="20000">&nbsp;&nbsp;20000&nbsp;</option>
                    <option value="30000">&nbsp;&nbsp;30000&nbsp;</option>
                    <option value="50000" selected>&nbsp;&nbsp;50000&nbsp;</option>
                    <option value="100000">&nbsp;&nbsp;100000&nbsp;</option>
                    <option value="200000">&nbsp;&nbsp;200000&nbsp;</option>
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
                <select name="nShockImpact">
                    <option value="20">&nbsp;&nbsp;20&nbsp;</option>
                    <option value="33">&nbsp;&nbsp;33&nbsp;</option>
                    <option value="50" selected>&nbsp;&nbsp;50&nbsp;</option>
                    <option value="67">&nbsp;&nbsp;67&nbsp;</option>
                    <option value="90">&nbsp;&nbsp;90&nbsp;</option>
                    <option value="100">&nbsp;&nbsp;100&nbsp;</option>
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
                <select name="nShockMaxlife">
                    <option value="0">&nbsp;&nbsp;0&nbsp;</option>
                    <option value="5000">&nbsp;&nbsp;5000&nbsp;</option>
                    <option value="10000" selected>&nbsp;&nbsp;10000&nbsp;</option>
                    <option value="20000">&nbsp;&nbsp;20000&nbsp;</option>
                    <option value="30000">&nbsp;&nbsp;30000&nbsp;</option>
                    <option value="50000">&nbsp;&nbsp;50000&nbsp;</option>
                    <option value="100000">&nbsp;&nbsp;100000&nbsp;</option>
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
                <select name="nShockSpan">
                    <option value="1" selected>&nbsp;&nbsp;1&nbsp;</option>
                    <option value="2">&nbsp;&nbsp;2&nbsp;</option>
                    <option value="3">&nbsp;&nbsp;3&nbsp;</option>
                    <option value="4">&nbsp;&nbsp;4&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>

               
    <td>
        <table>
            <tr><th align="left">
                <b>Expected Half-life of Servers (hrs) (0=infinite)                    </b>
            </th></tr>
            <tr><td>
                <select name="nServerDefaultLife">
                    <option value="0">&nbsp;&nbsp;0=infinite&nbsp;</option>
                    <option value="50000">&nbsp;&nbsp;50000=5yrs&nbsp;</option>
                    <option value="100000" selected>&nbsp;&nbsp;100000=10yrs&nbsp;</option>
                    <option value="200000">&nbsp;&nbsp;200000=20yrs&nbsp;</option>
                    <option value="500000">&nbsp;&nbsp;500000=50yrs&nbsp;</option>
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
                <select name="nGlitchFreq">
                    <option value="0">&nbsp;&nbsp;0&nbsp;</option>
                    <option value="3333" selected>&nbsp;&nbsp;3333&nbsp;</option>
                    <option value="10000">&nbsp;&nbsp;10000&nbsp;</option>
                    <option value="20000">&nbsp;&nbsp;20000&nbsp;</option>
                    <option value="30000">&nbsp;&nbsp;30000&nbsp;</option>
                    <option value="50000">&nbsp;&nbsp;50000&nbsp;</option>
                    <option value="100000">&nbsp;&nbsp;100000&nbsp;</option>
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
                <select name="nGlitchImpact">
                    <option value="10">&nbsp;&nbsp;10&nbsp;</option>
                    <option value="33" selected>&nbsp;&nbsp;33&nbsp;</option>
                    <option value="50">&nbsp;&nbsp;50&nbsp;</option>
                    <option value="67">&nbsp;&nbsp;67&nbsp;</option>
                    <option value="90">&nbsp;&nbsp;90&nbsp;</option>
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
                <select name="nGlitchMaxlife">
                    <option value="0">&nbsp;&nbsp;0&nbsp;</option>
                    <option value="250" selected>&nbsp;&nbsp;250&nbsp;</option>
                    <option value="1000">&nbsp;&nbsp;1000&nbsp;</option>
                    <option value="5000">&nbsp;&nbsp;5000&nbsp;</option>
                    <option value="10000">&nbsp;&nbsp;10000&nbsp;</option>
                    <option value="30000">&nbsp;&nbsp;30000&nbsp;</option>
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
                    <option value="0" selected>&nbsp;&nbsp;0&nbsp;</option>
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
             no details of sector errors)<br/> 
             <font size="+1">You may want this turned on 
            production runs.</font> <br/>
            <input type="checkbox" name="bShortLog" value="true">
        </td>

<!--  g e n e r a l  -->
        <td>
            <b>Length of simulated time:</b> <br/>
            (10,000 hours = 1 year)<br/>
            (0 = default = 10 years)<br/>
            <input type="text" name="nSimLength" size="5" value="0">
        </td>

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
                    <option value="5">&nbsp;&nbsp;5&nbsp;</option>
                    <option value="50" selected>&nbsp;&nbsp;50&nbsp;</option>
                    <option value="500">&nbsp;&nbsp;500&nbsp;</option>
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
                    <option value="1" selected>&nbsp;&nbsp;1&nbsp;</option>
                    <option value="10">&nbsp;&nbsp;10&nbsp;</option>
                    </select>
            </td></tr>
        </table>
    </td>


    </tr>

<!-- test mode warning button -->
    <tr bgcolor="#FF6666">
        <td>&nbsp;</td>
        <td>&nbsp;</td>

                <td><strong><font size="+2">TEST only!</font> </strong>
            Print instructions, 
            do not run simulations. <br />
            <font size="+1">Uncheck me for production run!</font><br/>
            <input type="checkbox" name="bTestOnly" value="true" checked><br/><br/>
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
</body>



<!--  d o c   a n d   s h e l f   s i z e  -->
<!-- NONONO  But preserve this in case we ever need it again.  
    <tr bgcolor="#999999">
        <td colspan="5">
            <b>Document size and shelf size (and doc size mixture, if any)</b>
    </tr>

    <tr bgcolor="#999999">
        <td>
            <b>Size of storage shelf:</b> <br/>
            (terabytes) <br/>
            <select name="nShelfSize">
                <option value="1">1 TB</option>
                <option value="10" selected>10 TB</option>
            </select>
        </td>
        <td>
            <b>Size of small document:</b> <br/>
            (megabytes) <br/>
            <select name="nSmallDoc">
                <option value="5">5 MB</option>
                <option value="50" selected>50 MB</option>
                <option value=""500>500 MB</option>
            </select>
        </td>
        <td>
            <b>Size of large doc (if any):</b> <br/>
            (megabytes) <br/>
            <select name="nLargeDoc">
                <option value="50" selected>50 MB</option>
                <option value="500">500 MB</option>
                <option value="5000">5000 MB</option>
            </select>
        </td>
        <td>
            <b>Percentage of small docs</b> <br/>
            in the mix of docs: <br/>
            <select name="nSmallDocPct">
                <option value="100" selected>100%</option>
                <option value="50">50%</option>
                <option value="90">90%</option>
            </select>
        </td>
        <td>
            <b>Std dev of doc size:</b> <br/>
            (if doc size if variable and not fixed)<br/>
            <input type="text" name="nPctDocVar" value="0">
        </td>
    </tr>
-->

<!-- Edit history:
20170220    RBL Original version cribbed almost entirely from previous
                 hand-wrought form.  Add block invocations so that Jinja 
                 can add the blocks of HTML generated by the child from
                 the instruction files.  Leave all the hand-written blocks
                 for non-instruction parameters that the user may select.  

-->

</html>
