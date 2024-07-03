--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2 (Homebrew)
-- Dumped by pg_dump version 16.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cluster_info; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cluster_info (
    user_id character varying NOT NULL,
    cluster integer NOT NULL,
    title character varying,
    description character varying
);


--
-- Name: lyrics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lyrics (
    lyrics text,
    url character varying
);


--
-- Name: not_found; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.not_found (
    name character varying,
    artist character varying,
    error character varying,
    url character varying NOT NULL,
    spot_id character varying
);


--
-- Name: oath_flow; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.oath_flow (
    user_id character varying NOT NULL,
    access_token character varying,
    token_type character varying,
    expires_in integer,
    scope character varying,
    expires_at bigint,
    refresh_token character varying
);


--
-- Name: open_ai_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.open_ai_data (
    url character varying NOT NULL,
    embedding public.vector,
    summary text,
    summary_embedding public.vector
);


--
-- Name: songs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.songs (
    url character varying NOT NULL,
    name character varying,
    artist character varying,
    spot_id character varying,
    cluster integer
);


--
-- Name: spotify_song_info; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spotify_song_info (
    spot_id character varying NOT NULL
);


--
-- Name: spotify_user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spotify_user (
    user_id character varying NOT NULL,
    display_name character varying
);


--
-- Name: user_songs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_songs (
    user_id character varying NOT NULL,
    url character varying NOT NULL
);


--
-- Name: cluster_info cluster_info_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cluster_info
    ADD CONSTRAINT cluster_info_pkey PRIMARY KEY (user_id, cluster);


--
-- Name: not_found incorrect_url_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.not_found
    ADD CONSTRAINT incorrect_url_unique UNIQUE (url);


--
-- Name: not_found not_found_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.not_found
    ADD CONSTRAINT not_found_pkey PRIMARY KEY (url);


--
-- Name: oath_flow oath_flow_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oath_flow
    ADD CONSTRAINT oath_flow_pkey PRIMARY KEY (user_id);


--
-- Name: open_ai_data open_ai_data_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.open_ai_data
    ADD CONSTRAINT open_ai_data_pkey PRIMARY KEY (url);


--
-- Name: songs songs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.songs
    ADD CONSTRAINT songs_pkey PRIMARY KEY (url);


--
-- Name: spotify_song_info spotify_info_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spotify_song_info
    ADD CONSTRAINT spotify_info_pkey PRIMARY KEY (spot_id);


--
-- Name: spotify_user spotify_user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spotify_user
    ADD CONSTRAINT spotify_user_pkey PRIMARY KEY (user_id);


--
-- Name: lyrics url_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lyrics
    ADD CONSTRAINT url_unique UNIQUE (url);


--
-- Name: user_songs user_songs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_songs
    ADD CONSTRAINT user_songs_pkey PRIMARY KEY (user_id, url);


--
-- Name: oath_flow fk_oath_spot_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oath_flow
    ADD CONSTRAINT fk_oath_spot_user FOREIGN KEY (user_id) REFERENCES public.spotify_user(user_id);


--
-- Name: lyrics lyrics_url_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lyrics
    ADD CONSTRAINT lyrics_url_fkey FOREIGN KEY (url) REFERENCES public.songs(url);


--
-- Name: open_ai_data open_ai_data_url_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.open_ai_data
    ADD CONSTRAINT open_ai_data_url_fkey FOREIGN KEY (url) REFERENCES public.songs(url);


--
-- Name: user_songs user_songs_url_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_songs
    ADD CONSTRAINT user_songs_url_fkey FOREIGN KEY (url) REFERENCES public.songs(url);


--
-- Name: user_songs user_songs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_songs
    ADD CONSTRAINT user_songs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.spotify_user(user_id);


--
-- PostgreSQL database dump complete
--

