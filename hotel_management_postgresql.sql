--
-- PostgreSQL database dump for Render.com
-- Converted from MySQL hotel_management database
-- Compatible with PostgreSQL 15+
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

SET default_tablespace = '';

--
-- Name: amenity; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.amenity (
    id SERIAL PRIMARY KEY,
    name varchar(50) NOT NULL,
    description text NOT NULL,
    icon varchar(50) NOT NULL,
    additional_cost float DEFAULT NULL
);

--
-- Name: booking; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.booking (
    id SERIAL PRIMARY KEY,
    user_id int NOT NULL,
    room_id int NOT NULL,
    check_in_date date NOT NULL,
    check_out_date date NOT NULL,
    num_guests int NOT NULL,
    total_price float NOT NULL,
    status varchar(20) DEFAULT NULL,
    payment_method varchar(20) NOT NULL,
    payment_reference varchar(100) DEFAULT NULL,
    payment_screenshot varchar(255) DEFAULT NULL,
    payment_status varchar(20) DEFAULT NULL,
    created_at timestamp DEFAULT NULL,
    approved_by int DEFAULT NULL,
    approved_at timestamp DEFAULT NULL,
    rejected_by int DEFAULT NULL,
    rejected_at timestamp DEFAULT NULL,
    cancellation_reason text DEFAULT NULL,
    cancelled_at timestamp DEFAULT NULL,
    rejection_reason text DEFAULT NULL
);

--
-- Name: booking_amenity; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.booking_amenity (
    booking_id int NOT NULL,
    amenity_id int NOT NULL,
    PRIMARY KEY (booking_id, amenity_id)
);

--
-- Name: comment; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.comment (
    id SERIAL PRIMARY KEY,
    user_id int NOT NULL,
    booking_id int NOT NULL,
    content text NOT NULL,
    rating int DEFAULT NULL,
    created_at timestamp DEFAULT NULL
);

--
-- Name: eatnrun_rating; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.eatnrun_rating (
    id SERIAL PRIMARY KEY,
    rating int NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment varchar(500) DEFAULT NULL,
    created_at timestamp DEFAULT current_timestamp,
    updated_at timestamp DEFAULT current_timestamp,
    order_id int NOT NULL
);

--
-- Name: gallery_image; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.gallery_image (
    id SERIAL PRIMARY KEY,
    filename varchar(255) NOT NULL,
    title varchar(100) NOT NULL,
    description text DEFAULT NULL,
    category varchar(50) DEFAULT NULL,
    created_at timestamp DEFAULT NULL,
    is_homepage boolean DEFAULT false
);

--
-- Name: home_page_image; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.home_page_image (
    id SERIAL PRIMARY KEY,
    filename varchar(255) NOT NULL,
    created_at timestamp DEFAULT current_timestamp,
    "order" int DEFAULT 0
);

--
-- Name: home_page_settings; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.home_page_settings (
    id SERIAL PRIMARY KEY,
    carousel_interval int DEFAULT 5000
);

--
-- Name: notification; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.notification (
    id SERIAL PRIMARY KEY,
    user_id int NOT NULL,
    title varchar(100) NOT NULL,
    message text NOT NULL,
    type varchar(20) NOT NULL,
    is_read boolean DEFAULT NULL,
    created_at timestamp DEFAULT NULL
);

--
-- Name: promo; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.promo (
    id SERIAL PRIMARY KEY,
    title varchar(120) NOT NULL,
    description text NOT NULL,
    image varchar(255) DEFAULT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    is_active boolean DEFAULT true,
    validity varchar(100) NOT NULL,
    created_at timestamp DEFAULT current_timestamp,
    discount_percentage float DEFAULT 0
);

--
-- Name: promo_rooms; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.promo_rooms (
    promo_id int NOT NULL,
    room_id int NOT NULL,
    PRIMARY KEY (promo_id, room_id)
);

--
-- Name: promo_room_types; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.promo_room_types (
    promo_id int NOT NULL,
    room_type_id int NOT NULL,
    PRIMARY KEY (promo_id, room_type_id)
);

