from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db.session import get_db
from app.models.card import CardCode
from app.models.report import Report
from app.schemas.card import CardVerify, CardVerifyResponse, CardCreate, CardListResponse
from app.api import deps
from app.utils.card import generate_card_code
from app.core import security
from datetime import datetime, timedelta
from typing import List, Optional

router = APIRouter()

@router.get("/", response_model=CardListResponse)
async def list_cards(
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(deps.get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[int] = None,
    batch_no: Optional[str] = None,
    card_code: Optional[str] = None
):
    query = select(CardCode)
    if status is not None:
        query = query.filter(CardCode.status == status)
    if batch_no:
        query = query.filter(CardCode.batch_no == batch_no)
    if card_code:
        query = query.filter(CardCode.card_code.like(f"%{card_code.upper().replace('-', '')}%"))
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    # Pagination
    result = await db.execute(
        query.order_by(CardCode.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    cards = result.scalars().all()
    
    return {
        "total": total,
        "items": cards,
        "page": page,
        "page_size": page_size
    }

@router.post("/generate")
async def generate_cards(
    data: CardCreate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(deps.get_current_user)
):
    batch_no = f"B{datetime.now().strftime('%Y%m%d%H%M%S')}"
    expire_at = datetime.now() + timedelta(days=data.valid_days)
    
    new_cards = []
    for _ in range(data.count):
        code = generate_card_code()
        # In a real app, you'd verify uniqueness here
        new_card = CardCode(
            card_code=code,
            card_secret="SECRET", # Simplified
            batch_no=batch_no,
            card_type=data.card_type,
            total_times=1,
            remain_times=1,
            status=0,
            expire_at=expire_at,
            created_by=current_admin.id,
            channel=data.channel
        )
        db.add(new_card)
        new_cards.append(new_card)
    
    await db.commit()
    return {"message": f"Successfully generated {len(new_cards)} cards", "batch_no": batch_no}

@router.post("/verify", response_model=CardVerifyResponse)
async def verify_card(
    data: CardVerify,
    db: AsyncSession = Depends(get_db)
):
    # Normalize card code (remove dashes)
    normalized_code = data.card_code.replace("-", "").upper()
    
    result = await db.execute(
        select(CardCode).filter(CardCode.card_code == normalized_code)
    )
    card = result.scalars().first()
    
    if not card:
        return CardVerifyResponse(valid=False, message="卡密无效，请检查后输入")
    
    if card.status != 0:
        if card.status == 1:
            # Find the associated report ID
            report_result = await db.execute(
                select(Report.id).filter(Report.card_code == card.card_code)
            )
            report_id = report_result.scalar_one_or_none()
            return CardVerifyResponse(
                valid=False, 
                message="卡密已被使用", 
                report_id=report_id
            )
        elif card.status == 2:
            return CardVerifyResponse(valid=False, message="卡密已过期")
        else:
            return CardVerifyResponse(valid=False, message="卡密已作废")
            
    if card.expire_at < datetime.now():
        card.status = 2
        await db.commit()
        return CardVerifyResponse(valid=False, message="卡密已过期")
        
    return CardVerifyResponse(
        valid=True, 
        message="验证成功",
        card_type=card.card_type
    )

@router.post("/{card_id}/revoke")
async def revoke_card(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(deps.get_current_user)
):
    result = await db.execute(select(CardCode).filter(CardCode.id == card_id))
    card = result.scalars().first()
    
    if not card:
        raise HTTPException(status_code=404, detail="卡密不存在")
    
    if card.status != 0:
        raise HTTPException(status_code=400, detail="只有未使用的卡密可以作废")
    
    card.status = 3 # 3: 已作废
    await db.commit()
    return {"message": "卡密已成功作废"}
