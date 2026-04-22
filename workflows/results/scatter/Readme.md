
# Scatterplots

The data is taken from spatial_obl table (or user defined table that has spatial obl data) and filtered using "tags" column.

The tag indicator is in the filename. 

- ELT = event+location+time
- EL = event+location 
- E = event 
- L = location
- A = alive
- S = state
- T = time 

How the tags were assigned in conf file:

| tag in file | target tag | other tags |
| ------------- | ------------- |------------- |
| A | A | ELT,S |
| E |  E | A,LT,S |
| EL | EL | A,S,T |
| ELT | ELT | A,S |
| L | L | A,ET,S |
| S | S | A,ELT |
| T | T | A,EL,S |


The n-lines on the graphs:

- grey zigzag: initial n-line 
- colored "smooth" line at the bottom of grey zigzag: for visual. Bottom poits of the grey zigzag.
- n+1 and -1 lines: grey zigzag +1 or -1




