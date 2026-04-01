"""Log service — auto-log all actions to change_log table with VN timezone."""

from datetime import datetime, timezone, timedelta
from database.db import get_db

VN_TZ = timezone(timedelta(hours=7))


def _vn_now():
    """Get current time in VN timezone as string."""
    return datetime.now(VN_TZ).strftime('%Y-%m-%d %H:%M:%S')


def _utc_to_vn(ts_str):
    """Convert UTC timestamp to VN display string."""
    if not ts_str:
        return ''
    try:
        dt = datetime.strptime(str(ts_str), '%Y-%m-%d %H:%M:%S')
        dt = dt.replace(tzinfo=timezone.utc).astimezone(VN_TZ)
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    except (ValueError, TypeError):
        return str(ts_str)


def add_log(action_type, detail, customer_id=None, customer_name=None, operator='Dương'):
    """Insert a log entry with VN timestamp."""
    conn = get_db()
    conn.execute(
        """INSERT INTO change_log (timestamp, action_type, detail, customer_id, customer_name, operator)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (_vn_now(), action_type, detail, customer_id, customer_name, operator)
    )
    conn.commit()
    conn.close()


def get_logs(action_type=None, customer_id=None, page=1, per_page=50):
    """Get logs with optional filters and pagination."""
    conn = get_db()
    query = "SELECT * FROM change_log WHERE 1=1"
    params = []

    if action_type:
        query += " AND action_type = ?"
        params.append(action_type)
    if customer_id:
        query += " AND customer_id = ?"
        params.append(customer_id)

    # Count total
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    total = conn.execute(count_query, params).fetchone()[0]

    # Paginate
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])

    rows = conn.execute(query, params).fetchall()
    conn.close()

    logs = []
    for r in rows:
        d = dict(r)
        # Convert timestamp to VN display format
        ts = d.get('timestamp', '')
        if ts:
            try:
                dt = datetime.strptime(str(ts), '%Y-%m-%d %H:%M:%S')
                # If timestamp is before we switched to VN (entries before ~14:30 VN on 2026-03-30),
                # treat as UTC and convert. Otherwise it's already VN time.
                if dt.year == 2026 and dt.month == 3 and dt.day == 30 and dt.hour < 8:
                    # Old UTC entry — convert to VN
                    dt = dt.replace(tzinfo=timezone.utc).astimezone(VN_TZ)
                d['timestamp'] = dt.strftime('%d/%m/%Y %H:%M:%S')
            except (ValueError, TypeError):
                pass
        logs.append(d)

    return {
        'logs': logs,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }
