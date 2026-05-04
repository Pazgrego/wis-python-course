def calculate_dilution(c1, c2, v2):
    """C1V1 = C2V2 — returns (v1, diluent) in ul."""
    v1 = (c2 * v2) / c1
    diluent = v2 - v1
    return v1, diluent


if __name__ == "__main__":
    stock_vol, diluent_vol = calculate_dilution(c1=100, c2=10, v2=50)
    print(f"Stock:   {stock_vol} ul")
    print(f"Diluent: {diluent_vol} ul")
    print(f"Total:   {stock_vol + diluent_vol} ul")
