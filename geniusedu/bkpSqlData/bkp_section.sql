-- -------------------------------------------------------------
-- TablePlus 3.12.2(358)
--
-- https://tableplus.com/
--
-- Database: bkp
-- Generation Time: 2021-02-22 23:36:29.0630
-- -------------------------------------------------------------


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


CREATE TABLE `bkp_section` (
  `section_id` varchar(128) NOT NULL,
  `section_name` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `fields` varchar(2550) DEFAULT NULL,
  PRIMARY KEY (`section_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `bkp_section` (`section_id`, `section_name`, `is_active`, `fields`) VALUES
('A', 'Academics', '1', 'Class6, Class7,Class8,Class9,Class10,Class11,Class12'),
('C', 'Compititive', '1', 'UPSC,JPSC,RPSC,MPSC,CDS,NDS,IFA,JEE,CAT,GATE,NIFT,XAT,SSC,NTPC'),
('E', 'Extra-curricular', '1', 'Music,Singing,Acting,Art,Blogging,Literature'),
('M', 'psychologist', '1', ''),
('P', 'Professionals', '1', 'Engineering,Medicine,Fashion Desiging, Interior Designing, Web Designing, Digital Marketing, Film & TV, Animation, Hospitality, Mass Communication, CA, Graphics Designing, Teacher, Computer Application, Agriculturist, Law, Pharmacist, MBA, Event Management, Beautician,');


/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;