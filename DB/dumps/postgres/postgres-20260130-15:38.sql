--
-- PostgreSQL database dump
--

\restrict UVsaisDP07qAGl2Fp1Gyjy9Gs55JWvXTqmirZ5ojmaKSKYeLJ802EQKPWlfbiCk

-- Dumped from database version 16.11 (Debian 16.11-1.pgdg13+1)
-- Dumped by pg_dump version 18.1

-- Started on 2026-01-30 15:38:29 CST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 215 (class 1259 OID 16388)
-- Name: tblfinishedgoods; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tblfinishedgoods (
    finishedgoodid uuid DEFAULT gen_random_uuid() NOT NULL,
    finishedgoodname character varying(150)
);


ALTER TABLE public.tblfinishedgoods OWNER TO postgres;

--
-- TOC entry 3455 (class 0 OID 0)
-- Dependencies: 215
-- Name: TABLE tblfinishedgoods; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.tblfinishedgoods IS 'Completed, accounted for items post-production line';


--
-- TOC entry 3456 (class 0 OID 0)
-- Dependencies: 215
-- Name: COLUMN tblfinishedgoods.finishedgoodid; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblfinishedgoods.finishedgoodid IS 'Primary Key for this table. UUID for items
CHECK TO BE SURE gen_random_UUID() IS WORKING!!!!!!';


--
-- TOC entry 3457 (class 0 OID 0)
-- Dependencies: 215
-- Name: COLUMN tblfinishedgoods.finishedgoodname; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblfinishedgoods.finishedgoodname IS 'Name for finished products sent across production line.';


--
-- TOC entry 216 (class 1259 OID 16392)
-- Name: tblproductiondata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tblproductiondata (
    finishedgoodid uuid NOT NULL,
    partsproduced integer DEFAULT '-1'::integer,
    productionstarttime timestamp without time zone,
    productionendtime timestamp without time zone,
    productionstartdate date,
    productionenddate date,
    orderid integer NOT NULL
);


ALTER TABLE public.tblproductiondata OWNER TO postgres;

--
-- TOC entry 3458 (class 0 OID 0)
-- Dependencies: 216
-- Name: TABLE tblproductiondata; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.tblproductiondata IS 'Metadata about production line, items produced, timing, etc...';


--
-- TOC entry 3459 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN tblproductiondata.finishedgoodid; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblproductiondata.finishedgoodid IS 'No default as it will inherit from PK in FinishedGoods table';


--
-- TOC entry 3460 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN tblproductiondata.partsproduced; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblproductiondata.partsproduced IS 'Default -1 for debugging. Indicates how many parts have been produced.';


--
-- TOC entry 3461 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN tblproductiondata.productionstarttime; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblproductiondata.productionstarttime IS 'Could be moved to not null. I am not sure exactly how sensors will send this data over, so for now, this will remain allowed to be null.';


--
-- TOC entry 3462 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN tblproductiondata.productionendtime; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblproductiondata.productionendtime IS 'Same as StartTime, but for ending.';


--
-- TOC entry 3463 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN tblproductiondata.orderid; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblproductiondata.orderid IS 'GENERATED ALWAYS AS IDENTITY to be an incrementing counter.';


--
-- TOC entry 220 (class 1259 OID 16446)
-- Name: tblproductiondata_orderid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.tblproductiondata ALTER COLUMN orderid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tblproductiondata_orderid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 217 (class 1259 OID 16397)
-- Name: tblproductioninventory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tblproductioninventory (
    finishedgoodid uuid NOT NULL,
    intavailableparts integer DEFAULT '-1'::integer
);


ALTER TABLE public.tblproductioninventory OWNER TO postgres;

--
-- TOC entry 3464 (class 0 OID 0)
-- Dependencies: 217
-- Name: TABLE tblproductioninventory; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.tblproductioninventory IS 'Available parts to be used for production';


--
-- TOC entry 3465 (class 0 OID 0)
-- Dependencies: 217
-- Name: COLUMN tblproductioninventory.finishedgoodid; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblproductioninventory.finishedgoodid IS 'Foreign key linking to tblfinishedgoods';


--
-- TOC entry 3466 (class 0 OID 0)
-- Dependencies: 217
-- Name: COLUMN tblproductioninventory.intavailableparts; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblproductioninventory.intavailableparts IS 'Stores number of available parts in inventory. Default is -1 for debugging';


--
-- TOC entry 218 (class 1259 OID 16401)
-- Name: tblsensorinfeeddata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tblsensorinfeeddata (
    sensorid uuid DEFAULT gen_random_uuid() NOT NULL,
    inventorycount integer,
    "TimeStamp" timestamp without time zone,
    productiondate date,
    orderid integer NOT NULL
);


ALTER TABLE public.tblsensorinfeeddata OWNER TO postgres;

--
-- TOC entry 3467 (class 0 OID 0)
-- Dependencies: 218
-- Name: TABLE tblsensorinfeeddata; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.tblsensorinfeeddata IS 'Data sent from sensors to be processed into other tables (align with InfluxDB if we move in that direction)
unsure how many of the columns in this table are correct as I''m not sure yet just how the sensors are going to send data, but I believe that it is up to our MicroPython dev.';


