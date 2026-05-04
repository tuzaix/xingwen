import uuid
import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.db.session import get_db, AsyncSessionLocal
from app.models.report import Report
from app.models.card import CardCode
from app.schemas.report import ReportCreate, ReportResponse, ReportListResponse
from app.services.ai_agent import ReportCoordinator
from app.services.pdf_service import generate_report_pdf
from app.api import deps
from app.core.config import settings
from datetime import datetime
from typing import Optional, List
from fastapi import Query
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
coordinator = ReportCoordinator()

@router.get("/", response_model=ReportListResponse)
async def list_reports(
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(deps.get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = None,
    status: Optional[int] = None
):
    query = select(Report)
    if user_id:
        query = query.filter(Report.user_id == user_id)
    if status is not None:
        query = query.filter(Report.status == status)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    result = await db.execute(
        query.order_by(Report.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    reports = result.scalars().all()
    
    return {
        "total": total,
        "items": reports,
        "page": page,
        "page_size": page_size
    }

async def generate_report_task(report_id: str):
    async with AsyncSessionLocal() as db_session:
        try:
            # 1. 获取报告信息
            result = await db_session.execute(select(Report).filter(Report.id == report_id))
            report = result.scalars().first()
            if not report:
                return

            start_time = datetime.now()

            # 2. 第一步：解析掌纹特征（如果尚未解析）
            if not report.palm_features:
                # 更新进度：10% - 正在读取手相图片
                report.progress = 10
                report.progress_desc = "正在读取手相图片..."
                await db_session.commit()

                # 获取后端根目录 (backend/api)
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
                
                # 图片现在只存储文件名，路径需要手动拼接
                left_abs_path = os.path.join(base_dir, "uploads", "images", report.left_hand_image)
                right_abs_path = os.path.join(base_dir, "uploads", "images", report.right_hand_image)

                # 更新进度：20% - 正在通过星纹 AI 提取掌纹特征
                report.progress = 20
                report.progress_desc = "正在通过星纹 AI 提取掌纹特征..."
                await db_session.commit()
                
                # 调用 Vision Agent 提取特征
                palm_features = await coordinator.extract_palm_features(left_abs_path, right_abs_path)
                
                # 立即存入数据库，避免后续失败导致需要重新解析
                report.palm_features = palm_features
                report.progress = 50
                report.progress_desc = "掌纹特征解析完成，准备生成命理报告..."
                await db_session.commit()
                await db_session.refresh(report)
            else:
                palm_features = report.palm_features

            # 3. 第二步：生成命理报告
            report.progress = 60
            report.progress_desc = "星辰轨迹对齐中，正在生成深度解析报告..."
            await db_session.commit()

            # 计算八字
            from lunar_python import Solar, Lunar
            
            bazi_string = "未知"
            bazi_favorable_elements = "根据八字自动推演"
            
            if report.birthday:
                dt = report.birthday
                if report.calendar_type == "lunar":
                    # 假设输入的日期是农历
                    lunar = Lunar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                    solar = lunar.getSolar()
                else:
                    # 默认公历
                    solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                
                eight_char = solar.getLunar().getEightChar()
                bazi_string = f"{eight_char.getYear()}年 {eight_char.getMonth()}月 {eight_char.getDay()}日 {eight_char.getTime()}时"
                
                # 简单推演喜用神（这里可以使用库提供的五行分析，或者让 AI 深度分析）
                # 为了更专业，我们可以提供五行强度
                vocal = solar.getLunar().getEightChar()
                bazi_favorable_elements = f"五行分布：{vocal.getYearWuXing()} {vocal.getMonthWuXing()} {vocal.getDayWuXing()} {vocal.getTimeWuXing()}"
                
                # 保存计算出的八字信息到数据库
                report.bazi = bazi_string
                report.bazi_favorable_elements = bazi_favorable_elements

            # 准备用户信息供 AI 使用
            # 如果秒数为 1，说明是我们在 create_report 中标记的“时间未知”
            birthday_str = "未知"
            if report.birthday:
                if report.birthday.second == 1:
                    birthday_str = report.birthday.strftime("%Y-%m-%d (出生时间未知)")
                else:
                    birthday_str = report.birthday.strftime("%Y-%m-%d %H:%M")

            user_info = {
                "name": report.user_name,
                "gender": report.gender,
                "birthday": birthday_str,
                "focus_area": report.focus_area,
                "location": report.location or "未知",
                "mbti": report.mbti or "未知",
                "zodiac": report.zodiac or "未知",
                "bazi": bazi_string,
                "bazi_favorable_elements": bazi_favorable_elements
            }
            logger.info(f"report.birthday: {report.birthday}")
            logger.info(f"user_info: {user_info}")

            raise Exception("调试用")

            sections = await coordinator.generate_astrology_report(user_info, palm_features)
            end_time = datetime.now()

            # 4. 更新报告状态
            # 同时保存结构化数据和纯文本内容（兼容旧版或简单展示）
            report.sections = sections
            # 适配新的 JSON 结构：s['chapter_title'] 和 s['paragraphs']
            report.content = "\n\n".join([
                f"## {s.get('chapter_title', '未知章节')}\n\n" + "\n\n".join(s.get('paragraphs', []))
                for s in sections
            ])
            report.status = 1  # 已完成
            report.progress = 100
            report.progress_desc = "报告生成完成"
            report.model_name = settings.AI_MODEL
            report.generation_time = (end_time - start_time).total_seconds()
            
            await db_session.commit()
        except Exception as e:
            print(f"Report Generation Task Error: {e}")
            # 更新状态为失败
            await db_session.execute(
                update(Report)
                .where(Report.id == report_id)
                .values(status=2, error_msg=str(e))
            )
            await db_session.commit()

@router.post("/generate", response_model=ReportResponse)
async def create_report(
    data: ReportCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    print(f"Generating report for: {data.name}, card: {data.card_code}")
    # 0. Check images
    if not data.left_hand_image or not data.right_hand_image:
        print("Error: Missing images")
        raise HTTPException(status_code=400, detail="Missing palm images")

    # 1. Verify Card (Safety check)
    clean_card_code = data.card_code.replace("-", "").upper()
    print(f"Cleaned card code: {clean_card_code}")
    
    card_result = await db.execute(
        select(CardCode).filter(CardCode.card_code == clean_card_code)
    )
    card = card_result.scalars().first()
    if not card:
        print(f"Error: Card not found: {clean_card_code}")
        raise HTTPException(status_code=400, detail="Invalid card code")
    
    if card.status != 0:
        print(f"Error: Card status is {card.status}")
        raise HTTPException(status_code=400, detail="Card already used or invalid")

    # 2. Create initial report record
    report_id = str(uuid.uuid4()).replace("-", "")
    print(f"Creating report record with ID: {report_id}")
    
    # Try parsing birthday with or without time
    birthday_dt = None
    if data.birthday:
        # 先去除前后空格，防止 "2024-05-05 " 导致解析失败
        clean_birthday = data.birthday.strip()
        try:
            # 尝试解析包含时间的格式
            birthday_dt = datetime.strptime(clean_birthday, "%Y-%m-%d %H:%M")
        except ValueError:
            try:
                # 尝试解析仅包含日期的格式
                birthday_dt = datetime.strptime(clean_birthday, "%Y-%m-%d")
                # 如果只有日期，按照约定设置为正午 12:00
                # 我们设置 second=1 作为内部标记，表示“用户未提供具体时间”
                birthday_dt = birthday_dt.replace(hour=12, minute=0, second=1)
            except ValueError:
                birthday_dt = None
    
    print(f"Parsed birthday: {birthday_dt}")

    try:
        new_report = Report(
            id=report_id,
            user_id=f"user_{uuid.uuid4().hex[:8]}",
            user_name=data.name,
            gender=data.gender,
            birthday=birthday_dt,
            focus_area=data.focus_area,
            location=data.location,
            mbti=data.mbti,
            calendar_type=data.calendar_type,
            zodiac=data.zodiac,
            bazi=data.bazi,
            bazi_favorable_elements=data.bazi_favorable_elements,
            left_hand_image=data.left_hand_image,
            right_hand_image=data.right_hand_image,
            card_code=card.card_code,
            status=0, # Generating
            progress=0,
            progress_desc="等待启动解析..."
        )
        db.add(new_report)

        # 3. Mark card as used
        card.status = 1
        card.used_at = datetime.now()
        card.used_by = new_report.user_id

        print("Committing to database...")
        await db.commit()
        print("Commit successful. Refreshing...")
        await db.refresh(new_report)
        print("Refresh successful.")

        # 4. Run AI generation in background
        background_tasks.add_task(generate_report_task, report_id)
        print("Background task added.")

        return new_report
    except Exception as e:
        print(f"Database Error in create_report: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Report).filter(Report.id == report_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.post("/{report_id}/regenerate", response_model=ReportResponse)
async def regenerate_report(
    report_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(deps.get_current_user)
):
    result = await db.execute(select(Report).filter(Report.id == report_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Update status to generating
    report.status = 0
    report.error_msg = None
    report.progress = 0
    report.progress_desc = "重新启动解析..."
    
    await db.commit()
    await db.refresh(report)
    
    # Start task
    background_tasks.add_task(generate_report_task, report_id)
    
    return report

@router.get("/{report_id}/pdf")
async def download_report_pdf(
    report_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Report).filter(Report.id == report_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.status != 1:
        raise HTTPException(status_code=400, detail="Report is not completed yet")

    try:
        from fastapi.responses import StreamingResponse
        import urllib.parse
        
        # 处理生日显示，识别“时间未知”标记
        birthday_str = "未知"
        if report.birthday:
            if report.birthday.second == 1:
                birthday_str = report.birthday.strftime("%Y-%m-%d (时间未知)")
            else:
                birthday_str = report.birthday.strftime("%Y-%m-%d %H:%M")

        report_data = {
            "user_name": report.user_name,
            "gender": report.gender,
            "birthday": birthday_str,
            "focus_area": report.focus_area,
            "bazi": report.bazi,
            "bazi_favorable_elements": report.bazi_favorable_elements,
            "sections": report.sections,
            "content": report.content
        }
        
        pdf_file = generate_report_pdf(report_data)
        
        filename = f"星纹报告_{report.user_name}_{report_id[:8]}.pdf"
        encoded_filename = urllib.parse.quote(filename)
        
        return StreamingResponse(
            pdf_file,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
    except Exception as e:
        logger.error(f"PDF Download Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@router.get("/export/csv")
async def export_reports_csv(
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(deps.get_current_user_from_query)
):
    result = await db.execute(select(Report).order_by(Report.created_at.desc()))
    reports = result.scalars().all()
    
    import io
    import csv
    from fastapi.responses import StreamingResponse
    
    output = io.StringIO()
    # Add BOM for Excel
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow(['ID', '姓名', '性别', '生日', '诉求', '卡密', '状态', '耗时(s)', '模型', '创建时间'])
    
    status_map = {0: '生成中', 1: '已完成', 2: '失败'}
    
    for r in reports:
        writer.writerow([
            r.id,
            r.user_name,
            r.gender,
            r.birthday.strftime('%Y-%m-%d %H:%M') if r.birthday else '-',
            r.focus_area,
            r.card_code,
            status_map.get(r.status, '未知'),
            f"{r.generation_time:.1f}" if r.generation_time else '-',
            r.model_name or '-',
            r.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=reports_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"}
    )

@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(deps.get_current_user)
):
    result = await db.execute(select(Report).filter(Report.id == report_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    await db.delete(report)
    await db.commit()
    return {"message": "Report deleted successfully"}
