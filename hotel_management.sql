-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Oct 07, 2025 at 08:31 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `hotel_management`
--

-- --------------------------------------------------------

--
-- Table structure for table `amenity`
--

CREATE TABLE `amenity` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` text NOT NULL,
  `icon` varchar(50) NOT NULL,
  `additional_cost` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `amenity`
--

INSERT INTO `amenity` (`id`, `name`, `description`, `icon`, `additional_cost`) VALUES
(26, 'Jacuzzi Tub', 'Private in-room jacuzzi tub for ultimate relaxation and comfort.', 'hot-tub', 800),
(27, 'Wi-Fi', 'High-speed internet access throughout your stay.', 'wifi', 150),
(28, 'Private Balcony', 'Enjoy the beautiful outdoors from your own private balcony with seating area.', 'door-open', 500),
(29, 'Mini Bar', 'Fully stocked mini refrigerator with beverages and snacks, replenished daily.', 'wine-glass-alt', 300),
(30, 'Room Service', '24/7 room service with a wide selection of meals and refreshments.', 'bell', 200);

-- --------------------------------------------------------

--
-- Table structure for table `booking`
--

CREATE TABLE `booking` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `check_in_date` date NOT NULL,
  `check_out_date` date NOT NULL,
  `num_guests` int(11) NOT NULL,
  `total_price` float NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `payment_method` varchar(20) NOT NULL,
  `payment_reference` varchar(100) DEFAULT NULL,
  `payment_screenshot` varchar(255) DEFAULT NULL,
  `payment_status` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `approved_by` int(11) DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  `rejected_by` int(11) DEFAULT NULL,
  `rejected_at` datetime DEFAULT NULL,
  `cancellation_reason` text DEFAULT NULL,
  `cancelled_at` datetime DEFAULT NULL,
  `rejection_reason` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `booking`
--

INSERT INTO `booking` (`id`, `user_id`, `room_id`, `check_in_date`, `check_out_date`, `num_guests`, `total_price`, `status`, `payment_method`, `payment_reference`, `payment_screenshot`, `payment_status`, `created_at`, `approved_by`, `approved_at`, `rejected_by`, `rejected_at`, `cancellation_reason`, `cancelled_at`, `rejection_reason`) VALUES
(77, 29, 7, '2025-07-11', '2025-07-12', 1, 1500, 'rejected', 'pay_on_site', NULL, NULL, 'pending', '2025-07-11 10:55:15', NULL, NULL, 4, '2025-07-11 13:04:55', NULL, NULL, NULL),
(78, 29, 8, '2025-07-11', '2025-07-12', 1, 2450, 'rejected', 'pay_on_site', NULL, NULL, 'pending', '2025-07-11 11:03:24', NULL, NULL, 4, '2025-07-16 18:22:11', NULL, NULL, NULL),
(79, 29, 7, '2025-07-16', '2025-07-17', 1, 1816.5, 'rejected', 'pay_on_site', NULL, NULL, 'pending', '2025-07-11 11:08:30', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(80, 29, 9, '2025-07-01', '2025-07-02', 1, 5000, 'completed', 'pay_on_site', NULL, NULL, 'pending', '2025-07-11 11:10:16', 4, '2025-07-11 12:26:55', NULL, NULL, NULL, NULL, NULL),
(81, 29, 7, '2025-07-09', '2025-07-11', 1, 1500, 'cancelled', 'pay_on_site', NULL, NULL, 'pending', '2025-07-11 13:05:09', 4, '2025-07-11 13:56:04', NULL, NULL, 'Cancel it', '2025-07-11 22:05:34', NULL),
(82, 29, 7, '2025-07-26', '2025-07-27', 1, 1500, 'completed', 'pay_on_site', NULL, NULL, 'pending', '2025-07-11 14:01:46', 4, '2025-07-11 18:02:26', NULL, NULL, NULL, NULL, NULL),
(88, 30, 8, '2025-07-16', '2025-07-17', 1, 3500, 'completed', 'pay_on_site', NULL, NULL, 'pending', '2025-07-16 11:14:06', 4, '2025-07-16 11:14:27', NULL, NULL, NULL, NULL, NULL),
(89, 31, 7, '2025-07-16', '2025-07-17', 1, 1500, 'completed', 'pay_on_site', NULL, NULL, 'pending', '2025-07-16 11:24:26', 4, '2025-07-16 11:24:34', NULL, NULL, NULL, NULL, NULL),
(90, 31, 9, '2025-07-01', '2025-07-02', 1, 5000, 'completed', 'pay_on_site', NULL, NULL, 'pending', '2025-07-16 18:22:30', 4, '2025-07-16 18:22:37', NULL, NULL, NULL, NULL, NULL),
(91, 31, 11, '2025-08-23', '2025-08-24', 1, 5000, 'completed', 'pay_on_site', NULL, NULL, 'pending', '2025-08-22 23:06:01', 4, '2025-08-22 23:07:00', NULL, NULL, NULL, NULL, NULL),
(105, 31, 11, '2025-08-27', '2025-08-28', 1, 5000, 'rejected', 'pay_on_site', NULL, NULL, 'pending', '2025-08-27 10:26:27', NULL, NULL, 4, '2025-08-27 10:33:56', 'hehe', NULL, 'hehe'),
(106, 31, 8, '2025-08-29', '2025-08-30', 1, 3500, 'completed', 'pay_on_site', NULL, NULL, 'pending', '2025-08-29 14:11:32', 4, '2025-08-29 14:12:10', NULL, NULL, NULL, NULL, NULL),
(107, 31, 9, '2025-09-24', '2025-09-25', 1, 5000, 'completed', 'pay_on_site', NULL, NULL, 'pending', '2025-09-24 10:00:02', 4, '2025-09-24 10:13:40', NULL, NULL, NULL, NULL, NULL),
(110, 31, 7, '2025-09-25', '2025-09-26', 1, 1800, 'completed', 'pay_on_site', NULL, NULL, 'pending', '2025-09-24 21:06:26', 4, '2025-09-24 21:06:49', NULL, NULL, NULL, NULL, NULL),
(112, 31, 11, '2025-09-29', '2025-09-30', 1, 5650, 'pending', 'pay_on_site', NULL, NULL, 'pending', '2025-09-29 04:32:28', NULL, NULL, NULL, NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `booking_amenity`
--

CREATE TABLE `booking_amenity` (
  `booking_id` int(11) NOT NULL,
  `amenity_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `booking_amenity`
