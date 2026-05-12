-- 1. USER & PRODUCT MANAGEMENT
-- Repurposed from 'athletes'
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,

    username VARCHAR(100) UNIQUE NOT NULL,

    password VARCHAR(255) NOT NULL,  -- hashed password

    full_name VARCHAR(100) NOT NULL,

    role ENUM('staff', 'admin', 'owner') DEFAULT 'staff',

    department VARCHAR(100) DEFAULT NULL,

    annual_salary DECIMAL(12,2) DEFAULT 0,

    hire_date DATE DEFAULT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- The core of the system
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    sku_code VARCHAR(50) UNIQUE NOT NULL, -- "Stock Keeping Unit"
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    unit_price DECIMAL(10,2) NOT NULL,
    current_stock INT DEFAULT 0,
    min_stock_level INT DEFAULT 10, -- THE "SMART" FEATURE: Reorder point
    supplier_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. STOCK MOVEMENTS (Repurposed from 'nutrition_logs' / 'training_sessions')
-- Tracks every time items come in or go out
CREATE TABLE IF NOT EXISTS inventory_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    user_id INT NOT NULL, -- Who performed the action?
    transaction_type ENUM('IN', 'OUT', 'ADJUSTMENT') NOT NULL,
    quantity INT NOT NULL,
    reason VARCHAR(255), -- e.g., "Customer Sale", "Restock", "Damaged Goods"
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 3. SALES & REVENUE (Repurposed from 'goals')
-- This is what business owners look at
CREATE TABLE IF NOT EXISTS sales_analytics (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity_sold INT NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    sale_date DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 4. SUPPLIER MANAGEMENT
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(100),
    lead_time_days INT -- How many days it takes for stock to arrive
);

CREATE TABLE IF NOT EXISTS product_stats (
    product_id INT PRIMARY KEY,

    total_in INT DEFAULT 0,
    total_out INT DEFAULT 0,

    revenue DECIMAL(12,2) DEFAULT 0.00,

    stock_in_value DECIMAL(12,2) DEFAULT 0.00,

    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Keep your team_members table exactly as it is for your "About Us" page!
CREATE TABLE IF NOT EXISTS team_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50),
    role VARCHAR(100),
    about_me TEXT,
    profile_image_path VARCHAR(255),
    github_link VARCHAR(255),
    facebook_link VARCHAR(255),
    accent_color VARCHAR(7) DEFAULT '#10b981' -- Emerald green default
);


CREATE TABLE if not exists system_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    event VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS history_logs (
    history_id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    action_type VARCHAR(50) NOT NULL,

    description TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE
);


TRUNCATE TABLE team_members;

INSERT INTO team_members 
(full_name, username, role, about_me, profile_image_path, github_link, facebook_link, accent_color)
VALUES 
(
    'Cyrus Troy Bazar', 
    'Alieelinux', 
    'Backend, Frontend, almost Everything', 
    'An Ilocano student living in the holy lands of Isabela, currently attending at Isabela State University. Specialized in Backend development and System Architecture.', 
    'https://media1.tenor.com/m/n6zppmoEdZUAAAAC/koishi-koishi-happy-love.gif', 
    'https://github.com/Alieelinux', 
    'https://www.facebook.com/KoishiKomeiji0', 
    '#ff00ea' -- Pink
)

insert into users (
    "owner",
    "owner",
    'admin',
    "I'm the owner",
)