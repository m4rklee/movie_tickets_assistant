CREATE TABLE IF NOT EXISTS movie_tickets (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    movie_name VARCHAR(100) COMMENT '电影名称',
    movie_time INT COMMENT '电影时长',
    ticket_date DATETIME COMMENT '观看日期',
    start_time TIME COMMENT '开始时间',
    end_time TIME COMMENT '结束时间',
    movie_duration INT COMMENT '电影时长（分钟）',
    price DECIMAL(10, 2) COMMENT '电影票价',
    cinema_name VARCHAR(255) COMMENT '影院名称',
    cinema_address VARCHAR(255) COMMENT '影院地址',
    cinema_hall VARCHAR(255) COMMENT '影厅',
    seat_row INT COMMENT '座位排号',
    seat_col INT COMMENT '座位座号',
    raw_text TEXT COMMENT '大模型原始识别结果',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
);
