import sys
from logic import calculate_dilution

if len(sys.argv) != 4:
    print("Usage: python ui_cli.py <C1> <C2> <V2>")
    print("  C1  — stock concentration")
    print("  C2  — desired concentration")
    print("  V2  — final volume (ul)")
    sys.exit(1)

c1 = float(sys.argv[1])
c2 = float(sys.argv[2])
v2 = float(sys.argv[3])

stock_vol, diluent_vol = calculate_dilution(c1, c2, v2)

print(f"Stock to take:  {stock_vol:.2f} ul")
print(f"Diluent to add: {diluent_vol:.2f} ul")
print(f"Total volume:   {stock_vol + diluent_vol:.2f} ul")
