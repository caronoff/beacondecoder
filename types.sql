-- phpMyAdmin SQL Dump
-- version 4.1.5
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jul 24, 2018 at 05:42 PM
-- Server version: 5.5.60-0+deb8u1-log
-- PHP Version: 5.6.36-0+deb8u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `cospas_staging`
--

-- --------------------------------------------------------

--
-- Table structure for table `joomla3_cospas_sarsat_contact_detail_types`
--

CREATE TABLE IF NOT EXISTS joomla3_cospas_sarsat_contact_detail_types (
  id int(11) unsigned NOT NULL AUTO_INCREMENT,
  name varchar(255) NOT NULL,
  short_name varchar(255) NOT NULL,
  state tinyint(1) NOT NULL,
  description varchar(255) NOT NULL,
  model_name varchar(255) NOT NULL,
  ordering int(11) NOT NULL,
  created_by int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=9 ;

--
-- Dumping data for table `joomla3_cospas_sarsat_contact_detail_types`
--

INSERT INTO joomla3_cospas_sarsat_contact_detail_types (id, name, short_name, state, description, model_name, ordering, created_by) VALUES
(1, '406 MHz Beacon Registers', '406reg', 1, 'available 24/7 for SAR Services', 'contact_details', 1, 0),
(2, 'National Contacts for Beacon Matters', '406admin', 1, 'Coding, Registration and Type Approval', 'contact_details', 2, 0),
(3, 'SPOC', 'spoc', 1, 'SAR Point of Contact', 'contact_details', 3, 0),
(4, 'PAIS/SAIS', 'sais_pais', 1, 'Primary / Secondary Air Information Stations', 'contact_details', 4, 0),
(5, 'Ground Segment Equipment Manufacturers', 'gsem', 1, '', 'contact_details', 6, 0),
(6, 'Beacon Test Facilities', 'tf', 1, '', 'tac_beacon_test_facilities', 7, 0),
(7, 'Beacon Manufacturers', 'manufacturers', 1, '', 'tac_beacon_manufacturers', 8, 0),
(8, 'Mission Control Centers', 'mcc', 1, '', 'contact_details', 5, 0);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