--

INSERT INTO `booking_amenity` (`booking_id`, `amenity_id`) VALUES
(79, 27),
(79, 29),
(82, 29),
(110, 29),
(112, 27),
(112, 28);

-- --------------------------------------------------------

--
-- Table structure for table `comment`
--

CREATE TABLE `comment` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `booking_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `rating` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `comment`
--

INSERT INTO `comment` (`id`, `user_id`, `booking_id`, `content`, `rating`, `created_at`) VALUES
(5, 3, 59, 'Good hotel.', 4, '2025-05-11 12:03:37'),
(15, 31, 90, 'Good hotel', 4, '2025-07-17 11:50:01'),
(16, 31, 89, 'Nice!', 3, '2025-07-17 23:37:58');

-- --------------------------------------------------------

--
-- Table structure for table `eatnrun_rating`
--

CREATE TABLE `eatnrun_rating` (
  `id` int(11) NOT NULL,
  `rating` int(11) NOT NULL CHECK (`rating` between 1 and 5),
  `comment` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `order_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `eatnrun_rating`
--

INSERT INTO `eatnrun_rating` (`id`, `rating`, `comment`, `created_at`, `updated_at`, `order_id`) VALUES
(13, 5, 'Very Good!', '2025-07-17 21:35:39', '2025-07-17 22:00:22', 51),
(14, 4, 'Good Restaurant', '2025-07-17 22:00:35', '2025-07-17 22:00:35', 50),
(15, 5, 'SAD', '2025-07-17 22:16:48', '2025-07-17 22:16:48', 12),
(16, 4, 'HEHE', '2025-08-22 22:52:21', '2025-08-22 22:52:21', 82),
(17, 4, 'Yes!', '2025-08-23 11:36:34', '2025-08-23 11:39:10', 92),
(18, 5, 'Good Food', '2025-08-23 12:45:30', '2025-08-23 12:45:30', 97),
(19, 4, 'Tongits ', '2025-08-29 22:19:26', '2025-08-29 22:19:26', 99);

-- --------------------------------------------------------

--
-- Table structure for table `gallery_image`
--

