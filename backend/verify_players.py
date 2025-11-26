"""Verify players in database."""
from app import create_app, db
from app.models.player import Player

app = create_app()

with app.app_context():
    total = Player.query.count()
    print(f"\n{'='*60}")
    print(f"Total players in database: {total}")
    print(f"{'='*60}\n")
    
    # Show some sample players
    print("Sample players:")
    for p in Player.query.limit(20).all():
        print(f"  - {p.name:30} ({p.role:4}, {p.country:15}) - Base: ₹{p.base_price} Cr")
    
    print("\n" + "="*60)
    
    # Show base price distribution
    print("\nBase Price Distribution:")
    price_ranges = [
        (0.3, 0.5, "0.3-0.5 Cr"),
        (0.5, 1.0, "0.5-1.0 Cr"),
        (1.0, 1.5, "1.0-1.5 Cr"),
        (1.5, 2.0, "1.5-2.0 Cr"),
        (2.0, 3.0, "2.0+ Cr")
    ]
    
    for min_price, max_price, label in price_ranges:
        count = Player.query.filter(
            Player.base_price >= min_price,
            Player.base_price < max_price
        ).count()
        print(f"  {label:15}: {count:3} players")
    
    print("\n" + "="*60)
    
    # Show role distribution
    print("\nRole Distribution:")
    for role in ['BAT', 'BOWL', 'AR', 'WK']:
        count = Player.query.filter_by(role=role).count()
        print(f"  {role:4}: {count:3} players")
    
    print("\n" + "="*60)
    
    # Show country distribution
    print("\nCountry Distribution:")
    countries = db.session.query(Player.country, db.func.count(Player.id)).group_by(Player.country).all()
    for country, count in sorted(countries, key=lambda x: x[1], reverse=True):
        print(f"  {country:20}: {count:3} players")
    
    print("\n" + "="*60 + "\n")
