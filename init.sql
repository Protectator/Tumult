DROP USER 'tumult'@'%';
CREATE USER 'tumult'@'%' IDENTIFIED BY 'tumult-tumult';
CREATE DATABASE IF NOT EXISTS `tumult`;
GRANT ALL PRIVILEGES ON tumult.* TO 'tumult'@'%';
FLUSH PRIVILEGES ;

CREATE TABLE `messages` (
  `id` varchar(65) NOT NULL,
  `guild_id` varchar(65) NOT NULL,
  `channel_id` varchar(65) NOT NULL,
  `author_id` varchar(65) NOT NULL,
  `content` varchar(2000) NOT NULL,
  `timestamp` timestamp NOT NULL,
  `author_username` varchar(40) NOT NULL,
  `author_discriminator` smallint(5) UNSIGNED NOT NULL,
  `avatar` varchar(65) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `guild_id` (`guild_id`),
  ADD KEY `channel_id` (`channel_id`);