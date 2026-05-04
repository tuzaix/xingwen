import asyncio
from datetime import datetime, timedelta
from app.db.session import AsyncSessionLocal
from app.models.card import CardCode
from app.core.security import get_password_hash

async def seed_cards():
    async with AsyncSessionLocal() as db:
        test_card = CardCode(
            card_code="XW12345678123456",
            card_secret="dummy", # Not used for now as per simple verify
            batch_no="TEST001",
            card_type="once",
            total_times=1,
            remain_times=1,
            status=0,
            expire_at=datetime.now() + timedelta(days=365),
            channel="official"
        )
        db.add(test_card)
        await db.commit()
        print("Test card seeded: XW-1234-5678-1234-56 (XW12345678123456)")

if __name__ == "__main__":
    asyncio.run(seed_cards())
