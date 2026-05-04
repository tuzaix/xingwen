import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.admin import AdminUser, AdminRole
from app.core.security import get_password_hash

async def seed_data():
    async with AsyncSessionLocal() as db:
        # Check if role exists
        result = await db.execute(select(AdminRole).filter(AdminRole.role_name == "super_admin"))
        role = result.scalars().first()
        if not role:
            role = AdminRole(
                role_name="super_admin",
                description="Super Administrator with all permissions",
                permissions=["*"]
            )
            db.add(role)
            await db.flush()
        
        # Check if admin exists
        result = await db.execute(select(AdminUser).filter(AdminUser.username == "admin"))
        admin = result.scalars().first()
        if not admin:
            admin = AdminUser(
                username="admin",
                password_hash=get_password_hash("admin123"),
                real_name="Super Admin",
                role_id=role.id,
                status=1
            )
            db.add(admin)
        
        await db.commit()
        print("Initial admin seeded: admin / admin123")

if __name__ == "__main__":
    asyncio.run(seed_data())
