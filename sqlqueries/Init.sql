CREATE TABLE IF NOT EXISTS athletes (
    athlete_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL, -- Added for login
    password VARCHAR(255) NOT NULL,        -- Added for login
    role ENUM('admin', 'user', 'owner') DEFAULT 'user', -- Added for permissions
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
),
(
    'Rens Joshua Serrano', 
    'Arrrjiiiiiii', 
    'Provides the System Title', 
    'DSA student from Alicia Isabela.', 
    '/static/members/renz.png', 
    NULL, 
    'https://www.facebook.com/Arrrjiiiiiii', 
    '#c588ff' -- Violet
),
(
    'Seb Salamatin', 
    'sebastiengabriel.buenosalamatin#', 
    'Low Cortisol Member', 
    'not provided.', 
    '/static/members/seb.jpg', 
    NULL, 
    'https://www.facebook.com/sebastiengabriel.buenosalamatin#', 
    '#ffffff'
),
(
    'Jl Imperial', 
    'jhae.elle12', 
    'Tester', 
    'Not provided.', 
    '/static/members/jl.jpg', 
    NULL, 
    'https://www.facebook.com/jhae.elle12', 
    '#00ffff'
);

insert INTO athletes (
    username,
    password,
    role,
    name,
    age,
    sex,
    weight,
    height
)
VALUES (
    "admin",
    "admin",
    "admin",
    "name admin",
    9999,
    "Female",
    999.00,
    999.00
)
