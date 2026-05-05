CREATE TABLE IF NOT EXISTS athletes (
    athlete_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL, -- Added for login
    password VARCHAR(255) NOT NULL,        -- Added for login
    role ENUM('admin', 'user') DEFAULT 'user', -- Added for permissions
    name VARCHAR(100) NOT NULL,            -- Kept separate as requested
    age INT,
    sex ENUM('Male', 'Female', 'Other'),
    weight DECIMAL(5,2),
    height DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nutrition_logs (
    nutrition_id INT AUTO_INCREMENT PRIMARY KEY,
    athlete_id INT NOT NULL,
    meal_type VARCHAR(50),
    calories INT NOT NULL,
    protein DECIMAL(5,2),
    carbs DECIMAL(5,2),
    fats DECIMAL(5,2),
    log_date DATE NOT NULL,
    FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS training_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    athlete_id INT NOT NULL,
    session_type VARCHAR(50),
    duration_minutes INT NOT NULL,
    intensity ENUM('Low', 'Medium', 'High'),
    calories_burned INT,
    session_date DATE NOT NULL,
    FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recovery_logs (
    recovery_id INT AUTO_INCREMENT PRIMARY KEY,
    athlete_id INT NOT NULL,
    sleep_hours DECIMAL(4,1), -- Increased to 4,1 just in case of precision
    soreness_level INT,
    stress_level INT,
    recovery_score INT,
    log_date DATE NOT NULL,
    FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS goals (
    goal_id INT AUTO_INCREMENT PRIMARY KEY,
    athlete_id INT NOT NULL,
    goal_type VARCHAR(50),
    target_value DECIMAL(6,2),
    current_value DECIMAL(6,2),
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    role ENUM('admin', 'user') DEFAULT 'user'
);