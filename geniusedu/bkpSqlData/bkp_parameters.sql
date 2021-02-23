-- -------------------------------------------------------------
-- TablePlus 3.12.2(358)
--
-- https://tableplus.com/
--
-- Database: bkp
-- Generation Time: 2021-02-22 23:36:05.7400
-- -------------------------------------------------------------


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


CREATE TABLE `bkp_parameters` (
  `TYPE` varchar(128) DEFAULT NULL,
  `PARAM` varchar(255) DEFAULT NULL,
  `VALUE` varchar(2550) DEFAULT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `bkp_parameters` (`TYPE`, `PARAM`, `VALUE`, `DESCRIPTION`) VALUES
('SUBJECT', 'ACADEMICS_COURSES', 'Class 6, Class 7, Class 8, Class 9, Class 10, Class 11, Class 12', NULL),
('SUBJECT', 'PROFESSIONALS_COURSES', 'Engineering,Medicine,Fashion Desiging, Interior Designing, Web Designing, Digital Marketing, Film & TV, Animation, Hospitality, Mass Communication, CA, Graphics Designing, Teacher, Computer Application, Agriculturist, Law, Pharmacist, MBA, Event Management, Beautician,', NULL),
('SUBJECT', 'COMPITITIVE_COURSES', 'UPSC,JPSC,RPSC,MPSC,CDS,NDS,IFA,JEE,CAT,GATE,NIFT,XAT,SSC,NTPC', NULL),
('SUBJECT', 'CURRICULAR_COURSES', 'Music,Singing,Acting,Art,Blogging,Literature', NULL);


/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;