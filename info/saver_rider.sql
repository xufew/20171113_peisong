/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

DROP TABLE IF EXISTS `saver_rider`;

CREATE TABLE `saver_rider` (
    `rider_id` bigint(20) NOT NULL,
    `mcx` varchar(255) DEFAULT NULL,
    `mcy` varchar(255) DEFAULT NULL,
    `aoi_id` bigint(20) DEFAULT NULL,
    `speed` double DEFAULT NULL,
    `max_load` tinyint(4) DEFAULT NULL,             # qi shi zui da qu can shu liang
    `has_load` tinyint(4) DEFAULT NULL,             # yi qu can shu liang
    `rider_status` tinyint(4) DEFAULT 0,            # qishi zhuang tai
    `min_complete` tinyint(4) DEFAULT NULL,         # zui xiao wan cheng dan liang
    `finish_complete` tinyint(4) DEFAULT NULL,      # yi wan cheng dan liang
    `mubiaox` varchar(255) DEFAULT NULL,            # mubiao di dian zuo biao x
    `mubiaoy` varchar(255) DEFAULT NULL,            # mubiao di dian zuo biao y
    PRIMARY KEY (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
