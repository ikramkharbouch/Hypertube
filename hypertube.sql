CREATE DATABASE IF NOT EXISTS `db_hypertube` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `db_hypertube`;

CREATE TABLE IF NOT EXISTS `accounts` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`firstname` varchar(50) NOT NULL,
	`lastname` varchar(50) NOT NULL,
  	`username` varchar(50) NOT NULL,
	`email` varchar(100) NOT NULL,
  	`password` varchar(255) NOT NULL,
	`token` varchar(500) NOT NULL,
	`validation` int(11) NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS `profiles` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`username` varchar(50) NOT NULL,
	`gender` varchar(50) NOT NULL,
	`preference` varchar(50) NOT NULL,
  	`bio` varchar(700) NOT NULL,
	`age` int(20) NOT NULL,
	`hashtag` varchar(700) NOT NULL,
	`lat` varchar(255) NOT NULL,
	`lon` varchar(255) NOT NULL,
	`profile_pic` varchar(755) NOT NULL,
	`img1` varchar(755) NOT NULL,
	`img2` varchar(755) NOT NULL,
	`img3` varchar(755) NOT NULL,
	`img4` varchar(755) NOT NULL,
	`score` int (200) NOT NULL,
  	`status` varchar(50) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `likes` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`id_liker` int(50) NOT NULL,
	`id_liked` int(50) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;



CREATE TABLE IF NOT EXISTS `blocks` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`id_blocker` int(50) NOT NULL,
	`id_blocked` int(50) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `reports` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`id_reporter` int(50) NOT NULL,
	`id_reported` int(50) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS `notification` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`type`  varchar(50) NOT NULL,
	`id_notifier` int(50) NOT NULL,
	`notifier`  varchar(50) NOT NULL,
	`id_notified` int(50) NOT NULL,
	`notified`  varchar(50) NOT NULL,
	`time`  varchar(50) NOT NULL,
	`vue` int(11) NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `chat` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`user1` int(50) NOT NULL,
	`user2` int(50) NOT NULL,
	`sender`  int(50) NOT NULL,
	`msg` varchar(500) NOT NULL,
	`time`  varchar(50) NOT NULL,
	`vue` int(11) NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;


 