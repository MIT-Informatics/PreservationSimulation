<!-- brokergroup_form_insert.j2 file -->
<!-- brokergroup_ setupform_base.j2 -->
<!-- THIS .tpl FORM IS AUTOMATICALLY GENERATED.  DO NOT EDIT. -->
<html>
    <!-- brokergroup_setupform_base.tpl - template for bottle to present options
        to setup clean output directories for simulations. -->
<head>
    <title>Broker Setup Form</title>
</head>
<body>

<style type="text/css">
    input.largerCheckbox
    {
        width: 18px;
        height: 18px;
    }
</style>

<form action="setup" method="post">
    <font size="+1">
        <title>PreservationSimulation broker.py Setup for Output Dirs</title>
        <h1>MIT Library Preservation Simulation Project</h1>
        <p><h3>Choose options for DIRECTORIES FOR OUTPUT of simulations.</h3></p>
        
        <table border="0" width="50%">
            <tr><td>
                <p>Use this interface is used to set up a directory structure
                    to hold the output of simulation runs.  Specify 
                    the family and specific directories and whether you 
                    want them cleaned out completely before proceeding.  
                </p>
                <p>WARNING: If you ask for the directory structure to be 
                    cleared, it will be erased and re-established as empty.
                </p><br/>
            </td></tr>
            <p></p>
        </table>


    <table cellpadding=6 cellspacing="0" border="0" width="97%">

<!--  c o m m o n   o p t i o n s  -->    
    <tr bgcolor="#ffffbb">
        <td colspan="4">
        <b>Where is the directory tree?</b>
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

        
        <!-- clear button -->
        <td>            <b>Clear directory structure?</b><br/>
            Completely erase and re-establish directory tree<br/>
            <input type="checkbox" name="bClearDirs" value="true" class="largerCheckbox"><br/><br/>
        </td>

    </tr>

    </table>

<!--  a c t i o n   b u t t o n  -->
    <p>
        <center>    
            <button type="submit" value="start" bgcolor="#ffaaaa">
                <strong><font face="Arial" size="+3">  OK  </font></strong>
            </button>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <button type="submit" value="cancel" bgcolor="#ffaaaa">
                <strong><font face="Arial" size="+3">  Cancel  </font></strong>
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
20170520    RBL Add bRedo checkbox.
                Correct missing </td> for bTestOnly.
20170913    RBL Widen the table w.r.t. the window.  
20171129    RBL Remove min/max vars in favor of multi-select ones.
20171130    RBL Narrow formatting a little.  

-->

</html>