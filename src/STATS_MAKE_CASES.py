# STATS MAKE CASES extension command
# This replaces the Make Cases with Data custom dialog with a full extension command.


__author__ = "JKP"
__version__ = "1.0.0"

# history
# 26-jun-2023 original version

import spss, spssaux, SpssClient
from extension import Template, Syntax, processcmd



# debugging
#try:
    #import wingdbstub
    #import threading
    #wingdbstub.Ensure()
    #wingdbstub.debugger.SetDebugThreads({threading.get_ident(): 1})
#except:
    #pass

# main function
def makecases(dataset, numvars, numcases, p1, distribution="normal",
     p2=None, p3=None, orthog="nofactor", structure="none", display=True,
    corrs=None, displayinputpgm=False):
    
    parms = [p1, p2, p3]
    parms = [p for p in parms if p is not None]
    structure = structure.upper()   # for historical reasons
    if structure == "NONE" and corrs is not None:
        raise ValueError(_("""Correlations were specified without a structure type."""))
    generate(dataset, numvars, numcases, distribution, parms, orthog, structure,
        corrs, display)

def gendis(distrib, parms):
    """Return expression for random number generation

    distrib is the name of the generator without the "RV."
    parms is a list with blank-separated parameter values
    "triangular" is an exception"""
    

    if distrib.upper() == "TRIANGULAR":   # not built in to Statistics
        if len(parms) != 3:
            raise ValueError(_("The triangular distribution requires three parameters"))
        a = float(parms[0])
        b = float(parms[1])
        c = float(parms[2])
        if not (a <= c <= b) or a == b:
            raise ValueError("Invalid parameters for Triangular distribution: %(a)s, %(b)s, %(c)" % locals())
        Fc = (c-a) / (b-a)
        syn = """COMPUTE #u = RV.UNIFORM(0,1).
        DO IF (#u < %(Fc)s).
            COMPUTE V(#j-1) = %(a)s + SQRT(#u*(%(b)s - %(a)s) * (%(c)s - %(a)s)).
        ELSE.
            COMPUTE V(#j-1) = %(b)s - SQRT((1 - #u)*(%(b)s - %(a)s) * (%(b)s - %(c)s)).
        END IF.""" % locals()
        return syn
    else:
        parms = "(" + ",".join(str(item) for item in parms) + ")"
        return "COMPUTE V(#j-1) = RV.%(distrib)s%(parms)s." % locals()

def gencorrmatrix(corrtype, numvar, corrdata):
    """generate and return  correlation matrix as string according to type

    corrtype
      EQUAL - generate numvar rows of form 1, rho, rho, rho; rho, 1, rho, rho ...
      TOEPLITZ - generate numvar rows of form 1, rho1, rho2, rho(k-1), ...
      FA - generate numvar rows of form d + lambdai*lambdaj
      ARBITRARY - generate specified rows from rows of lower triangle, including diagonal
      RANDOM - generate rows with random correlations between minimum and maximum

      corrdata is a string of numbers appropriate to the correlation type"""

    import copy, random
    corrmat = []
    ###corrdata = corrdata.split()
    corrdata = [str(c) for c in corrdata]
    if corrtype == "EQUAL":
        if len(corrdata) != 1:
            raise ValueError("EQUAL correlations require one parameter")
        row = ["1."] + (numvar-1) *[corrdata[0]]
        for i in range(numvar):
            corrmat.append(copy.copy(row))
            row.insert(0, row.pop())

    elif corrtype == "TOEPLITZ":
        if len(corrdata) != numvar or float(corrdata[0]) != 1:
            raise ValueError("Invalid data for Toeplitz matrix")
        row = copy.copy(corrdata)
        for i in range(numvar):
            corrmat.append(copy.copy(row))
            if i < numvar-1:
                row.insert(0, corrdata[i+1])
                row.pop()

    elif corrtype == "FA":
        if len(corrdata) != numvar + 1:
            raise ValueError("Wrong number of elements for factor analytic correlations")
        d = float(corrdata.pop(0))
        for i in range(numvar):
            row = []
            for j in range(numvar):
                row.append(float(corrdata[i]) * float(corrdata[j]))
                if i == j:
                    row[-1] += d
                row[-1] = str(row[-1])
            corrmat.append(copy.copy(row))

    elif corrtype == "ARBITRARY":
        if len(corrdata) != numvar*(numvar+1)/2:
            raise ValueError("Wrong number of parameters for Arbitrary correlations")
        start = 0
        for i in range(numvar):
            row = corrdata[start:start+i+1]
            corrmat.append(copy.copy(row))
            start += i + 1
        for i in range(numvar):
            for j in range(i+1, numvar):
                corrmat[i].append(corrmat[j][i])

    elif corrtype == "RANDOM":
        if len(corrdata) != 2:
            raise ValueError("Random correlations require two parameters")
        low, high = float(corrdata[0]), float(corrdata[1])
        for i in range(numvar):
            corrmat.append([])
            for j in range(i+1):
                if i == j:
                    corrmat[i].append("1.")
                else:
                    corrmat[i].append(str(random.uniform(low, high)))
                    corrmat[j].append(corrmat[i][-1])

    else:
        raise ValueError("Invalid correlation type")
    result = ";".join([",".join(row) for row in corrmat])
    return result


