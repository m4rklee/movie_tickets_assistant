CREATE DATABASE IF NOT EXISTS filmarchive_wallet
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE filmarchive_wallet;

CREATE TABLE IF NOT EXISTS ticket_drafts (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  ticket_type ENUM('electronic', 'paper') NOT NULL,
  extract_json JSON NOT NULL,
  image_path VARCHAR(500) NULL,
  expires_at DATETIME NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_drafts_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS movie_tickets (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  ticket_type ENUM('electronic', 'paper') NOT NULL,
  movie_title VARCHAR(200) NOT NULL,
  show_date DATE NOT NULL,
  show_time TIME NULL COMMENT 'electronic only',
  cinema_name VARCHAR(200) NULL,
  cinema_address VARCHAR(500) NULL,
  hall_name VARCHAR(100) NULL,
  seat_info VARCHAR(50) NULL,
  price DECIMAL(10, 2) NULL,
  payment_status VARCHAR(50) NULL,
  image_path VARCHAR(500) NULL,
  raw_extract_json JSON NULL,
  confirm_status ENUM('pending', 'confirmed') NOT NULL DEFAULT 'confirmed',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_dedup (
    ticket_type,
    movie_title,
    show_date,
    hall_name,
    seat_info,
    show_time
  ),
  INDEX idx_tickets_show_date (show_date),
  INDEX idx_tickets_movie (movie_title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
