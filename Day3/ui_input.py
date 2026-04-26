from logic import calculate_dilution

c1 = float(input("Enter stock concentration (C1): "))
c2 = float(input("Enter desired concentration (C2): "))
v2 = float(input("Enter final volume (V2, in ul): "))

stock_vol, diluent_vol = calculate_dilution(c1, c2, v2)

print(f"\nStock to take:  {stock_vol:.2f} ul")
print(f"Diluent to add: {diluent_vol:.2f} ul")
print(f"Total volume:   {stock_vol + diluent_vol:.2f} ul")
