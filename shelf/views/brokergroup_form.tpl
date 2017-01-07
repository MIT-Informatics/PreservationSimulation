<html>
    <!-- brokergroup_form.tpl - template for bottle to present options
        for a broker.py run of hundreds or thousands of individual simulation
        runs using PreservationSimulation/shelf/main.py -->
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


    <table cellpadding=6 cellspacing="0" border="0">

<!--  c o m m o n   o p t i o n s  -->    
    <tr bgcolor="#ffffbb">
        <td colspan="4">
        <b>Common options</b>
        </td>
    </tr>

<!--  d i r e c t o r i e s ,  d a t a b a s e   n a m e  -->    
    <tr bgcolor="#ffffbb">
        <td><b>Family dir:</b> <font color="red">* required</font><br /><br />
            <input type="text" name="sFamilyDir" size="30" /><br/><br/></td>
        <td><b>Specific dir:</b> <font color="red">* required</font><br /><br />
            <input type="text" name="sSpecificDir" size="30" /><br/><br/></td>
        <td><b>Instruction MongoDb:</b> <font color="red">* required</font><br /><br />
            <input type="text" name="sDatabaseName" size="30" /><br/><br/></td>
        <td><b>Number of trials:</b> <br /><br />
            <select name="nRandomSeeds">
                <option value="11">11</option>
                <option value="21" selected>21</option>
                <option value="41">41</option>
                <option value="101">101</option>
            </select>
            <br/><br/>
        </td>
    </tr>

<!--  c o p i e s ,   s e c t o r   l i f e  -->
    <tr bgcolor="#ffffbb">
        <td><b>MIN Number of copies:</b> <br />
             <br />
            <select name="nCopiesMin">
                <option value="1" selected>1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
                <option value="8">8</option>
                <option value="10">10</option>
                <option value="12">12</option>
                <option value="14">14</option>
                <option value="20">20</option>
            </select></td>
        <td><b>MAX Number of copies:</b> <br />
             <br />
            <select name="nCopiesMax">
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5" selected>5</option>
                <option value="8">8</option>
                <option value="10">10</option>
                <option value="12">12</option>
                <option value="14">14</option>
                <option value="20">20</option>
            </select></td>
        <td><b>MIN Sector half-life:</b> <br />
            (in megaHours)<br />
            <select name="nLifemMin">
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="30">30</option>
                <option value="50">50</option>
                <option value="100" selected>100</option>
                <option value="200">200</option>
                <option value="300">300</option>
                <option value="500">500</option>
                <option value="1000">1000</option>
                <option value="2000">2000</option>
                <option value="3000">3000</option>
                <option value="5000">5000</option>
                <option value="10000">10000</option>
        </select></td>
        <td><b>MAX Sector half-life:</b> <br />
            (in megaHours)<br />
            <select name="nLifemMax">
                <option value="none">none</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="30">30</option>
                <option value="50">50</option>
                <option value="100">100</option>
                <option value="200">200</option>
                <option value="300">300</option>
                <option value="500">500</option>
                <option value="1000" selected>1000</option>
                <option value="2000">2000</option>
                <option value="3000">3000</option>
                <option value="5000">5000</option>
                <option value="10000">10000</option>
        </select></td>
    </tr>
 
 <!--  a u d i t i n g  -->   
    <tr bgcolor="#ccffbb">
        <td colspan="4">
        <b>Auditing of collection</b>
        </td>
    </tr>
    
    <tr bgcolor="#ccffbb">
        <td>
            <b>Auditing cycle frequency:</b> <br />
            (hours) <br />
            <select name="nAuditFreq">
                <option value="0" selected>0 (no auditing)</option>
                <option value="1000">1000 (monthly)</option>
                <option value="2500">2500 (quarterly)</option>
                <option value="5000">5000 (semi-annually)</option>
                <option value="10000">10000 (annually)</option>
                <option value="20000">20000 (biennially)</option>
            </select>
        </td>
        <td>
            <b>Number of audit segments</b> <br />
            per cycle: <br />
            <select name="nAuditSegments">
                <option value="1" selected>1</option>
                <option value="2">2</option>
                <option value="4">4</option>
                <option value="10">10</option>
            </select>
        </td>
        <td>
            <b>Audit type:</b> <br/>
             <br/>
            <select name="sAuditType">
                <option value="TOTAL" selected>TOTAL</option>
                <option value="SEGMENTED">SEGMENTED</option>
                <option value="RANDOM">RANDOM</option>
            </select>
        </td>
        <td>&nbsp;</td>
    </tr>