--
-- Name: room; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.room (
    id SERIAL PRIMARY KEY,
    room_number varchar(10) NOT NULL UNIQUE,
    floor int NOT NULL,
    is_available boolean DEFAULT NULL,
    room_type_id int NOT NULL,
    occupancy_limit int NOT NULL,
    image varchar(255) DEFAULT NULL
);

--
-- Name: room_amenities; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.room_amenities (
    room_id int NOT NULL,
    amenity_id int NOT NULL,
    PRIMARY KEY (room_id, amenity_id)
);

--
-- Name: room_type; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public.room_type (
    id SERIAL PRIMARY KEY,
    name varchar(50) NOT NULL,
    description text NOT NULL,
    price_per_night float NOT NULL
);

--
-- Name: "user"; Type: TABLE; Schema: public; Owner: (Render default)
--

CREATE TABLE IF NOT EXISTS public."user" (
    id SERIAL PRIMARY KEY,
    name varchar(100) NOT NULL,
    email varchar(120) NOT NULL UNIQUE,
    phone varchar(20) DEFAULT NULL,
    password varchar(200) NOT NULL,
    profile_pic varchar(200) DEFAULT NULL,
    is_admin boolean DEFAULT NULL,
    created_at timestamp DEFAULT NULL,
    email_verified boolean DEFAULT NULL,
    email_verification_token varchar(100) DEFAULT NULL UNIQUE,
    email_verification_sent_at timestamp DEFAULT NULL,
    verification_token varchar(100) DEFAULT NULL,
    id_picture varchar(255) DEFAULT NULL,
    registration_status varchar(20) DEFAULT 'pending',
    id_type varchar(50) DEFAULT NULL
);

--
-- Data for Name: amenity; Type: TABLE DATA; Schema: public; Owner: (Render default)
--

COPY public.amenity (id, name, description, icon, additional_cost) FROM stdin;
26	Jacuzzi Tub	Private in-room jacuzzi tub for ultimate relaxation and comfort.	hot-tub	800.0
27	Wi-Fi	High-speed internet access throughout your stay.	wifi	150.0
28	Private Balcony	Enjoy the beautiful outdoors from your own private balcony with seating area.	door-open	500.0
29	Mini Bar	Fully stocked mini refrigerator with beverages and snacks, replenished daily.	wine-glass-alt	300.0
30	Room Service	24/7 room service with a wide selection of meals and refreshments.	bell	200.0
\.

--
-- Data for Name: booking; Type: TABLE DATA; Schema: public; Owner: (Render default)
--