--
-- TOC entry 3468 (class 0 OID 0)
-- Dependencies: 218
-- Name: COLUMN tblsensorinfeeddata.orderid; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblsensorinfeeddata.orderid IS 'foreign key linked to orderid in tblproductiondata';


--
-- TOC entry 221 (class 1259 OID 16452)
-- Name: tblsensorinfeeddata_orderid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.tblsensorinfeeddata ALTER COLUMN orderid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tblsensorinfeeddata_orderid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 219 (class 1259 OID 16433)
-- Name: tblusercredentials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tblusercredentials (
    userid uuid DEFAULT gen_random_uuid() NOT NULL,
    username character varying,
    password text,
    isadmin boolean DEFAULT false NOT NULL,
    canviewtables boolean DEFAULT false NOT NULL,
    canedittables boolean DEFAULT false NOT NULL,
    CONSTRAINT check_admin_permissions CHECK (((isadmin = true) OR ((canviewtables = false) AND (canedittables = false)))),
    CONSTRAINT tblusercredentials_usernotemail CHECK (((username)::text ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'::text))
);


ALTER TABLE public.tblusercredentials OWNER TO postgres;

--
-- TOC entry 3469 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN tblusercredentials.userid; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblusercredentials.userid IS 'These are IDs associated with users';


--
-- TOC entry 3470 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN tblusercredentials.username; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblusercredentials.username IS 'This is for usernames (which should always be emails)
I might convert this to ''citext'' type eventually for case insensitivity.';


--
-- TOC entry 3471 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN tblusercredentials.password; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblusercredentials.password IS 'This is for passwords, they are stored as text so we can hash them.';


--
-- TOC entry 3472 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN tblusercredentials.isadmin; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblusercredentials.isadmin IS 'This will determine whether the user has admin privileges or not.';


--
-- TOC entry 3473 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN tblusercredentials.canviewtables; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblusercredentials.canviewtables IS 'Whether or not the user can view database data';


--
-- TOC entry 3474 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN tblusercredentials.canedittables; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tblusercredentials.canedittables IS 'whether or not the user can edit database data';


--
-- TOC entry 3475 (class 0 OID 0)
-- Dependencies: 219
-- Name: CONSTRAINT check_admin_permissions ON tblusercredentials; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON CONSTRAINT check_admin_permissions ON public.tblusercredentials IS 'Ensure that isadmin must be true for canviewtables and canedittables to be true';


--
-- TOC entry 3476 (class 0 OID 0)
-- Dependencies: 219
-- Name: CONSTRAINT tblusercredentials_usernotemail ON tblusercredentials; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON CONSTRAINT tblusercredentials_usernotemail ON public.tblusercredentials IS 'The username is not formatted as an email.';


--
-- TOC entry 3295 (class 2606 OID 16406)
-- Name: tblfinishedgoods tblfinishedgoods_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tblfinishedgoods
    ADD CONSTRAINT tblfinishedgoods_pk PRIMARY KEY (finishedgoodid);


--
-- TOC entry 3297 (class 2606 OID 16451)
-- Name: tblproductiondata tblproductiondata_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tblproductiondata
    ADD CONSTRAINT tblproductiondata_pk PRIMARY KEY (orderid);


--
-- TOC entry 3299 (class 2606 OID 16410)
-- Name: tblproductioninventory tblproductioninventory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tblproductioninventory
    ADD CONSTRAINT tblproductioninventory_pkey PRIMARY KEY (finishedgoodid);


--
-- TOC entry 3301 (class 2606 OID 16412)
-- Name: tblsensorinfeeddata tblsensorinfeeddata_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tblsensorinfeeddata
    ADD CONSTRAINT tblsensorinfeeddata_pk PRIMARY KEY (sensorid);


--
-- TOC entry 3303 (class 2606 OID 16445)
-- Name: tblusercredentials tblusercredentials_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tblusercredentials
    ADD CONSTRAINT tblusercredentials_pk PRIMARY KEY (userid);


--
-- TOC entry 3304 (class 2606 OID 16413)
-- Name: tblproductiondata tblproductiondata_tblfinishedgoods_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tblproductiondata
    ADD CONSTRAINT tblproductiondata_tblfinishedgoods_fk FOREIGN KEY (finishedgoodid) REFERENCES public.tblfinishedgoods(finishedgoodid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3305 (class 2606 OID 16423)
-- Name: tblproductioninventory tblproductioninventory_tblfinishedgoods_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tblproductioninventory
    ADD CONSTRAINT tblproductioninventory_tblfinishedgoods_fk FOREIGN KEY (finishedgoodid) REFERENCES public.tblfinishedgoods(finishedgoodid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3306 (class 2606 OID 16457)
-- Name: tblsensorinfeeddata tblsensorinfeeddata_tblproductiondata_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tblsensorinfeeddata
    ADD CONSTRAINT tblsensorinfeeddata_tblproductiondata_fk FOREIGN KEY (orderid) REFERENCES public.tblproductiondata(orderid) ON UPDATE CASCADE ON DELETE CASCADE;


-- Completed on 2026-01-30 15:38:31 CST

--
-- PostgreSQL database dump complete
--

\unrestrict UVsaisDP07qAGl2Fp1Gyjy9Gs55JWvXTqmirZ5ojmaKSKYeLJ802EQKPWlfbiCk

