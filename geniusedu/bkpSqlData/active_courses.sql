-- -------------------------------------------------------------
-- TablePlus 3.12.2(358)
--
-- https://tableplus.com/
--
-- Database: bkp
-- Generation Time: 2021-02-22 23:35:16.6980
-- -------------------------------------------------------------


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


CREATE TABLE `active_courses` (
  `id` int NOT NULL,
  `course_name` varchar(128) NOT NULL,
  `section_id` varchar(128) NOT NULL,
  `course_id` varchar(100) NOT NULL,
  `field_id` varchar(100) NOT NULL,
  `educator_id` varchar(100) NOT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `language` varchar(20) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `timing` varchar(10) NOT NULL,
  `is_bkp` tinyint(1) NOT NULL,
  `course_duration` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_section_id1` (`section_id`),
  KEY `fk_course_id1` (`course_id`),
  KEY `fk_field_id1` (`field_id`),
  KEY `fk_educator_id` (`educator_id`),
  CONSTRAINT `fk_course_id1` FOREIGN KEY (`course_id`) REFERENCES `bkp_course` (`course_id`),
  CONSTRAINT `fk_educator_id` FOREIGN KEY (`educator_id`) REFERENCES `bkp_educator` (`educator_id`),
  CONSTRAINT `fk_field_id1` FOREIGN KEY (`field_id`) REFERENCES `bkp_field` (`field_id`),
  CONSTRAINT `fk_section_id1` FOREIGN KEY (`section_id`) REFERENCES `bkp_section` (`section_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `active_courses` (`id`, `course_name`, `section_id`, `course_id`, `field_id`, `educator_id`, `start_date`, `end_date`, `language`, `is_active`, `timing`, `is_bkp`, `course_duration`) VALUES
('1', 'Maths', 'A', '100', '001', '1', '2021-02-12', '2021-12-12', 'eng', '1', '10:00', '1', '1'),
('2', 'Maths', 'A', '100', '001', '1', '2021-02-18', '2021-12-12', 'eng', '1', '10:00', '1', '1'),
('3', 'Maths', 'A', '100', '001', '1', '2021-02-18', '2021-12-12', 'eng', '1', '10:00', '1', '1'),
('4', 'Maths', 'A', '100', '001', '1', '2021-02-18', '2021-12-12', 'eng', '1', '10:00', '1', '1'),
('5', 'Maths', 'A', '100', '001', '1', '2021-02-18', '2021-12-12', 'eng', '1', '10:00', '1', '1');


/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;