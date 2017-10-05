SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

CREATE TABLE `accounts` (
  `id` int(11) NOT NULL,
  `host` varchar(100) NOT NULL,
  `ssl` tinyint(1) NOT NULL,
  `login` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `last_checked` int(11) NOT NULL,
  `check_interval` int(11) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `in_work` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `accounts_errors` (
  `id` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  `error` varchar(200) NOT NULL,
  `when_add` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `attachments` (
  `id` int(11) NOT NULL,
  `letter_id` int(11) NOT NULL,
  `file_name` varchar(100) NOT NULL,
  `mime_type` varchar(50) NOT NULL,
  `ext` varchar(10) NOT NULL,
  `hash` varchar(32) NOT NULL,
  `size` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `filters` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `target` enum('subject','content','from','to','attachment') NOT NULL,
  `type` enum('str','regex') NOT NULL,
  `content` varchar(255) NOT NULL,
  `new` tinyint(1) NOT NULL DEFAULT '1',
  `when_add` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `filters_finds` (
  `filter_id` int(11) NOT NULL,
  `letter_id` int(11) NOT NULL,
  `when_add` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `folders` (
  `id` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  `parent_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `full_name` varchar(200) NOT NULL,
  `server_name` varchar(200) NOT NULL,
  `last_updated` int(11) NOT NULL,
  `last_checked` int(11) NOT NULL DEFAULT '0',
  `removed` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `letters` (
  `id` int(11) NOT NULL,
  `uid` int(11) NOT NULL,
  `hash` varchar(32) NOT NULL,
  `folder_id` int(11) NOT NULL,
  `subject` varchar(255) NOT NULL,
  `from_name` varchar(100) NOT NULL,
  `from_mail` varchar(100) NOT NULL,
  `to_name` varchar(100) NOT NULL,
  `to_mail` varchar(100) NOT NULL,
  `has_attachments` tinyint(1) NOT NULL,
  `date` int(11) NOT NULL,
  `when_add` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

 
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `host` (`host`,`login`);

 
ALTER TABLE `accounts_errors`
  ADD PRIMARY KEY (`id`),
  ADD KEY `account_id` (`account_id`);

 
ALTER TABLE `attachments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `letter_id` (`letter_id`);

 
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

 
ALTER TABLE `filters`
  ADD PRIMARY KEY (`id`);

 
ALTER TABLE `filters_finds`
  ADD PRIMARY KEY (`filter_id`,`letter_id`),
  ADD KEY `when_add` (`when_add`);

 
ALTER TABLE `folders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `parent_id` (`parent_id`);

 
ALTER TABLE `letters`
  ADD PRIMARY KEY (`id`),
  ADD KEY `folder_id` (`folder_id`);

 

 
ALTER TABLE `accounts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=0;
 
ALTER TABLE `accounts_errors`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=0;
 
ALTER TABLE `attachments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=0;

ALTER TABLE `django_migrations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
 
ALTER TABLE `filters`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=0;
 
ALTER TABLE `folders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=0;
 
ALTER TABLE `letters`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=0;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