COPY public.booking (id, user_id, room_id, check_in_date, check_out_date, num_guests, total_price, status, payment_method, payment_reference, payment_screenshot, payment_status, created_at, approved_by, approved_at, rejected_by, rejected_at, cancellation_reason, cancelled_at, rejection_reason) FROM stdin;
77	29	7	2025-07-11	2025-07-12	1	1500	rejected	pay_on_site	\N	\N	pending	2025-07-11 10:55:15	\N	\N	4	2025-07-11 13:04:55	\N	\N	\N
78	29	8	2025-07-11	2025-07-12	1	2450	rejected	pay_on_site	\N	\N	pending	2025-07-11 11:03:24	\N	\N	4	2025-07-16 18:22:11	\N	\N	\N
79	29	7	2025-07-16	2025-07-17	1	1816.5	rejected	pay_on_site	\N	\N	pending	2025-07-11 11:08:30	\N	\N	\N	\N	\N	\N	\N
80	29	9	2025-07-01	2025-07-02	1	5000	completed	pay_on_site	\N	\N	pending	2025-07-11 11:10:16	4	2025-07-11 12:26:55	\N	\N	\N	\N	\N
81	29	7	2025-07-09	2025-07-11	1	1500	cancelled	pay_on_site	\N	\N	pending	2025-07-11 13:05:09	4	2025-07-11 13:56:04	\N	\N	Cancel it	2025-07-11 22:05:34	\N
82	29	7	2025-07-26	2025-07-27	1	1500	completed	pay_on_site	\N	\N	pending	2025-07-11 14:01:46	4	2025-07-11 18:02:26	\N	\N	\N	\N	\N
88	30	8	2025-07-16	2025-07-17	1	3500	completed	pay_on_site	\N	\N	pending	2025-07-16 11:14:06	4	2025-07-16 11:14:27	\N	\N	\N	\N	\N
89	31	7	2025-07-16	2025-07-17	1	1500	completed	pay_on_site	\N	\N	pending	2025-07-16 11:24:26	4	2025-07-16 11:24:34	\N	\N	\N	\N	\N
90	31	9	2025-07-01	2025-07-02	1	5000	completed	pay_on_site	\N	\N	pending	2025-07-16 18:22:30	4	2025-07-16 18:22:37	\N	\N	\N	\N	\N
91	31	11	2025-08-23	2025-08-24	1	5000	completed	pay_on_site	\N	\N	pending	2025-08-22 23:06:01	4	2025-08-22 23:07:00	\N	\N	\N	\N	\N
105	31	11	2025-08-27	2025-08-28	1	5000	rejected	pay_on_site	\N	\N	pending	2025-08-27 10:26:27	\N	\N	4	2025-08-27 10:33:56	hehe	\N	hehe
106	31	8	2025-08-29	2025-08-30	1	3500	completed	pay_on_site	\N	\N	pending	2025-08-29 14:11:32	4	2025-08-29 14:12:10	\N	\N	\N	\N	\N
107	31	9	2025-09-24	2025-09-25	1	5000	completed	pay_on_site	\N	\N	pending	2025-09-24 10:00:02	4	2025-09-24 10:13:40	\N	\N	\N	\N	\N
110	31	7	2025-09-25	2025-09-26	1	1800	completed	pay_on_site	\N	\N	pending	2025-09-24 21:06:26	4	2025-09-24 21:06:49	\N	\N	\N	\N	\N
112	31	11	2025-09-29	2025-09-30	1	5650	pending	pay_on_site	\N	\N	pending	2025-09-29 04:32:28	\N	\N	\N	\N	\N	\N	\N
\.

--
-- Data for Name: booking_amenity; Type: TABLE DATA; Schema: public; Owner: (Render default)
--

COPY public.booking_amenity (booking_id, amenity_id) FROM stdin;
79	27
79	29
82	29
110	29
112	27
112	28
\.

--
-- Data for Name: comment; Type: TABLE DATA; Schema: public; Owner: (Render default)
--

COPY public.comment (id, user_id, booking_id, content, rating, created_at) FROM stdin;
5	3	59	Good hotel.	4	2025-05-11 12:03:37
15	31	90	Good hotel	4	2025-07-17 11:50:01
16	31	89	Nice!	3	2025-07-17 23:37:58
\.

--
-- Data for Name: eatnrun_rating; Type: TABLE DATA; Schema: public; Owner: (Render default)
--

COPY public.eatnrun_rating (id, rating, comment, created_at, updated_at, order_id) FROM stdin;
13	5	Very Good!	2025-07-17 21:35:39	2025-07-17 22:00:22	51
14	4	Good Restaurant	2025-07-17 22:00:35	2025-07-17 22:00:35	50
15	5	SAD	2025-07-17 22:16:48	2025-07-17 22:16:48	12
16	4	HEHE	2025-08-22 22:52:21	2025-08-22 22:52:21	82
17	4	Yes!	2025-08-23 11:36:34	2025-08-23 11:39:10	92
18	5	Good Food	2025-08-23 12:45:30	2025-08-23 12:45:30	97
19	4	Tongits 	2025-08-29 22:19:26	2025-08-29 22:19:26	99
\.

--
-- Data for Name: gallery_image; Type: TABLE DATA; Schema: public; Owner: (Render default)
--

