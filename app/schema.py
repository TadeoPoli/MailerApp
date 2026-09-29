instructions = [
    """
      CREATE TABLE IF NOT EXISTS email (
         id INT PRIMARY KEY AUTO_INCREMENT,
         email VARCHAR(254) NOT NULL,
         subject VARCHAR(200) NOT NULL,
         content TEXT NOT NULL,
         created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
         INDEX idx_email_created_at (created_at)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
]
