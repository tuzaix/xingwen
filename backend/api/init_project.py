import asyncio
import subprocess
import sys
import os

async def run_command(command, description):
    print(f"\n>>> {description}...")
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode == 0:
        print(f"SUCCESS: {description}")
        if stdout:
            print(stdout.decode().strip())
        return True
    else:
        print(f"FAILED: {description}")
        if stderr:
            print(stderr.decode().strip())
        return False

async def main():
    print("=" * 60)
    print("星纹 AI 手相项目首次部署初始化脚本")
    print("=" * 60)

    # 1. 创建数据库
    if not await run_command(f"{sys.executable} create_db.py", "正在创建数据库"):
        return

    # 2. 运行 Alembic 迁移
    if not await run_command("alembic upgrade head", "正在运行数据库迁移 (Alembic)"):
        return

    # 3. 初始化管理员数据
    if not await run_command(f"{sys.executable} seed_admin.py", "正在初始化管理员数据"):
        return

    # 4. 初始化测试卡密 (可选)
    if not await run_command(f"{sys.executable} seed_cards.py", "正在初始化测试卡密"):
        return

    print("\n" + "=" * 60)
    print("项目初始化完成！")
    print("默认管理员: admin / admin123")
    print("测试卡密: XW12345678123456")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
