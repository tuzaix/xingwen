
CREATE DATABASE `xingwen` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `xingwen`;

CREATE TABLE if not exists `admin_roles`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `permissions` json NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_name` (`role_name`),
  KEY `ix_admin_roles_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE if not exists `admin_users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `real_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role_id` int DEFAULT NULL,
  `status` smallint DEFAULT NULL,
  `last_login_at` datetime DEFAULT NULL,
  `last_login_ip` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_admin_users_username` (`username`),
  KEY `role_id` (`role_id`),
  KEY `ix_admin_users_id` (`id`),
  KEY `idx_admin_status` (`status`),
  CONSTRAINT `admin_users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `admin_roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE if not exists `alembic_version`  (
  `version_num` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE if not exists `card_codes`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `card_code` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `card_secret` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `batch_no` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `card_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_times` int DEFAULT NULL,
  `remain_times` int DEFAULT NULL,
  `status` smallint DEFAULT NULL,
  `expire_at` datetime NOT NULL,
  `used_at` datetime DEFAULT NULL,
  `used_by` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `channel` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_card_codes_card_code` (`card_code`),
  KEY `created_by` (`created_by`),
  KEY `ix_card_codes_batch_no` (`batch_no`),
  KEY `ix_card_codes_channel` (`channel`),
  KEY `ix_card_codes_id` (`id`),
  KEY `idx_cards_expire_status` (`expire_at`,`status`),
  KEY `idx_cards_batch_status` (`batch_no`,`status`),
  CONSTRAINT `card_codes_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `admin_users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE if not exists `operation_logs`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `admin_id` int DEFAULT NULL,
  `operation_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `operation_module` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `request_params` json DEFAULT NULL,
  `ip_address` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_operation_logs_id` (`id`),
  KEY `idx_logs_admin_time` (`admin_id`,`created_at` DESC),
  CONSTRAINT `operation_logs_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `admin_users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE if not exists `reports`  (
  `id` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gender` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `birthday` datetime DEFAULT NULL,
  `focus_area` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `left_hand_image` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `right_hand_image` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `card_code` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `model_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `content` text COLLATE utf8mb4_unicode_ci,
  `status` smallint DEFAULT NULL,
  `progress` int DEFAULT '0',
  `progress_desc` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `error_msg` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `generation_time` float DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  `palm_features` json DEFAULT NULL,
  `location` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mbti` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `calendar_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `zodiac` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bazi` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '生辰八字信息',
  `bazi_favorable_elements` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '八字五行喜用神/分布',
  `sections` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_reports_id` (`id`),
  KEY `ix_reports_user_id` (`user_id`),
  KEY `idx_reports_user_id` (`user_id`),
  KEY `idx_reports_status_created` (`status`,`created_at` DESC),
  KEY `idx_reports_card_code` (`card_code`),
  CONSTRAINT `reports_ibfk_1` FOREIGN KEY (`card_code`) REFERENCES `card_codes` (`card_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE if not exists `system_configs`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `config_key` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `config_value` text COLLATE utf8mb4_unicode_ci,
  `config_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_encrypted` smallint DEFAULT NULL,
  `updated_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_system_configs_config_key` (`config_key`),
  UNIQUE KEY `idx_configs_key` (`config_key`),
  KEY `updated_by` (`updated_by`),
  KEY `ix_system_configs_id` (`id`),
  CONSTRAINT `system_configs_ibfk_1` FOREIGN KEY (`updated_by`) REFERENCES `admin_users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;