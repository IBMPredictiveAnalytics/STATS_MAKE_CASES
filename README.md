# STATS_MAKE_CASES
A conversion of the custom dialog to make a dataset of random data according to any of the distributions supported in the rv.* functions plus the triangular distribution.

---
Requirements
----
- IBM SPSS Statistics 18 or later and the corresponding IBM SPSS Statistics-Integration Plug-in for Python.


---
Installation intructions
----
1. Open IBM SPSS Statistics
2. Navigate to Utilities -> Extension Bundles -> Download and Install Extension Bundles
3. Search for the name of the extension and click Ok. Your extension will be available.

---
Tutorial
----
Generate a dataset of random values<br/><br/>
STATS MAKE CASES <br/> <br/>
DATASET = dataset name<sup>&#42;</sup><br/>
NUMVARS = number of variables<sup>&#42;</sup><br/>
NUMCASES = number of cases<sup>&#42;</sup>  <br/>
DISTRIBUTION =
BERNOULLI or BETA or BINOM or CAUCHY or 
CHISQ or EXP or F or GAMMA or GEOM or 
HALFNRM or HYPER or IGAUSS or LAPLACE or 
LNORMAL or LOGISTIC or NEGBIN or NORMAL or 
PARETO or POISSON or T or TRIANGULAR or 
UNIFORM or WEIBULL<br/> 
P1 = first parameter<sup>&#42;</sup><br/>
P2 = second parameter<br/>
P3 = third parameter<br/></p>

<p>CORRELATIONS<br/>
ORTHOG = NOFACTOR<sup>&#42;&#42;</sup> or FACTOR<br/>
STRUCTURE = NONE<sup>&#42;&#42;</sup> or EQUAL or TOEPLITZ or 
FA or ARBITRARY or RANDOM<br/>
DISPLAY = YES<sup>&#42;&#42;</sup> or NO<br/>
CORRS = list of correl	ations</p

<p><sup>&#42;</sup> Required<br/>
<sup>&#42;&#42;</sup> Default</p>

STATS MAKE CASES /HELP prints this information and does nothing else.

Example:
```
STATS MAKE CASES
DATASET=normals NUMVARS=3 NUMCASES=100
DISTRIBUTION=NORMAL P1=5.0 P2=2.0 
/CORRELATIONS ORTHOG=NOFACTOR STRUCTURE=TOEPLITZ DISPLAY=YES
CORRS=1. .5 .3.
```

**DATASET** specify the name for the dataset to be created. If that dataset name is alreadyin use, it will be replaced.

**NUMVARS** specify the number of variables to be created. The variable names will be named V1 ....  An ID variable named ID is always created.

**NUMCASES** specify the number of cases to be created.

**DISTRIBUTION** specify the probability distribution to be sampled from the list above.  Any distribution for which Statistics has an RV.* function can be used plus the Triangular distribution.  For the selected distribution  enter the appropriate number of parameter valuess in the order they appear in the RV function in P1, P2, and P3 fields..  For the triangular distribution, the parameters are the min, max, and mode of the distribution.Since the regular random number generators are used, the choice of generator and starting value for the sequence follows the regular SPSS setting.
**CORRELATIONS**
By default, no correlations are generated for the variables.
**ORTHOG** specifies whether the generated variables are orthogonalized or not before any subsequent transformation.
**STRUCTURE** specifies the form of the correlations to be generated, defaulting to NONE. Choose the desired correlation structure and enter the required parameters in the CORRS keyword.
The Help in the Analyze>Mixed Models>Linear dialog and the Command Syntax Reference gives the
definitions of these structures. 

OPTIONS
-------
* **None**: The variables will be approximately or exactly uncorrelated.  No correlations should be specified
* **Equal**: Each pair of variables will have the same correlation.  Enter one correlation coefficient.
* **Toeplitz**: The correlations will be the same down each diagonal of the correlation matrix. Enter as many correlation coefficients as there are variables, starting with 1.
* **Factor Analytic**: The correlation for each pair of variables will be the product lambda(i) * lambda(j) plus a constant, d, on the diagonal.  Enter d followed by one lambda for each variable.
* **Arbitrary**: The correlation for each pair will be a specified value.  Enter the lower triangle of the correlation matrix, ending each row with 1.
* **Random**: The correlation for each pair will be a random value drawn from a uniform distribution.  Enter the minimum and maximum correlations.To generate the correlation structure, the variables are replaced by linear combinations to yield the specified structure.
Note that this will change the probability distribution in most cases, although Normal variables will still follow that distribution.
* **DISPLAY** specifies whether to display the specified correlation matrix.

---
License
----

- Apache 2.0
                              
Contributors
----

  - JKP, IBM SPSS
