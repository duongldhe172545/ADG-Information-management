-- Customers table: 19 original columns + scoring + metadata
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- 10 cột gốc từ file anh Cường
    loai_kh TEXT,
    ten_cong_ty TEXT,
    ho_ten TEXT,
    sdt TEXT,
    tinh TEXT,
    quan_huyen TEXT,
    dia_chi TEXT,
    nguon TEXT,
    thong_tin_chi_tiet TEXT,
    khu_vuc TEXT,

    -- 9 trường scoring input
    so_kh_quay_lai INTEGER,
    biet_loi_nhuan TEXT,
    doi_tho TEXT,
    chinh_sach_bh TEXT,
    muc_quan_tam TEXT,
    ban_kinh_km INTEGER,
    quan_ly_data TEXT,
    kiem_soat_mua_hang TEXT,
    so_nguoi_gioi_thieu INTEGER,

    -- Scoring output (tự tính)
    c1 INTEGER DEFAULT 0,
    c2 INTEGER DEFAULT 0,
    c3 INTEGER DEFAULT 0,
    c4 INTEGER DEFAULT 0,
    c5 INTEGER DEFAULT 0,
    c6 INTEGER DEFAULT 0,
    c7 INTEGER DEFAULT 0,
    c8 INTEGER DEFAULT 0,
    c9 INTEGER DEFAULT 0,
    c_score INTEGER DEFAULT 0,
    tier TEXT DEFAULT '',

    -- Metadata
    review_status TEXT DEFAULT 'ok',  -- 'ok' / 'needs_review'
    is_deleted INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Scoring weights
CREATE TABLE IF NOT EXISTS scoring_weights (
    c_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    weight REAL NOT NULL
);

-- Change log
CREATE TABLE IF NOT EXISTS change_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action_type TEXT NOT NULL,
    detail TEXT,
    customer_id INTEGER,
    customer_name TEXT,
    operator TEXT DEFAULT 'Dương'
);

-- Custom columns
CREATE TABLE IF NOT EXISTS custom_columns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    column_name TEXT NOT NULL UNIQUE,
    is_visible INTEGER DEFAULT 1
);

-- Column visibility (for built-in columns)
CREATE TABLE IF NOT EXISTS column_settings (
    column_key TEXT PRIMARY KEY,
    is_visible INTEGER DEFAULT 1
);

-- Default scoring weights
INSERT OR IGNORE INTO scoring_weights (c_id, name, weight) VALUES
    ('C1', 'Sở hữu KH bền vững', 0.20),
    ('C2', 'P&L độc lập', 0.15),
    ('C3', 'Quản lý đội thi công', 0.15),
    ('C4', 'Trách nhiệm cuối', 0.15),
    ('C5', 'Động lực tham gia', 0.10),
    ('C6', 'Kiểm soát địa bàn', 0.10),
    ('C7', 'Kỷ luật data', 0.08),
    ('C8', 'Chuỗi cung ứng', 0.04),
    ('C9', 'Ảnh hưởng cộng đồng', 0.03);