CREATE TABLE `gallery_image` (
  `id` int(11) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `title` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `is_homepage` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `gallery_image`
--

INSERT INTO `gallery_image` (`id`, `filename`, `title`, `description`, `category`, `created_at`, `is_homepage`) VALUES
(2, '1746965234_suiteroom.jpg', 'Full of Amenities', 'Amenities including wifi, bathtub and more.', 'room', '2025-05-11 11:51:35', 0),
(3, '1746964333_romanticgetaway.jpg', 'Comfortable Hotel', 'We offer a comfortable hotel to stay in.', 'room', '2025-05-11 11:52:13', 0);

-- --------------------------------------------------------

--
-- Table structure for table `home_page_image`
--

CREATE TABLE `home_page_image` (
  `id` int(11) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `order` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `home_page_image`
--

INSERT INTO `home_page_image` (`id`, `filename`, `created_at`, `order`) VALUES
(1, '1752662237_HomepageImage.png', '2025-07-11 09:28:08', 0),
(2, '1752662307_discount.jpg', '2025-07-11 09:28:15', 1),
(3, '1752226101_descriptionimage.jpg', '2025-07-11 09:28:21', 1);

-- --------------------------------------------------------

--
-- Table structure for table `home_page_settings`
--

CREATE TABLE `home_page_settings` (
  `id` int(11) NOT NULL,
  `carousel_interval` int(11) DEFAULT 5000
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `home_page_settings`
--

INSERT INTO `home_page_settings` (`id`, `carousel_interval`) VALUES
(1, 3);

-- --------------------------------------------------------

--
-- Table structure for table `notification`
--

CREATE TABLE `notification` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(100) NOT NULL,
  `message` text NOT NULL,
  `type` varchar(20) NOT NULL,
  `is_read` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notification`
--

INSERT INTO `notification` (`id`, `user_id`, `title`, `message`, `type`, `is_read`, `created_at`) VALUES
(149, 3, 'Booking Created', 'Your booking for Room 101 has been submitted and is pending approval. (Booking ID: 56)', 'booking', 0, '2025-05-11 11:52:50'),
(151, 3, 'Booking Approved', 'Your booking for Room 101 has been approved! (Booking ID: 56)', 'booking', 0, '2025-05-11 11:53:02'),
(153, 3, 'Booking Created', 'Your booking for Room 201 has been submitted and is pending approval. (Booking ID: 57)', 'booking', 0, '2025-05-11 11:53:24'),
(155, 3, 'Booking Rejected', 'Your booking for Room 201 has been rejected. (Booking ID: 57)', 'booking', 0, '2025-05-11 11:53:32'),
(157, 3, 'Booking Created', 'Your booking for Room 301 has been submitted and is pending approval. (Booking ID: 58)', 'booking', 0, '2025-05-11 11:53:58'),
(159, 3, 'Booking Approved', 'Your booking for Room 301 has been approved! (Booking ID: 58)', 'booking', 0, '2025-05-11 11:54:06'),
(161, 3, 'Booking Cancelled', 'Your booking for Room 301 has been cancelled. (Booking ID: 58)', 'booking', 0, '2025-05-11 11:54:29'),
(163, 3, 'Booking Created', 'Your booking for Room 401 has been submitted and is pending approval. (Booking ID: 59)', 'booking', 0, '2025-05-11 11:58:11'),
(165, 3, 'Booking Approved', 'Your booking for Room 401 has been approved! (Booking ID: 59)', 'booking', 1, '2025-05-11 11:58:26'),
(171, 3, 'Booking Created', 'Your booking for Room 401 has been submitted and is pending approval. (Booking ID: 61)', 'booking', 0, '2025-07-09 08:59:03'),
(173, 17, 'Account Rejected', 'Your account registration has been rejected by the administrator.', 'system', 0, '2025-07-09 16:17:24'),
(174, 18, 'Account Approved', 'Your account has been approved by the administrator.', 'system', 0, '2025-07-09 16:24:33'),
(175, 18, 'Account Approved', 'Your account has been approved by the administrator.', 'system', 1, '2025-07-09 16:24:40'),
(176, 19, 'Account Approved', 'Your account has been approved by the administrator.', 'system', 0, '2025-07-09 16:30:17'),
(177, 20, 'Account Approved', 'Your account has been approved by the administrator.', 'system', 0, '2025-07-09 17:02:07'),
(178, 21, 'Account Approved', 'Your account has been approved by the administrator.', 'system', 0, '2025-07-09 17:59:51'),
(182, 3, 'Booking Deleted', 'Your booking for Room 201 has been deleted by an administrator.', 'booking', 0, '2025-07-09 19:11:01'),
(245, 29, 'Account Approved', 'Your account has been approved by the administrator.', 'system', 1, '2025-07-11 09:26:59'),
(246, 29, 'Booking Created', 'Your booking for Room 101 has been submitted and is pending approval. (Booking ID: 77)', 'booking', 1, '2025-07-11 10:55:15'),
(248, 29, 'Booking Created', 'Your booking for Room 201 has been submitted and is pending approval. (Booking ID: 78)', 'booking', 1, '2025-07-11 11:03:24'),
(250, 29, 'Booking Created', 'Your booking for Room 101 has been submitted and is pending approval. (Booking ID: 79)', 'booking', 1, '2025-07-11 11:08:30'),
(252, 29, 'Booking Created', 'Your booking for Room 301 has been submitted and is pending approval. (Booking ID: 80)', 'booking', 1, '2025-07-11 11:10:16'),
(256, 29, 'Booking Approved', 'Your booking for Room 301 has been approved! (Booking ID: 80)', 'booking', 1, '2025-07-11 12:26:55'),
(258, 29, 'Booking Rejected', 'Your booking for Room 101 has been rejected. (Booking ID: 77)', 'booking', 1, '2025-07-11 13:04:55'),
(260, 29, 'Booking Created', 'Your booking for Room 101 has been submitted and is pending approval. (Booking ID: 81)', 'booking', 1, '2025-07-11 13:05:09'),
(264, 29, 'Booking Approved', 'Your booking for Room 101 has been approved! (Booking ID: 81)', 'booking', 1, '2025-07-11 13:56:04'),
(266, 29, 'Booking Created', 'Your booking for Room 101 has been submitted and is pending approval. (Booking ID: 82)', 'booking', 1, '2025-07-11 14:01:46'),
(268, 1, 'Booking Cancelled', 'Booking #81 has been cancelled by Jessie Rex Sacluti Somogod Jr..', 'booking', 0, '2025-07-11 14:05:34'),
(269, 29, 'Booking Approved', 'Your booking for Room 101 has been approved! (Booking ID: 82)', 'booking', 1, '2025-07-11 18:02:26'),
(283, 1, 'Booking Cancelled', 'Booking #85 has been cancelled by Jhune Vincent Aquino Roces.', 'booking', 0, '2025-07-15 16:35:35'),
(288, 1, 'Booking Cancelled', 'Booking #86 has been cancelled by Jhune Vincent Aquino Roces.', 'booking', 0, '2025-07-15 17:22:42'),
(291, 30, 'Account Approved', 'Your account has been approved by the administrator.', 'system', 0, '2025-07-16 05:35:31'),
(294, 30, 'Booking Created', 'Your booking for Room 201 has been submitted and is pending approval. (Booking ID: 88)', 'booking', 1, '2025-07-16 11:14:06'),
(296, 30, 'Booking Approved', 'Your booking for Room 201 has been approved! (Booking ID: 88)', 'booking', 1, '2025-07-16 11:14:27'),
(301, 29, 'Booking Rejected', 'Your booking for Room 101 from 2025-07-16 to 2025-07-17 was rejected because the room was booked by another guest.', 'booking', 1, '2025-07-16 11:24:34'),
(304, 29, 'Booking Rejected', 'Your booking for Room 201 has been rejected. (Booking ID: 78)', 'booking', 1, '2025-07-16 18:22:11'),
(316, 1, 'Booking Cancelled', 'Booking #92 has been cancelled by Jhune Vincent Aquino Roces.', 'booking', 0, '2025-08-27 09:40:33'),
(356, 31, 'Booking Created', 'Your booking for Room 401 has been submitted and is pending approval. (Booking ID: 101)', 'booking', 1, '2025-08-27 10:12:38'),
(358, 1, 'Booking Cancelled', 'Booking #101 has been cancelled by Jhune Vincent Aquino Roces.', 'booking', 0, '2025-08-27 10:13:23'),
(359, 31, 'Booking Created', 'Your booking for Room 401 has been submitted and is pending approval. (Booking ID: 102)', 'booking', 1, '2025-08-27 10:13:43'),
(361, 31, 'Booking Rejected', 'Your booking for Room 401 has been rejected. (Booking ID: 102)', 'booking', 1, '2025-08-27 10:14:22'),
(363, 31, 'Booking Deleted', 'Your booking for Room 401 has been deleted by an administrator.', 'booking', 1, '2025-08-27 10:14:29'),
(364, 31, 'Booking Created', 'Your booking for Room 401 has been submitted and is pending approval. (Booking ID: 103)', 'booking', 1, '2025-08-27 10:15:29'),
(366, 31, 'Booking Rejected', 'Your booking for Room 401 has been rejected. (Booking ID: 103)', 'booking', 1, '2025-08-27 10:20:25'),
(368, 31, 'Booking Deleted', 'Your booking for Room 401 has been deleted by an administrator.', 'booking', 1, '2025-08-27 10:20:31'),
(369, 31, 'Booking Created', 'Your booking for Room 401 has been submitted and is pending approval. (Booking ID: 104)', 'booking', 1, '2025-08-27 10:20:50'),
(371, 31, 'Booking Rejected', 'Your booking for Room 401 has been rejected. (Booking ID: 104)', 'booking', 1, '2025-08-27 10:25:59'),
(373, 31, 'Booking Deleted', 'Your booking for Room 401 has been deleted by an administrator.', 'booking', 1, '2025-08-27 10:26:05'),
(374, 31, 'Booking Created', 'Your booking for Room 401 has been submitted and is pending approval. (Booking ID: 105)', 'booking', 1, '2025-08-27 10:26:27'),
(376, 31, 'Booking Rejected', 'Your booking for Room 401 has been rejected. (Booking ID: 105)', 'booking', 1, '2025-08-27 10:33:56'),
(377, 4, 'Booking Rejected', 'Booking for Room 401 has been rejected by Fawna Hotel. (Booking ID: 105)', 'booking', 0, '2025-08-27 10:33:56'),
(378, 31, 'Booking Created', 'Your booking for Room 201 has been submitted and is pending approval. (Booking ID: 106)', 'booking', 1, '2025-08-29 14:11:32'),
(379, 4, 'Booking Created', 'New booking request for Room 201 from Jhune Vincent Aquino Roces. (Booking ID: 106)', 'booking', 0, '2025-08-29 14:11:32'),
(380, 31, 'Booking Approved', 'Your booking for Room 201 has been approved! (Booking ID: 106)', 'booking', 1, '2025-08-29 14:12:10'),
(381, 4, 'Booking Approved', 'Booking for Room 201 has been approved by Fawna Hotel. (Booking ID: 106)', 'booking', 0, '2025-08-29 14:12:10'),
(387, 31, 'Booking Created', 'Your booking for Room 301 has been submitted and is pending approval. (Booking ID: 107)', 'booking', 1, '2025-09-24 10:00:02'),
(388, 4, 'Booking Created', 'New booking request for Room 301 from Jhune Vincent Aquino Roces. (Booking ID: 107)', 'booking', 0, '2025-09-24 10:00:02'),
(389, 31, 'Booking Approved', 'Your booking for Room 301 has been approved! (Booking ID: 107)', 'booking', 1, '2025-09-24 10:13:41'),
(390, 4, 'Booking Approved', 'Booking for Room 301 has been approved by Fawna Hotel. (Booking ID: 107)', 'booking', 0, '2025-09-24 10:13:41'),
(393, 4, 'Booking Created', 'New booking request for Room 401 from Jesselle Somogod. (Booking ID: 108)', 'booking', 0, '2025-09-24 19:38:13'),
(395, 4, 'Booking Approved', 'Booking for Room 401 has been approved by Fawna Hotel. (Booking ID: 108)', 'booking', 0, '2025-09-24 19:38:42'),
(396, 31, 'Booking Created', 'Your booking for Room 201 has been submitted and is pending approval. (Booking ID: 109)', 'booking', 1, '2025-09-24 21:00:53'),
(397, 4, 'Booking Created', 'New booking request for Room 201 from Jhune Vincent Aquino Roces. (Booking ID: 109)', 'booking', 0, '2025-09-24 21:00:53'),
(398, 31, 'Booking Rejected', 'Your booking for Room 201 has been rejected. (Booking ID: 109)', 'booking', 1, '2025-09-24 21:01:29'),
(399, 4, 'Booking Rejected', 'Booking for Room 201 has been rejected by Fawna Hotel. (Booking ID: 109)', 'booking', 0, '2025-09-24 21:01:29'),
(400, 31, 'Booking Created', 'Your booking for Room 101 has been submitted and is pending approval. (Booking ID: 110)', 'booking', 1, '2025-09-24 21:06:26'),
(401, 4, 'Booking Created', 'New booking request for Room 101 from Jhune Vincent Aquino Roces. (Booking ID: 110)', 'booking', 0, '2025-09-24 21:06:26'),
(402, 31, 'Booking Approved', 'Your booking for Room 101 has been approved! (Booking ID: 110)', 'booking', 1, '2025-09-24 21:06:49'),
(403, 4, 'Booking Approved', 'Booking for Room 101 has been approved by Fawna Hotel. (Booking ID: 110)', 'booking', 0, '2025-09-24 21:06:49'),
(404, 31, 'Booking Created', 'Your booking for Room 101 has been submitted and is pending approval. (Booking ID: 111)', 'booking', 1, '2025-09-29 04:31:44'),
(405, 4, 'Booking Created', 'New booking request for Room 101 from Jhune Vincent Aquino Roces. (Booking ID: 111)', 'booking', 0, '2025-09-29 04:31:44'),
(406, 1, 'Booking Cancelled', 'Booking #111 has been cancelled by Jhune Vincent Aquino Roces.', 'booking', 0, '2025-09-29 04:31:58'),
(407, 31, 'Booking Created', 'Your booking for Room 401 has been submitted and is pending approval. (Booking ID: 112)', 'booking', 1, '2025-09-29 04:32:28'),
(408, 4, 'Booking Created', 'New booking request for Room 401 from Jhune Vincent Aquino Roces. (Booking ID: 112)', 'booking', 0, '2025-09-29 04:32:28');

-- --------------------------------------------------------

--
-- Table structure for table `promo`
--

CREATE TABLE `promo` (
  `id` int(11) NOT NULL,
  `title` varchar(120) NOT NULL,
  `description` text NOT NULL,
  `image` varchar(255) DEFAULT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `validity` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `discount_percentage` float DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `promo`
--

INSERT INTO `promo` (`id`, `title`, `description`, `image`, `start_date`, `end_date`, `is_active`, `validity`, `created_at`, `discount_percentage`) VALUES
(4, 'Family Getaway', 'Book a family suite and get free breakfast for 4!', 'promos/promo_1752481806_deluxeroom.jpg', '2025-07-01', '2025-09-30', 1, '', '2025-07-14 16:29:47', 15),
(5, 'Summer Splash!', 'Enjoy a refreshing summer stay with 20% off on all rooms!', 'promos/promo_1752481828_descriptionimage.jpg', '2025-06-01', '2025-08-31', 1, '', '2025-07-14 16:29:47', 20),
(6, 'VIP Member Special', 'Exclusive 30% discount for VIP members only.', 'promos/promo_1752481851_vipmembership.jpg', '2025-01-01', '2025-12-31', 1, '', '2025-07-14 16:29:47', 30);

-- --------------------------------------------------------

--
-- Table structure for table `promo_rooms`
--

CREATE TABLE `promo_rooms` (
  `promo_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `promo_room_types`
--

CREATE TABLE `promo_room_types` (
  `promo_id` int(11) NOT NULL,
  `room_type_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `room`
--

CREATE TABLE `room` (
  `id` int(11) NOT NULL,
  `room_number` varchar(10) NOT NULL,
  `floor` int(11) NOT NULL,
  `is_available` tinyint(1) DEFAULT NULL,
  `room_type_id` int(11) NOT NULL,
  `occupancy_limit` int(11) NOT NULL,
  `image` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `room`
--

INSERT INTO `room` (`id`, `room_number`, `floor`, `is_available`, `room_type_id`, `occupancy_limit`, `image`) VALUES
(7, '101', 1, 1, 1, 2, 'room_images/room_20250511_194904_discount.jpg'),
(8, '201', 2, 1, 4, 3, 'room_images/room_20250511_194923_vipmembership.jpg'),
(9, '301', 3, 1, 7, 4, 'room_images/room_20250511_194939_AccomodationsImage.jpg'),
(11, '401', 4, 1, 7, 2, 'room_images/room_20250511_194953_descriptionimage.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `room_amenities`
--

CREATE TABLE `room_amenities` (
  `room_id` int(11) NOT NULL,
  `amenity_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `room_amenities`
--

INSERT INTO `room_amenities` (`room_id`, `amenity_id`) VALUES
(7, 27),
(7, 29),
(8, 29),
(9, 29),
(11, 26),
(11, 27),
(11, 28),
(11, 29),
(11, 30);

-- --------------------------------------------------------

--
-- Table structure for table `room_type`
--

CREATE TABLE `room_type` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` text NOT NULL,
  `price_per_night` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `room_type`
--

INSERT INTO `room_type` (`id`, `name`, `description`, `price_per_night`) VALUES
(1, 'Standard Room', 'A cozy room for two.', 1500),
(4, 'Family Room', 'Comfortable room with two queen beds, designed to accommodate families with children. Features child-friendly amenities and extra space.', 3500),
(7, 'Deluxe Suite', 'A spacious suite with premium furnishings, king-size bed, and panoramic views of the city skyline. Perfect for couples seeking luxury.', 5000),
(8, 'Mega Family ', 'Comfortable room with two queen beds, designed to accommodate families with children. Features child-friendly amenities and extra space.', 3500);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(120) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `password` varchar(200) NOT NULL,
  `profile_pic` varchar(200) DEFAULT NULL,
  `is_admin` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `email_verified` tinyint(1) DEFAULT NULL,
  `email_verification_token` varchar(100) DEFAULT NULL,
  `email_verification_sent_at` datetime DEFAULT NULL,
  `verification_token` varchar(100) DEFAULT NULL,
  `id_picture` varchar(255) DEFAULT NULL,
  `registration_status` varchar(20) DEFAULT 'pending',
  `id_type` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `name`, `email`, `phone`, `password`, `profile_pic`, `is_admin`, `created_at`, `email_verified`, `email_verification_token`, `email_verification_sent_at`, `verification_token`, `id_picture`, `registration_status`, `id_type`) VALUES
(4, 'Fawna Hotel', 'fawnahotel@gmail.com', '+639475448982', 'pbkdf2:sha256:260000$XidbJxMsLeMw72H2$131c694ac2702be3b1ed6dfa832c419f71cb7147a195e19e0a8bdc6f7a1774f5', 'images/profiles/profile_4_1756287449_fawna.png', 1, '2025-05-08 03:10:49', 1, NULL, NULL, NULL, NULL, 'pending', NULL),
(29, 'Jessie Rex Sacluti Somogod Jr.', 'somogodjessierex12@gmail.com', '+639754067938', 'pbkdf2:sha256:260000$DzqewXO7hpmqylz1$82b5b183f07fdaeafdb4fc226e25ea5063572226a45b524248b8883ca49bff69', 'images/profiles/profile_29_1752289850_me.jpg', 0, '2025-07-11 09:26:14', 1, NULL, NULL, NULL, 'ids/1752225974_me.jpg', 'approved', 'drivers_license'),
(30, 'Brian Sandoval Garlando', 'paxleyaiden@gmail.com', '+639673624454', 'pbkdf2:sha256:260000$YhissqIQdq8KdMtx$f959ee83b5fefe10e9e22d686257cc486a0297b513bdb091f756ce8144570418', NULL, 0, '2025-07-16 05:32:59', 1, NULL, NULL, NULL, 'ids/1752643978_484901034_122209037672188872_4198655431084102122_n.jpg', 'approved', 'drivers_license'),
(31, 'Jhune Vincent Aquino Roces', 'jhunevincentaquinoroces@gmail.com', '+639475448982', 'pbkdf2:sha256:260000$eAolSHaNM8odgJOv$1e140f4d5e256a5e1c21e1382ac98463b2422985d591a46e94c0c2bf0db00d60', 'images/profiles/profile_31_1758743444_IMG20250925025558.jpg', 0, '2025-07-16 11:23:52', 1, NULL, NULL, NULL, 'ids/1752665031_slide1.jpg', 'approved', 'passport');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `amenity`
--
ALTER TABLE `amenity`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `booking`
--
ALTER TABLE `booking`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `room_id` (`room_id`),
  ADD KEY `approved_by` (`approved_by`),
  ADD KEY `rejected_by` (`rejected_by`);

--
-- Indexes for table `booking_amenity`
--
ALTER TABLE `booking_amenity`
  ADD PRIMARY KEY (`booking_id`,`amenity_id`),
  ADD KEY `amenity_id` (`amenity_id`);

--
-- Indexes for table `comment`
--
ALTER TABLE `comment`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `booking_id` (`booking_id`);

--
-- Indexes for table `eatnrun_rating`
--
ALTER TABLE `eatnrun_rating`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `gallery_image`
--
ALTER TABLE `gallery_image`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `home_page_image`
--
ALTER TABLE `home_page_image`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `home_page_settings`
--
ALTER TABLE `home_page_settings`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `notification`
--
ALTER TABLE `notification`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `promo`
--
ALTER TABLE `promo`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `promo_rooms`
--
ALTER TABLE `promo_rooms`
  ADD PRIMARY KEY (`promo_id`,`room_id`),
  ADD KEY `room_id` (`room_id`);

--
-- Indexes for table `promo_room_types`
--
ALTER TABLE `promo_room_types`
  ADD PRIMARY KEY (`promo_id`,`room_type_id`),
  ADD KEY `room_type_id` (`room_type_id`);

--
-- Indexes for table `room`
--
ALTER TABLE `room`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `room_number` (`room_number`),
  ADD KEY `room_type_id` (`room_type_id`);

--
-- Indexes for table `room_amenities`
--
ALTER TABLE `room_amenities`
  ADD PRIMARY KEY (`room_id`,`amenity_id`),
  ADD KEY `amenity_id` (`amenity_id`);

--
-- Indexes for table `room_type`
--
ALTER TABLE `room_type`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `email_verification_token` (`email_verification_token`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `amenity`
--
ALTER TABLE `amenity`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `booking`
--
ALTER TABLE `booking`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=113;

--
-- AUTO_INCREMENT for table `comment`
--
ALTER TABLE `comment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `eatnrun_rating`
--
ALTER TABLE `eatnrun_rating`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `gallery_image`
--
ALTER TABLE `gallery_image`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `home_page_image`
--
ALTER TABLE `home_page_image`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `home_page_settings`
--
ALTER TABLE `home_page_settings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `notification`
--
ALTER TABLE `notification`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=409;

--
-- AUTO_INCREMENT for table `promo`
--
ALTER TABLE `promo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `room`
--
ALTER TABLE `room`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `room_type`
--
ALTER TABLE `room_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=38;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `booking`
--
ALTER TABLE `booking`
  ADD CONSTRAINT `booking_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  ADD CONSTRAINT `booking_ibfk_2` FOREIGN KEY (`room_id`) REFERENCES `room` (`id`),
  ADD CONSTRAINT `booking_ibfk_3` FOREIGN KEY (`approved_by`) REFERENCES `user` (`id`),
  ADD CONSTRAINT `booking_ibfk_4` FOREIGN KEY (`rejected_by`) REFERENCES `user` (`id`);

--
-- Constraints for table `booking_amenity`
--
ALTER TABLE `booking_amenity`
  ADD CONSTRAINT `booking_amenity_ibfk_1` FOREIGN KEY (`amenity_id`) REFERENCES `amenity` (`id`),
  ADD CONSTRAINT `booking_amenity_ibfk_2` FOREIGN KEY (`booking_id`) REFERENCES `booking` (`id`);

--
-- Constraints for table `promo_rooms`
--
ALTER TABLE `promo_rooms`
  ADD CONSTRAINT `promo_rooms_ibfk_1` FOREIGN KEY (`promo_id`) REFERENCES `promo` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `promo_rooms_ibfk_2` FOREIGN KEY (`room_id`) REFERENCES `room` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `promo_room_types`
--
ALTER TABLE `promo_room_types`
  ADD CONSTRAINT `promo_room_types_ibfk_1` FOREIGN KEY (`promo_id`) REFERENCES `promo` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `promo_room_types_ibfk_2` FOREIGN KEY (`room_type_id`) REFERENCES `room_type` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
