import pandas as pd # Create a dataframe with the provided information
seed_data = {
    "Type": ["Herb", "Annual", "Annual", "Annual", "Annual", "Vegetable", "Annual", "Vegetable"],
    "Species": [
        "Allium schoenoprasum",
        "Zinnia elegans",
        "Myosotis sylvatica",
        "Zinnia elegans",
        "Tagetes patula",
        "Allium fistulosum",
        "Delphinium elatum",
        "Allium fistulosum"
    ],
    "Common Name": [
        "Chives",
        "Zinnia",
        "Forget-Me-Not",
        "Zinnia",
        "Marigold",
        "Bunching Onion",
        "Delphinium",
        "Bunching Onion"
    ],
    "Variety": [
        "Dolores",
        "Candy Cane",
        "Blue Bird",
        "Giants of California",
        "French Dwarf Double Mix",
        "Evergreen",
        "Pacific Giant Mixed Colors",
        "White Lisbon"
    ],
    "Vendor": [
        "Burpee",
        "Ferry-Morse",
        "Burpee",
        "American Seed",
        "American Seed",
        "Ferry-Morse",
        "American Seed",
        "Burpee"
    ],
    "Amount": ["400 mg", "600 mg", "100 mg", "100 mg", "15 mg", "60 seeds", "100 mg", "700 mg"]
}

df = pd.DataFrame(seed_data)

# Save the dataframe to a CSV file
csv_file_path = "seed_varieties.csv"
df.to_csv(csv_file_path, index=False)

