print("Lab Dilution Calculator (C1V1 = C2V2)")
  
#Input for Stock (C1)
c1 = float(input("Enter Stock Concentration (ng/ul): "))
  
#Input for Target (C2)
c2 = float(input("Enter Target Concentration (ng/ul): "))

#Input for Final Volume (V2)
v2 = float(input("Enter Final Desired Volume (ul): "))

# Calculation: V1 = (C2 * V2) / C1
v1 = (c2 * v2) / c1
diluent = v2 - v1

print(f"Stock:   {v1} ul")
print(f"Diluent: {diluent} ul")
print(f"Total:   {v2} ul")