COPY public.gallery_image (id, filename, title, description, category, created_at, is_homepage) FROM stdin;
2	1746965234_suiteroom.jpg	Full of Amenities	Amenities including wifi, bathtub and more.	room	2025-05-11 11:51:35	f
3	1746964333_romanticgetaway.jpg	Comfortable Hotel	We offer a comfortable hotel to stay in.	room	2025-05-11 11:52:13	f
\.

--
-- Data for Name: home_page_image; Type: TABLE DATA; Schema: public; Owner: (Render default)
--

COPY public.home_page_image (id, filename, created_at, "order") FROM stdin;
1	1752662237_HomepageImage.png	2025-07-11 09:28:08	0
2	1752662307_discount.jpg	2025-07-11 09:28:15	1
3	1752226101_descriptionimage.jpg	2025-07-11 09:28:21	1
\.

--
-- Data for Name: home_page_settings; Type: TABLE DATA; Schema: public; Owner: (Render default)
--

COPY public.home_page_settings (id, carousel_interval) FROM stdin;
1	3
\.

--
-- Data for Name: notification; Type: TABLE DATA; Schema: public; Owner: (Render default)
--

COPY public.notification (id, user_id, title, message, type, is_read, created_at) FROM stdin;
149	3	Booking Created	Your booking for Room 101 has been submitted and is pending approval. (Booking ID: 56)	booking	f	2025-05-11 11:52:50
151	3	Booking Approved	Your booking for Room 101 has been approved! (Booking ID: 56)	booking	f	2025-05-11 11:53:02
153	3	Booking Created	Your booking for Room 201 has been submitted and is pending approval. (Booking ID: 57)	booking	f	2025-05-11 11:53:24
155	3	Booking Rejected	Your booking for Room 201 has been rejected. (Booking ID: 57)	booking	f	2025-05-11 11:53:32
157	3	Booking Created	Your booking for Room 301 has been submitted and is pending approval. (Booking ID: 58)	booking	f	2025-05-11 11:53:58
159	3	Booking Approved	Your booking for Room 301 has been approved! (Booking ID: 58)	booking	f	2025-05-11 11:54:06
161	3	Booking Cancelled	Your booking for Room 301 has been cancelled. (Booking ID: 58)	booking	f	2025-05-11 11:54:29
163	3	Booking Approved	Your booking for Room 401 has been approved! (Booking ID: 59)	booking	t	2025-05-11 11:58:26
\.

--
-- Data for Name: promo; Type: TABLE DATA; Schema: public; Owner: (Render default)
--

COPY public.promo (id, title, description, image, start_date, end_date, is_active, validity, created_at, discount_percentage) FROM stdin;
4	Family Getaway	Book a family suite and get free breakfast for 4!	promos/promo_1752481806_deluxeroom.jpg	2025-07-01	2025-09-30	t	2025-07-14 16:29:47	15
5	Summer Splash!	Enjoy a refreshing summer stay with 20% off on all rooms!	promos/promo_1752481828_descriptionimage.jpg	2025-06-01	2025-08-31	t	2025-07-14 16:29:47	20
6	VIP Member Special	Exclusive 30% discount for VIP members only.	promos/promo_1752481851_vipmembership.jpg	2025-01-01	2025-12-31	t	2025-07-14 16:29:47	30
\.

--
-- Data for Name: room; Type: TABLE DATA; Schema: public; Owner: (Render default)
--

COPY public.room (id, room_number, floor, is_available, room_type_id, occupancy_limit, image) FROM stdin;
7	101	1	t	1	2	room_images/room_20250511_194904_discount.jpg
8	201	2	t	4	3	room_images/room_20250511_194923_vipmembership.jpg
9	301	3	t	7	4	room_images/room_20250511_194939_AccomodationsImage.jpg
11	401	4	t	7	2	room_images/room_20250511_194953_descriptionimage.jpg
\.

--
-- Data for Name: room_amenities; Type: TABLE DATA; Schema: public; Owner: (Render default)
--

COPY public.room_amenities (room_id, amenity_id) FROM stdin;
7	27
7	29
8	29
9	29
11	26
11	27
11	28
11	29
11	30
\.

