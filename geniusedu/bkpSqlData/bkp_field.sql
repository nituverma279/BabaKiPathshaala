-- -------------------------------------------------------------
-- TablePlus 3.12.2(358)
--
-- https://tableplus.com/
--
-- Database: bkp
-- Generation Time: 2021-02-22 23:35:54.5450
-- -------------------------------------------------------------


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


CREATE TABLE `bkp_field` (
  `field_id` varchar(100) NOT NULL,
  `field_name` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `section_id` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`field_id`),
  KEY `fk_section_id` (`section_id`),
  CONSTRAINT `fk_section_id` FOREIGN KEY (`section_id`) REFERENCES `bkp_section` (`section_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `bkp_field` (`field_id`, `field_name`, `is_active`, `section_id`) VALUES
('001', 'engineering', '1', 'P'),
('002', 'medicine', '1', 'P'),
('003', 'web designing', '1', 'P'),
('004', 'computer application', '1', 'P'),
('005', 'mass communication', '0', 'P'),
('006', 'digital marketing', '0', 'P'),
('007', 'class 6', '1', 'A'),
('008', 'class 7', '1', 'A'),
('009', 'class 8', '1', 'A'),
('010', 'class 9', '1', 'A'),
('011', 'class 10', '1', 'A'),
('012', 'class 11', '1', 'A'),
('013', 'class 12', '1', 'A'),
('014', 'music', '1', 'E'),
('015', 'singing', '1', 'E'),
('016', 'acting', '1', 'E'),
('017', 'painting', '1', 'E'),
('018', 'blogging', '1', 'E'),
('019', 'UPSC', '1', 'C'),
('020', 'SSC', '1', 'C'),
('021', 'CDS', '1', 'C'),
('022', 'CAT', '1', 'C'),
('023', 'AIEEE', '1', 'C'),
('024', 'IIT', '1', 'C'),
('025', 'NIFT', '1', 'C'),
('026', 'JPSC', '1', 'C'),
('027', 'BPSC', '1', 'C'),
('028', 'RPSC', '1', 'C'),
('029', 'IBPS', '1', 'C');


/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;