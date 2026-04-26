# Simple Lab Dilution Protocol

### Description
This script calculates the exact volumes needed for a dilution. 
It requires inputs in **ng/µl** and **µl**.

### Sample Input
- **Stock (C1):** 100
- **Target (C2):** 5
- **Final Vol (V2):** 500

### Expected Result
- Stock: 25.00 µl
- Diluent: 475.00 µl

AI prompt (for Gemini): 
> Write a linear Python script for a biochemistry lab to calculate dilutions using C1V1=C2​V2, forcing all inputs to be in ng/µl and µl, and outputting a simple 3-line protocol (Stock, Diluent, Total) using f-strings rounded to 2 decimal places.
