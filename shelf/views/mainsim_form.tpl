<form action="mainsim" method="post">
    <font size="+1">
        <title>PreservationSimulation single run</title>
        <h1>MIT Library Preservation Simulation Project</h1>
        <p><h3>Choose options for single simulation run</h3></p>

    <table cellpadding=6 cellspacing="0" border="0">
    
    <tr bgcolor="#ffffbb">
        <td colspan="3">
        <b>Common options</b>
        </td>
    </tr>
    
    <tr bgcolor="#ffffbb">
        <td>Family dir: <font color="red">* required</font><br />
            <input type="text" name="sFamilyDir" size="30" /></td>
        <td>Specific dir: <font color="red">* required</font><br />
            <input type="text" name="sSpecificDir" size="30" /></td>
        <td>Random seed: <br />
            <input type="text" name="nRandomSeed" value="1" /></td>
    </tr>
    
    <tr bgcolor="#ffffbb">
        <td>Number of copies: <br />
             <br />
            <select name="nCopies">
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
        <td>Sector half-life: <br />
            (in megaHours)<br />
            <select name="nLifem">
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
        <td>Sector half-life in kiloHours: <br />(Use only if megaHours is "none")<br />
            <input type="text" name="nLifek" value="" size="8" /></td>
    </tr>
    
    <tr bgcolor="#ccffbb">
        <td colspan="3">
        <b>Auditing of collection</b>
        </td>
    </tr>
    
    <tr bgcolor="#ccffbb">
        <td>
            Auditing cycle frequency: <br />
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
            Number of audit segments <br />
            per cycle: <br />
            <select name="nAuditSegments">
                <option value="1" selected>1</option>
                <option value="2">2</option>
                <option value="4">4</option>
                <option value="10">10</option>
            </select>
        </td>
        <td>
            Audit type: <br/>
             <br/>
            <select name="sAuditType">
                <option value="TOTAL" selected>TOTAL</option>
                <option value="SEGMENTED">SEGMENTED</option>
                <option value="RANDOM">RANDOM</option>
            </select>
        </td>
    </tr>
    
    <tr bgcolor="#ffddaa">
        <td colspan="5">
            <b>Glitches in operations, e.g, HVAC failures</b>
            <br/>(May be used to kill multiple servers at once, e.g., earthquake, war, credit failure)
        </td>
    </tr>
    
    <tr bgcolor="#ffddaa">
        <td>
            Glitch frequency: <br/>
            (hours) <br />
            <select name="nGlitchFreq">
                <option value="0" selected>0</option>
                <option value="2500">2500 (quarterly)</option>
                <option value="10000">10000 (annually)</option>
                <option value="20000">20000 (every two years)</option>
                <option value="40000">40000 (every four years)</option>
            </select>
        </td>
        <td>
            Glitch impact percentage: <br/>
            (reduction of sector lifetime)<br/>
            <select name="nGlitchImpact">
                <option value="100" selected>100 (fatal to server)</option>
                <option value="90">90 (10-fold increase in errors)</option>
                <option value="80">80 (5-fold increase)</option>
                <option value="67">67 (triple error rate)</option>
                <option value="50">50 (double error rate)</option>
            </select>
        </td>
        <td>
            Glitch maximum life: <br/>
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
            Glitch span of impact: <br/>
            (number of servers affected)<br/>
            <select name="nGlitchSpan">
                <option value="1" selected>1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="5">5</option>
            </select>
        </td>
        <td>
            Glitch decay half-life: <br/>
            (hours) <br />
            <select name="nGlitchDecay">
                <option value="0" selected>0 (no decay)</option>
                <option value="250">250 (week)</option>
                <option value="1000">1000 (month)</option>
            </select>
        </td>
    </tr>

    <tr bgcolor="#ffaaaa">
        <td colspan="4">
            <b>Economic shocks that may affect multiple servers</b> (Not Yet Implemented)
        </td>
    </tr>

    <tr bgcolor="#ffaaaa">
        <td>
            Shock frequency: <br/>
            (hours) <br />
            <select name="nShockFreq">
                <option value="0" selected>0</option>
                <option value="2500">2500 (quarterly)</option>
                <option value="10000">10000 (annually)</option>
                <option value="20000">20000 (every two years)</option>
                <option value="40000">40000 (every four years)</option>
            </select>
        </td>
        <td>
            Shock impact percentage: <br/>
            (reduction of server lifetime)<br/>
            <select name="nShockImpact">
                <option value="100" selected>100 (fatal to server)</option>
                <option value="90">90 (10-fold increase in errors)</option>
                <option value="80">80 (5-fold increase)</option>
                <option value="67">67 (triple error rate)</option>
                <option value="50">50 (double error rate)</option>
            </select>
        </td>
        <td>
            Shock maximum life: <br/>
            (hours) <br />
            <select name="nShockMaxlife">
                <option value="0" selected>0 (forever)</option>
                <option value="250">250 (week)</option>
                <option value="1000">1000 (month)</option>
                <option value="2500">2500 (quarter)</option>
                <option value="10000">10000 (year)</option>
            </select>
        </td>
        <td>
            Shock span of impact: <br/>
            (number of servers affected)<br/>
            <select name="nShockSpan">
                <option value="1" selected>1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="5">5</option>
            </select>
        </td>
    </tr>

    <tr bgcolor="#eeeeee">
        <td colspan="3">
            <b>Logging: detail, where</b>
        </td>
    </tr>

    <tr bgcolor="#eeeeee">
        <td>
            Short log: <br/>
            (includes only params and stats,<br/>
             no details of sector errors) <br/>
            <input type="checkbox" name="bShortLog">
        </td>
        <td>
            Log filename: <br/>
            (blank = stdout) <br/>
            <input type="text" name="sLogFile" size="30" >
        </td>
        <td>
            Logging level: <br/>
            (NYI) <br/>
            <select name="sLogLevel">
                <option name="INF0" selected>INFO</option>
                <option name="DEBUG">DEBUG</option>
            </select>
        </td>
    </tr>

    <tr bgcolor="#dddddd">
        <td colspan="5">
            <b>Document size and shelf size (and doc size mixture, if any)</b>
    </tr>

    <tr bgcolor="#dddddd">
        <td>
            Size of storage shelf: <br/>
            (terabytes) <br/>
            <select name="nShelfSize">
                <option value="1">1 TB</option>
                <option value="10" selected>10 TB</option>
            </select>
        </td>
        <td>
            Size of small document: <br/>
            (megabytes) <br/>
            <select name="nSmallDoc">
                <option value="5">5 MB</option>
                <option value="50" selected>50 MB</option>
                <option value=""500>500 MB</option>
            </select>
        </td>
        <td>
            Size of large doc (if any): <br/>
            (megabytes) <br/>
            <select name="nLargeDoc">
                <option value="50" selected>50 MB</option>
                <option value="500">500 MB</option>
                <option value="5000">5000 MB</option>
            </select>
        </td>
        <td>
            Percentage of small docs <br/>
            in the mix of docs: <br/>
            <select name="nSmallDocPct">
                <option value="100" selected>100%</option>
                <option value="50">50%</option>
                <option value="90">90%</option>
            </select>
        </td>
        <td>
            Std dev of doc size: <br/>
            (if doc size if variable and not fixed)<br/>
            <input type="text" name="nPctDocVar" value="0">
        </td>
    </tr>

    <tr bgcolor="#cccccc">
        <td colspan="2">
        <b>General params</b>
        </td>
    </tr>

    <tr bgcolor="#cccccc">
        <td>
            Length of simulated time: <br/>
            (10,000 hours = 1 year)<br/>
            (0 = default = 10 years)<br/>
            <input type="text" name="nSimLength" value="0">
        </td>
        <td>
            Communications bandwith <br/>
            for auditing (in Mbps): <br/>
             <br />
            <input type="text" name="nBandwidthMbps" value="100">
        </td>
    </tr>

    </table>
    
    <p>
        <center>    
            <button type="submit" value="start" bgcolor="#ffaaaa">
                <strong><font face="Arial" size="+2">  Run Me!  </font></strong>
            </button>
        </center>
    </p>
    </font>
</form>
