--
-- PostgreSQL database dump
--

\restrict z577xRLszoIezFifLVaQdfiBb7S64c9sLxmXjNQr7HGbckGaF75GL1BAYys2eSb

-- Dumped from database version 16.10 (Debian 16.10-1.pgdg13+1)
-- Dumped by pg_dump version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)

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

ALTER TABLE IF EXISTS ONLY public.violations DROP CONSTRAINT IF EXISTS violations_rule_id_fkey;
ALTER TABLE IF EXISTS ONLY public.violations DROP CONSTRAINT IF EXISTS violations_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.reports DROP CONSTRAINT IF EXISTS reports_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.configurations DROP CONSTRAINT IF EXISTS configurations_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.anomaly_history DROP CONSTRAINT IF EXISTS anomaly_history_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.alerts DROP CONSTRAINT IF EXISTS alerts_rule_id_fkey;
ALTER TABLE IF EXISTS ONLY public.alerts DROP CONSTRAINT IF EXISTS alerts_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.activity_logs DROP CONSTRAINT IF EXISTS activity_logs_user_id_fkey;
DROP INDEX IF EXISTS public.ix_users_username;
DROP INDEX IF EXISTS public.ix_users_id;
DROP INDEX IF EXISTS public.ix_users_email;
DROP INDEX IF EXISTS public.ix_reports_id;
DROP INDEX IF EXISTS public.ix_api_tokens_id;
DROP INDEX IF EXISTS public.ix_alerts_id;
DROP INDEX IF EXISTS public.ix_agents_id;
DROP INDEX IF EXISTS public.ix_activity_logs_id;
ALTER TABLE IF EXISTS ONLY public.violations DROP CONSTRAINT IF EXISTS violations_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.schedules DROP CONSTRAINT IF EXISTS schedules_pkey;
ALTER TABLE IF EXISTS ONLY public.rules DROP CONSTRAINT IF EXISTS rules_pkey;
ALTER TABLE IF EXISTS ONLY public.reports DROP CONSTRAINT IF EXISTS reports_pkey;
ALTER TABLE IF EXISTS ONLY public.configurations DROP CONSTRAINT IF EXISTS configurations_pkey;
ALTER TABLE IF EXISTS ONLY public.api_tokens DROP CONSTRAINT IF EXISTS api_tokens_token_key;
ALTER TABLE IF EXISTS ONLY public.api_tokens DROP CONSTRAINT IF EXISTS api_tokens_pkey;
ALTER TABLE IF EXISTS ONLY public.anomaly_history DROP CONSTRAINT IF EXISTS anomaly_history_pkey;
ALTER TABLE IF EXISTS ONLY public.alerts DROP CONSTRAINT IF EXISTS alerts_pkey;
ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS ONLY public.agents DROP CONSTRAINT IF EXISTS agents_pkey;
ALTER TABLE IF EXISTS ONLY public.activity_logs DROP CONSTRAINT IF EXISTS activity_logs_pkey;
ALTER TABLE IF EXISTS public.violations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.schedules ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.rules ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.reports ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.configurations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.api_tokens ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.anomaly_history ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.alerts ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.agents ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.activity_logs ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.violations_id_seq;
DROP TABLE IF EXISTS public.violations;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.schedules_id_seq;
DROP TABLE IF EXISTS public.schedules;
DROP SEQUENCE IF EXISTS public.rules_id_seq;
DROP TABLE IF EXISTS public.rules;
DROP SEQUENCE IF EXISTS public.reports_id_seq;
DROP TABLE IF EXISTS public.reports;
DROP SEQUENCE IF EXISTS public.configurations_id_seq;
DROP TABLE IF EXISTS public.configurations;
DROP SEQUENCE IF EXISTS public.api_tokens_id_seq;
DROP TABLE IF EXISTS public.api_tokens;
DROP SEQUENCE IF EXISTS public.anomaly_history_id_seq;
DROP TABLE IF EXISTS public.anomaly_history;
DROP SEQUENCE IF EXISTS public.alerts_id_seq;
DROP TABLE IF EXISTS public.alerts;
DROP TABLE IF EXISTS public.alembic_version;
DROP SEQUENCE IF EXISTS public.agents_id_seq;
DROP TABLE IF EXISTS public.agents;
DROP SEQUENCE IF EXISTS public.activity_logs_id_seq;
DROP TABLE IF EXISTS public.activity_logs;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activity_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activity_logs (
    id integer NOT NULL,
    user_id integer,
    action character varying(255) NOT NULL,
    target character varying(255),
    description text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.activity_logs OWNER TO postgres;

--
-- Name: activity_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activity_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.activity_logs_id_seq OWNER TO postgres;

--
-- Name: activity_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activity_logs_id_seq OWNED BY public.activity_logs.id;


--
-- Name: agents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agents (
    id integer NOT NULL,
    hostname character varying NOT NULL,
    ip_address character varying,
    os character varying,
    version character varying,
    is_online boolean,
    last_checkin timestamp with time zone
);


ALTER TABLE public.agents OWNER TO postgres;

--
-- Name: agents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.agents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agents_id_seq OWNER TO postgres;

--
-- Name: agents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.agents_id_seq OWNED BY public.agents.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: alerts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alerts (
    id integer NOT NULL,
    agent_id integer,
    rule_id integer,
    message text NOT NULL,
    severity character varying(50),
    status character varying(50),
    created_at timestamp with time zone DEFAULT now(),
    resolved_at timestamp with time zone
);


ALTER TABLE public.alerts OWNER TO postgres;

--
-- Name: alerts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.alerts_id_seq OWNER TO postgres;

--
-- Name: alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.alerts_id_seq OWNED BY public.alerts.id;


--
-- Name: anomaly_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.anomaly_history (
    id integer NOT NULL,
    agent_id integer,
    baseline_score double precision,
    checked_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.anomaly_history OWNER TO postgres;

--
-- Name: anomaly_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.anomaly_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.anomaly_history_id_seq OWNER TO postgres;

--
-- Name: anomaly_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.anomaly_history_id_seq OWNED BY public.anomaly_history.id;


--
-- Name: api_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.api_tokens (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    token character varying(255) NOT NULL,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone
);


ALTER TABLE public.api_tokens OWNER TO postgres;

--
-- Name: api_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.api_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.api_tokens_id_seq OWNER TO postgres;

--
-- Name: api_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.api_tokens_id_seq OWNED BY public.api_tokens.id;


--
-- Name: configurations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.configurations (
    id integer NOT NULL,
    agent_id integer,
    config_type character varying,
    config_data json,
    last_updated timestamp with time zone DEFAULT now()
);


ALTER TABLE public.configurations OWNER TO postgres;

--
-- Name: configurations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.configurations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.configurations_id_seq OWNER TO postgres;

--
-- Name: configurations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.configurations_id_seq OWNED BY public.configurations.id;


--
-- Name: reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reports (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    type character varying(100),
    file_path character varying(255),
    generated_at timestamp with time zone DEFAULT now(),
    created_by integer
);


ALTER TABLE public.reports OWNER TO postgres;

--
-- Name: reports_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reports_id_seq OWNER TO postgres;

--
-- Name: reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reports_id_seq OWNED BY public.reports.id;


--
-- Name: rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rules (
    id integer NOT NULL,
    name character varying NOT NULL,
    description character varying,
    check_expression character varying,
    severity character varying,
    active boolean
);


ALTER TABLE public.rules OWNER TO postgres;

--
-- Name: rules_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rules_id_seq OWNER TO postgres;

--
-- Name: rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rules_id_seq OWNED BY public.rules.id;


--
-- Name: schedules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schedules (
    id integer NOT NULL,
    cron character varying,
    description character varying,
    active boolean,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.schedules OWNER TO postgres;

--
-- Name: schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schedules_id_seq OWNER TO postgres;

--
-- Name: schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.schedules_id_seq OWNED BY public.schedules.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying NOT NULL,
    is_active boolean,
    role character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: violations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.violations (
    id integer NOT NULL,
    agent_id integer,
    rule_id integer,
    message character varying,
    confidence_score double precision,
    detected_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.violations OWNER TO postgres;

--
-- Name: violations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.violations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.violations_id_seq OWNER TO postgres;

--
-- Name: violations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.violations_id_seq OWNED BY public.violations.id;


--
-- Name: activity_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_logs ALTER COLUMN id SET DEFAULT nextval('public.activity_logs_id_seq'::regclass);


--
-- Name: agents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agents ALTER COLUMN id SET DEFAULT nextval('public.agents_id_seq'::regclass);


--
-- Name: alerts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alerts ALTER COLUMN id SET DEFAULT nextval('public.alerts_id_seq'::regclass);


--
-- Name: anomaly_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anomaly_history ALTER COLUMN id SET DEFAULT nextval('public.anomaly_history_id_seq'::regclass);


--
-- Name: api_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.api_tokens ALTER COLUMN id SET DEFAULT nextval('public.api_tokens_id_seq'::regclass);


--
-- Name: configurations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configurations ALTER COLUMN id SET DEFAULT nextval('public.configurations_id_seq'::regclass);


--
-- Name: reports id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports ALTER COLUMN id SET DEFAULT nextval('public.reports_id_seq'::regclass);


--
-- Name: rules id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rules ALTER COLUMN id SET DEFAULT nextval('public.rules_id_seq'::regclass);


--
-- Name: schedules id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedules ALTER COLUMN id SET DEFAULT nextval('public.schedules_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: violations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.violations ALTER COLUMN id SET DEFAULT nextval('public.violations_id_seq'::regclass);


--
-- Data for Name: activity_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.activity_logs (id, user_id, action, target, description, created_at) FROM stdin;
\.


--
-- Data for Name: agents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.agents (id, hostname, ip_address, os, version, is_online, last_checkin) FROM stdin;
1	web-server-01	192.168.1.10	Ubuntu 22.04 LTS	1.0.0	t	2025-11-10 22:14:22.032646+00
2	db-server-01	192.168.1.11	Ubuntu 20.04 LTS	1.0.0	t	2025-11-10 22:09:22.03268+00
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
f620c806eaee
\.


--
-- Data for Name: alerts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alerts (id, agent_id, rule_id, message, severity, status, created_at, resolved_at) FROM stdin;
\.


--
-- Data for Name: anomaly_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.anomaly_history (id, agent_id, baseline_score, checked_at) FROM stdin;
\.


--
-- Data for Name: api_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.api_tokens (id, name, token, is_active, created_at, expires_at) FROM stdin;
\.


--
-- Data for Name: configurations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.configurations (id, agent_id, config_type, config_data, last_updated) FROM stdin;
\.


--
-- Data for Name: reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reports (id, title, type, file_path, generated_at, created_by) FROM stdin;
\.


--
-- Data for Name: rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rules (id, name, description, check_expression, severity, active) FROM stdin;
1	Ensure SSH root login is disabled	Prevent direct root login via SSH	sshd -T | grep -i 'permitrootlogin no'	high	t
2	Ensure SSH PermitEmptyPasswords is disabled	Disallow empty passwords	sshd -T | grep -i 'permitemptypasswords no'	high	t
3	Ensure ufw service is enabled	Enable ufw service at boot	systemctl is-enabled ufw	high	t
\.


--
-- Data for Name: schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schedules (id, cron, description, active, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, hashed_password, is_active, role, created_at, updated_at) FROM stdin;
1	admin	admin@baseline.local	$2b$12$MjTsHjJoTS3w.DmsVcYtsesFjdbCzQMxl0qW/oogI7eahZkeBZHC.	t	admin	2025-11-10 15:14:21.543+00	\N
2	operator	operator@baseline.local	$2b$12$ZATvFNYRQfpcSSy48uB93OTtTpdIORi9HfDFsSJwVRrD9/QLdxS1.	t	operator	2025-11-10 15:14:21.543+00	\N
3	viewer	viewer@baseline.local	$2b$12$RA1nXr96TWMBoaHUxCCWtuujbj8ck4XXRka4N7yIGXX/g1C1jhKEq	t	viewer	2025-11-10 15:14:21.543+00	\N
\.


--
-- Data for Name: violations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.violations (id, agent_id, rule_id, message, confidence_score, detected_at) FROM stdin;
\.


--
-- Name: activity_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.activity_logs_id_seq', 1, false);


--
-- Name: agents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.agents_id_seq', 2, true);


--
-- Name: alerts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.alerts_id_seq', 1, false);


--
-- Name: anomaly_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.anomaly_history_id_seq', 1, false);


--
-- Name: api_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.api_tokens_id_seq', 1, false);


--
-- Name: configurations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.configurations_id_seq', 1, false);


--
-- Name: reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reports_id_seq', 1, false);


--
-- Name: rules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rules_id_seq', 3, true);


--
-- Name: schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.schedules_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 3, true);


--
-- Name: violations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.violations_id_seq', 1, false);


--
-- Name: activity_logs activity_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_pkey PRIMARY KEY (id);


--
-- Name: agents agents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: alerts alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (id);


--
-- Name: anomaly_history anomaly_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anomaly_history
    ADD CONSTRAINT anomaly_history_pkey PRIMARY KEY (id);


--
-- Name: api_tokens api_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.api_tokens
    ADD CONSTRAINT api_tokens_pkey PRIMARY KEY (id);


--
-- Name: api_tokens api_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.api_tokens
    ADD CONSTRAINT api_tokens_token_key UNIQUE (token);


--
-- Name: configurations configurations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configurations
    ADD CONSTRAINT configurations_pkey PRIMARY KEY (id);


--
-- Name: reports reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_pkey PRIMARY KEY (id);


--
-- Name: rules rules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rules
    ADD CONSTRAINT rules_pkey PRIMARY KEY (id);


--
-- Name: schedules schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: violations violations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.violations
    ADD CONSTRAINT violations_pkey PRIMARY KEY (id);


--
-- Name: ix_activity_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_activity_logs_id ON public.activity_logs USING btree (id);


--
-- Name: ix_agents_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_agents_id ON public.agents USING btree (id);


--
-- Name: ix_alerts_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_alerts_id ON public.alerts USING btree (id);


--
-- Name: ix_api_tokens_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_api_tokens_id ON public.api_tokens USING btree (id);


--
-- Name: ix_reports_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reports_id ON public.reports USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: activity_logs activity_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: alerts alerts_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(id);


--
-- Name: alerts alerts_rule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_rule_id_fkey FOREIGN KEY (rule_id) REFERENCES public.rules(id);


--
-- Name: anomaly_history anomaly_history_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anomaly_history
    ADD CONSTRAINT anomaly_history_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(id);


--
-- Name: configurations configurations_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configurations
    ADD CONSTRAINT configurations_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(id);


--
-- Name: reports reports_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: violations violations_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.violations
    ADD CONSTRAINT violations_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(id);


--
-- Name: violations violations_rule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.violations
    ADD CONSTRAINT violations_rule_id_fkey FOREIGN KEY (rule_id) REFERENCES public.rules(id);


--
-- PostgreSQL database dump complete
--

\unrestrict z577xRLszoIezFifLVaQdfiBb7S64c9sLxmXjNQr7HGbckGaF75GL1BAYys2eSb