--
-- Data for Name: room_type; Type: TABLE DATA; Schema: public; Owner: (Render default)
--

COPY public.room_type (id, name, description, price_per_night) FROM stdin;
1	Standard Room	A cozy room for two.	1500
4	Family Room	Comfortable room with two queen beds, designed to accommodate families with children. Features child-friendly amenities and extra space.	3500
7	Deluxe Suite	A spacious suite with premium furnishings, king-size bed, and panoramic views of the city skyline. Perfect for couples seeking luxury.	5000
8	Mega Family 	Comfortable room with two queen beds, designed to accommodate families with children. Features child-friendly amenities and extra space.	3500
\.

--
-- Data for Name: "user"; Type: TABLE DATA; Schema: public; Owner: (Render default)
--

COPY public."user" (id, name, email, phone, password, profile_pic, is_admin, created_at, email_verified, email_verification_token, email_verification_sent_at, verification_token, id_picture, registration_status, id_type) FROM stdin;
4	Fawna Hotel	fawnahotel@gmail.com	+639475448982	pbkdf2:sha256:260000$XidbJxMsLeMw72H2$131c694ac2702be3b1ed6dfa832c419f71cb7147a195e19e0a8bdc6f7a1774f5	images/profiles/profile_4_1756287449_fawna.png	t	2025-05-08 03:10:49	t	\N	\N	\N	\N	pending	\N
29	Jessie Rex Sacluti Somogod Jr.	somogodjessierex12@gmail.com	+639754067938	pbkdf2:sha256:260000$DzqewXO7hpmqylz1$82b5b183f07fdaeafdb4fc226e25ea5063572226a45b524248b8883ca49bff69	images/profiles/profile_29_1752289850_me.jpg	f	2025-07-11 09:26:14	t	\N	\N	\N	ids/1752225974_me.jpg	approved	drivers_license
30	Brian Sandoval Garlando	paxleyaiden@gmail.com	+639673624454	pbkdf2:sha256:260000$YhissqIQdq8KdMtx$f959ee83b5fefe10e9e22d686257cc486a0297b513bdb091f756ce8144570418	\N	f	2025-07-16 05:32:59	t	\N	\N	\N	ids/1752643978_484901034_122209037672188872_4198655431084102122_n.jpg	approved	drivers_license
31	Jhune Vincent Aquino Roces	jhunevincentaquinoroces@gmail.com	+639475448982	pbkdf2:sha256:260000$eAolSHaNM8odgJOv$1e140f4d5e256a5e1c21e1382ac98463b2422985d591a46e94c0c2bf0db00d60	images/profiles/profile_31_1758743444_IMG20250925025558.jpg	f	2025-07-16 11:23:52	t	\N	\N	\N	ids/1752665031_slide1.jpg	approved	passport
\.

--
-- Foreign Key Constraints
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.room(id);

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public."user"(id);

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_rejected_by_fkey FOREIGN KEY (rejected_by) REFERENCES public."user"(id);

ALTER TABLE ONLY public.booking_amenity
    ADD CONSTRAINT booking_amenity_amenity_id_fkey FOREIGN KEY (amenity_id) REFERENCES public.amenity(id);

ALTER TABLE ONLY public.booking_amenity
    ADD CONSTRAINT booking_amenity_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.booking(id);

ALTER TABLE ONLY public.promo_rooms
    ADD CONSTRAINT promo_rooms_promo_id_fkey FOREIGN KEY (promo_id) REFERENCES public.promo(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.promo_rooms
    ADD CONSTRAINT promo_rooms_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.room(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.promo_room_types
    ADD CONSTRAINT promo_room_types_promo_id_fkey FOREIGN KEY (promo_id) REFERENCES public.promo(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.promo_room_types
    ADD CONSTRAINT promo_room_types_room_type_id_fkey FOREIGN KEY (room_type_id) REFERENCES public.room_type(id) ON DELETE CASCADE;

--
-- PostgreSQL database dump complete
--
