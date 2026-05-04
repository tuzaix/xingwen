from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db.session import get_db
from app.models.report import Report
from app.models.card import CardCode
from app.api import deps
from app.core.config import settings
from datetime import datetime, timedelta, date
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/config")
async def get_system_config():
    logger.info("Public config requested")
    return {
        "ai_model": settings.AI_MODEL,
        "project_name": settings.PROJECT_NAME
    }

@router.get("/summary")
async def get_stats_summary(
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(deps.get_current_user)
):
    try:
        logger.info(f"Summary stats requested by {current_admin.username}")
        print(f"DEBUG: Summary stats requested by {current_admin.username}")
        today = date.today()
        start_of_today = datetime.combine(today, datetime.min.time())

        # Today DAU
        print("DEBUG: Fetching DAU...")
        dau_result = await db.execute(
            select(func.count(func.distinct(Report.user_id)))
            .filter(Report.created_at >= start_of_today)
        )
        dau = dau_result.scalar() or 0
        print(f"DEBUG: DAU={dau}")

        # Today Card Verifications
        print("DEBUG: Fetching card verifications...")
        card_verifications_result = await db.execute(
            select(func.count(CardCode.id))
            .filter(and_(CardCode.status == 1, CardCode.used_at >= start_of_today))
        )
        card_verifications = card_verifications_result.scalar() or 0
        print(f"DEBUG: CardVer={card_verifications}")

        # Total Reports
        print("DEBUG: Fetching total reports...")
        total_reports_result = await db.execute(select(func.count(Report.id)))
        total_reports = total_reports_result.scalar() or 0
        print(f"DEBUG: TotalReports={total_reports}")

        # Failed Reports
        print("DEBUG: Fetching failed reports...")
        failed_reports_result = await db.execute(
            select(func.count(Report.id)).filter(Report.status == 2)
        )
        failed_reports = failed_reports_result.scalar() or 0
        print(f"DEBUG: FailedReports={failed_reports}")

        return {
            "dau": dau,
            "card_verifications": card_verifications,
            "total_reports": total_reports,
            "failed_reports": failed_reports
        }
    except Exception as e:
        print(f"DEBUG ERROR in get_stats_summary: {e}")
        logger.error(f"Error in get_stats_summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trend")
async def get_report_trend(
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(deps.get_current_user)
):
    try:
        logger.info(f"Trend stats requested by {current_admin.username}")
        # Last 7 days trend
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        start_time = datetime.combine(start_date, datetime.min.time())
        
        # Efficient single query for trend
        result = await db.execute(
            select(
                func.date(Report.created_at).label("date"),
                func.count(Report.id).label("count")
            )
            .filter(Report.created_at >= start_time)
            .group_by(func.date(Report.created_at))
            .order_by(func.date(Report.created_at))
        )
        
        rows = result.all()
        trend_map = {row[0].strftime("%m-%d") if hasattr(row[0], 'strftime') else str(row[0]): row[1] for row in rows}
        
        trend_data = []
        for i in range(7):
            current_day = start_date + timedelta(days=i)
            day_str = current_day.strftime("%m-%d")
            trend_data.append({
                "date": day_str,
                "count": trend_map.get(day_str, 0)
            })
            
        return trend_data
    except Exception as e:
        logger.error(f"Error in get_report_trend: {e}", exc_info=True)
        # Return empty list instead of 500 to keep UI working
        return []

@router.get("/distribution")
async def get_distribution(
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(deps.get_current_user)
):
    try:
        logger.info(f"Distribution stats requested by {current_admin.username}")
        # Card type distribution
        result = await db.execute(
            select(CardCode.card_type, func.count(CardCode.id))
            .group_by(CardCode.card_type)
        )
        distribution = [{"name": row[0], "value": row[1]} for row in result.all()]
        
        return distribution
    except Exception as e:
        logger.error(f"Error in get_distribution: {e}", exc_info=True)
        return []