<!--  s h o c k s  -->
    <tr bgcolor="#ffaaaa">
        <td colspan="5">
            <b>Economic shocks that may affect multiple servers</b> 
            <br/>(May be used to decrease life expectancy or kill multiple servers at once.)
        </td>
    </tr>

    <tr bgcolor="#ffaaaa">
        <td>
            <b>Shock frequency:</b> <br/>
            (hours) <br />
            <select name="nShockFreq">
                <option value="0" selected>0 (disabled)</option>
                <option value="2500">2500 (quarterly)</option>
                <option value="10000">10000 (annually)</option>
                <option value="20000">20000 (every two years)</option>
                <option value="30000">30000 (every three years)</option>
                <option value="40000">40000 (every four years)</option>
                <option value="50000">50000 (every five years)</option>
            </select>
        </td>
        <td>
            <b>Shock impact percentage:</b> <br/>
            (reduction of server lifetime)<br/>
            <select name="nShockImpact">
                <option value="100">100 (fatal to server)</option>
                <option value="90">90 (10% normal lifespan)</option>
                <option value="80">80 (20% normal lifespan)</option>
                <option value="67">67 (1/3 normal lifespan)</option>
                <option value="50" selected>50 (1/2 normal lifespan)</option>
                <option value="33">33 (2/3 normal lifespan)</option>
            </select>
        </td>
        <td>
            <b>Shock maximum life:</b> <br/>
            (hours) <br />
            <select name="nShockMaxlife">
                <option value="0">0 (forever)</option>
                <option value="2500">2500 (quarter)</option>
                <option value="5000">5000 (half year)</option>
                <option value="10000" selected>10000 (one year)</option>
                <option value="20000">20000 (two years)</option>
            </select>
        </td>
        <td>
            <b>Shock span of impact:</b> <br/>
            (number of servers affected)<br/>
            <select name="nShockSpan">
                <option value="1" selected>1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
            </select>
        </td>
        <td><b>Server default half-life:</b> <br />(Hours) (zero=infinite)<br />
            <input type="text" name="nServerDefaultLife" value="0" size="10" /></td>
    </tr>

<!--  g l i t c h e s  -->    
    <tr bgcolor="#ffaaaa">
        <td colspan="5">
            <b>Glitches in operations, e.g, HVAC failures</b>
            <br/>(May be used increase error rate on multiple servers at once.)
        </td>
    </tr>
    
    <tr bgcolor="#ffaaaa">
        <td>
            <b>Glitch frequency:</b> <br/>
            (hours) <br />
            <select name="nGlitchFreq">
                <option value="0" selected>0 (disabled)</option>
                <option value="2500">2500 (quarterly)</option>
                <option value="10000">10000 (annually)</option>
                <option value="20000">20000 (every two years)</option>
                <option value="30000">30000 (every three years)</option>
                <option value="40000">40000 (every four years)</option>
                <option value="50000">50000 (every five years)</option>
            </select>
        </td>
        <td>
            <b>Glitch impact percentage:</b> <br/>
            (reduction of sector lifetime)<br/>
            <select name="nGlitchImpact">
                <option value="100">100 (fatal to server)</option>
                <option value="90">90 (10-fold increase in errors)</option>
                <option value="80">80 (5-fold increase)</option>
                <option value="67">67 (triple error rate)</option>
                <option value="50" selected>50 (double error rate)</option>
            </select>
        </td>
        <td>
            <b>Glitch maximum life:</b> <br/>
            (hours) <br />
            <select name="nGlitchMaxlife">
                <option value="0" selected>0 (forever)</option>
                <option value="250">250 (week)</option>
                <option value="1000">1000 (month)</option>
                <option value="2500">2500 (quarter)</option>
                <option value="10000">10000 (year)</option>
            </select>
        </td>
        <td>
            <b>Glitch span of impact:</b> <br/>
            (number of servers affected)<br/>
            <select name="nGlitchSpan">
                <option value="1" selected>1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
            </select>
        </td>
        <td>
            <b>Glitch decay half-life:</b> <br/>
            (hours) <br />
            <select name="nGlitchDecay">
                <option value="0" selected>0 (no decay)</option>
                <option value="250">250 (week)</option>
                <option value="1000">1000 (month)</option>
            </select>
        </td>
    </tr>

<!--  l o g g i n g  -->
    <tr bgcolor="#cccccc">
        <td colspan="1">
            <b>Logging: level of detail</b>
        </td>
        <td colspan="2">
        <b>General params</b>
        </td>
    </tr>

    <tr bgcolor="#cccccc">
        <td>
            <b>Short log:</b> <br/>
            (includes only params and stats,<br/>
             no details of sector errors) <br/>
            <input type="checkbox" name="bShortLog" value="true">
        </td>

<!--  g e n e r a l  -->

        <td>
            <b>Length of simulated time:</b> <br/>
            (10,000 hours = 1 year)<br/>
            (0 = default = 10 years)<br/>
            <input type="text" name="nSimLength" value="0">
        </td>
        <td>
            <b>Communications bandwith</b> <br/>
            for auditing (in Mbps): <br/>
             <br />
            <input type="text" name="nBandwidthMbps" value="100">
        </td>
    </tr>

<!-- test mode warning button -->
    <tr bgcolor="#FF6666">
        <td>&nbsp;</td>
        <td>&nbsp;</td>
        <td><strong><fong size="+2">TEST only!</font> </strong>Print instructions, do not run: <br />
            Uncheck me for production run<br/>
            <input type="checkbox" name="bTestOnly" value="true" checked><br/><br/>
    </tr>

    </table>

<!--  d o c   a n d   s h e l f   s i z e  -->
<!-- NONONO
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
</html>