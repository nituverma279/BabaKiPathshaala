-- -------------------------------------------------------------
-- TablePlus 3.12.2(358)
--
-- https://tableplus.com/
--
-- Database: bkp
-- Generation Time: 2021-02-22 23:36:17.0910
-- -------------------------------------------------------------


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


CREATE TABLE `bkp_psychologist` (
  `psy_id` int NOT NULL,
  `psy_name` varchar(255) DEFAULT NULL,
  `psy_details` varchar(2550) DEFAULT NULL,
  `mail_id` varchar(255) NOT NULL,
  `psy_whatsapp` varchar(255) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `intro_url` varchar(1775) DEFAULT NULL,
  `DOJ` date DEFAULT NULL,
  PRIMARY KEY (`psy_id`,`mail_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `bkp_psychologist` (`psy_id`, `psy_name`, `psy_details`, `mail_id`, `psy_whatsapp`, `active`, `intro_url`, `DOJ`) VALUES
('1', 'Nitu', 'MBBS from Pune', 'nitu@gmail.com', '1234567890', '1', 'https://www.youtube.com/watch?v=tO7k5U2Zl4o', '2021-02-09'),
('2', 'Nitu', 'MBBS from Pune', 'verma@gmail.com', '1234567890', '1', 'https://www.youtube.com/watch?v=tO7k5U2Zl4o', '2021-02-09'),
('3', 'Aditya', 'MBBS from Pune', 'aditya@gmail.com', '1234567890', '1', 'https://www.youtube.com/watch?v=tO7k5U2Zl4o', '2021-02-09'),
('4', 'Ajay', 'MBBS from Pune', 'ajay@gmail.com', '1234567890', '1', 'https://www.youtube.com/watch?v=tO7k5U2Zl4o', '2021-02-09'),
('5', 'Ajay', 'MBBS from Pune', 'ajay@gmail.com', '1234567890', '1', 'https://www.youtube.com/watch?v=tO7k5U2Zl4o', '2021-02-09'),
('6', 'Rupa', 'MBBS from Pune', 'rupa@gmail.com', '1234567890', '1', 'https://www.youtube.com/watch?v=tO7k5U2Zl4o', '2021-02-09');


/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;