def generate(dsname, numvar, numcase, distribution, parms, factor, corrtype, corrs, displaycorr):
    """generate new dataset
    
    dsname is the name for the dataset
    numvar is the number of random variables to generate
    numcase is the number of cases
    distribution is the name of the random number function (without "RV.")
    factor is "factor" or "nofactor" to specify whether random data should be orthogonalized
    corrtype is the name of the correlation pattern
    corrs is a string of correlations for the specified corrtype
    displaycorr determines whether the requested correlation matrix is displayed"""
    
    numvar1 = numvar  # number of random variables
    numvar+= 1    # includes the ID variable
    if displaycorr:
        displaycorr = f"""print CORR /format=F8.3 /TITLE="Correlation Matrix Specified for New Random Dataset {dsname}".""" % locals()
    else:
        displaycorr = ""
    # generate random data via an INPUT PROGRAM
    
    distribcode = gendis(distribution, parms)
    gendata=r"""* Create a new dataset.
INPUT PROGRAM.
NUMERIC ID(F5.0).
VECTOR V(%(numvar)s).
LOOP #i = 1 to %(numcase)s.
    DO REPEAT #j = 1 TO %(numvar)s.
        DO IF #j = 1.
           COMPUTE ID = $CASENUM.
        ELSE.
           %(distribcode)s
        END IF.
    END REPEAT.
    END CASE.
END LOOP.
END FILE.
END INPUT PROGRAM.
DATASET NAME %(dsname)s.
DATASET ACTIVATE %(dsname)s.
FORMAT V1 TO V%(numvar1)s (F8.2).
EXECUTE.
DELETE VARIABLES V%(numvar)s."""
    try:
        spss.Submit(gendata % locals())
    except:
        raise
    # Optionally  orthogonalize the data
    
    if factor == "factor":
        ortho = r"""oms /destination viewer=no.
    FACTOR
              /VARIABLES V1 to V%(numvar1)s
              /CRITERIA FACTORS(%(numvar1)s)
              /EXTRACTION PC
              /ROTATION NOROTATE
              /SAVE REG(ALL)
              /METHOD=CORRELATION.
    omsend.
    delete variables V1 TO V%(numvar1)s.
    rename variables (fac1_1 TO fac%(numvar1)s_1=V1 to V%(numvar1)s)."""
        try:
            spss.Submit(ortho % locals())
        except:
            raise 
        spss.Submit("VARIABLE LABELS " + "/".join(["V"+ str(i) for i in range (1, numvar1+1)]))
    
    # Optionally generate correlations among the variables
    
    if corrtype != "NONE":
        import random, copy
        randomdsname = "G" + str(random.uniform(0,1))
        corrmat = gencorrmatrix(corrtype, numvar1, corrs)
        corrcmd = r"""DATASET DECLARE %(randomdsname)s.
PRESERVE.
SET MDISPLAY=TABLES.
MATRIX.
get DATA /variables=V1 TO V%(numvar1)s.
compute ID = T({1:%(numcase)s}).
compute CORR = {%(corrmat)s}.
compute U = chol(CORR).
%(displaycorr)s
compute CORRDATA = DATA * U.
save {ID, CORRDATA} /outfile=%(randomdsname)s /variables = ID V1 TO V%(numvar1)s.
END MATRIX.
DATASET ACTIVATE %(randomdsname)s.
FORMAT V1 TO V%(numvar1)s (F8.2).
DATASET CLOSE %(dsname)s.
DATASET ACTIVATE %(randomdsname)s.
DATASET NAME %(dsname)s.
RESTORE."""
        spss.Submit(corrcmd % locals())

def Run(args):
    """Run the STATS MAKE CASES command"""
    
    args = args[list(args.keys())[0]]
    
    oobj = Syntax([
    Template("DATASET", subc="", var="dataset", ktype="varname", islist=False),
    Template("NUMVARS", subc="", var="numvars", ktype="int", vallist=[1]),
    Template("NUMCASES", subc="", var="numcases", ktype="int"),
    Template("DISTRIBUTION", subc="", var="distribution", ktype="str",
        vallist=["bernoulli","beta","binom","cauchy","chisq",
        "exp","f","gamma","geom","halfnrm","hyper",
        "igauss","laplace","lnormal","logistic",
        "negbin","normal","pareto","poisson","t",
        "triangular","uniform","weibull"]),
    Template("P1", subc="", var="p1", ktype="float"),
    Template("P2", subc="", var="p2", ktype="float"),
    Template("P3", subc="", var="p3", ktype="float"),
    
    Template("ORTHOG", subc="CORRELATIONS", var="orthog", ktype="str",
        vallist=["nofactor", "factor"]),
    Template("STRUCTURE", subc="CORRELATIONS", var="structure", ktype="str",
        vallist=["none", "equal", "toeplitz", "fa", "arbitrary", "random"]),
    Template("DISPLAY", subc="CORRELATIONS", var="display", ktype="bool"),
    Template("CORRS", subc="CORRELATIONS", var="corrs", ktype="float", islist=True),
    
    Template("HELP", subc="", ktype="bool")])

    #enable localization
    global _
    try:
        _("---")
    except:
        def _(msg):
            return msg

    if "HELP" in args:
        #print helptext
        helper()
    else:
        processcmd(oobj, args, makecases)

def helper():
    """open html help in default browser window
    
    The location is computed from the current module name"""

    import webbrowser, os.path

    path = os.path.splitext(__file__)[0]
    helpspec = "file://" + path + os.path.sep + \
         "markdown.html"

    # webbrowser.open seems not to work well
    browser = webbrowser.get()
    if not browser.open_new(helpspec):
        print(("Help file not found:" + helpspec))
try:    #override
    from extension import helper
except:
    pass