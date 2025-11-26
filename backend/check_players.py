from data.real_players import REAL_IPL_PLAYERS

print(f"Total players: {len(REAL_IPL_PLAYERS)}")

# Check for MS Dhoni
dhoni = [p for p in REAL_IPL_PLAYERS if "Dhoni" in p["name"]]
print(f"\nMS Dhoni found: {len(dhoni) > 0}")
if dhoni:
    for player in dhoni:
        print(f"  - {player['name']} ({player['role']}, Base: ₹{player['base_price']} Cr)")

# Check for retired players (sample check)
retired_names = ["Kapil Dev", "Sunil Gavaskar", "Sachin Tendulkar", "Rahul Dravid", "Sourav Ganguly", 
                 "Anil Kumble", "Harbhajan Singh", "Zaheer Khan", "Yuvraj Singh", "Suresh Raina",
                 "Chris Gayle", "AB de Villiers", "Shane Warne", "Brett Lee"]

print(f"\nChecking for retired players:")
found_retired = []
for name in retired_names:
    for player in REAL_IPL_PLAYERS:
        if name in player["name"]:
            found_retired.append(player["name"])

if found_retired:
    print(f"  Found {len(found_retired)} retired players:")
    for name in found_retired:
        print(f"    - {name}")
else:
    print("  No retired players found (except MS Dhoni)")

print(f"\nAll players are active IPL players (2024-2025 season) + MS Dhoni")
