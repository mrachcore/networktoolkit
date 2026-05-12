import html
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.log_analyzer import analyze_log_text, build_summary_text
from utils.network_tools import calculate_subnet, check_tcp_port, dns_lookup, run_ping, run_traceroute
from utils.system_info import get_process_list, get_resource_usage, get_system_overview


APP_DIR = Path(__file__).parent
LOGO_PATH = APP_DIR / "assets" / "logo.png"
GITHUB_URL = "https://github.com/mrachcore/networktoolkit"


st.set_page_config(
    page_title="Network Toolkit by mrachcore",
    page_icon="NT",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_custom_css():
    """Add a cyber/terminal-inspired visual style to Streamlit."""
    st.markdown(
        """
        <style>
        :root {
            --bg-main: #071019;
            --bg-card: rgba(12, 24, 36, 0.88);
            --cyan: #42f4ff;
            --blue: #3d8bfd;
            --purple: #9b5cff;
            --text-main: #e8f7ff;
            --text-muted: #8fb6c8;
            --border: rgba(66, 244, 255, 0.22);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(66, 244, 255, 0.10), transparent 30%),
                radial-gradient(circle at top right, rgba(155, 92, 255, 0.10), transparent 25%),
                linear-gradient(135deg, #05080d 0%, #071019 45%, #0b1320 100%);
            color: var(--text-main);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #060b12 0%, #0b1723 100%);
            border-right: 1px solid var(--border);
        }

        section[data-testid="stSidebar"] * {
            color: var(--text-main);
        }

        div[data-testid="stRadio"] label {
            background: rgba(66, 244, 255, 0.05);
            border: 1px solid rgba(66, 244, 255, 0.14);
            border-radius: 10px;
            padding: 0.45rem 0.75rem;
            margin: 0.15rem 0;
        }

        h1, h2, h3 {
            color: var(--text-main);
            letter-spacing: 0;
        }

        .main-header {
            padding: 1.2rem 0 0.7rem 0;
        }

        .main-title {
            font-size: 3rem;
            font-weight: 800;
            margin: 0;
            color: var(--text-main);
            text-shadow: 0 0 24px rgba(66, 244, 255, 0.28);
        }

        .subtitle {
            color: var(--cyan);
            font-size: 1.08rem;
            margin-top: 0.2rem;
        }

        .section-title {
            color: var(--cyan);
            font-size: 1.25rem;
            font-weight: 700;
            margin: 1.2rem 0 0.6rem 0;
            border-left: 3px solid var(--cyan);
            padding-left: 0.7rem;
        }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.1rem;
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
        }

        .metric-card {
            background: linear-gradient(145deg, rgba(12, 24, 36, 0.98), rgba(10, 18, 28, 0.92));
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1rem;
            min-height: 118px;
            box-shadow: inset 0 0 22px rgba(66, 244, 255, 0.035);
        }

        .metric-label {
            color: var(--text-muted);
            font-size: 0.84rem;
            text-transform: uppercase;
            letter-spacing: 0.04rem;
            margin-bottom: 0.35rem;
        }

        .metric-value {
            color: var(--text-main);
            font-size: 1.35rem;
            font-weight: 700;
            overflow-wrap: anywhere;
        }

        .banner {
            background: linear-gradient(90deg, rgba(66, 244, 255, 0.12), rgba(155, 92, 255, 0.10));
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1rem 1.15rem;
            color: var(--text-main);
        }

        .terminal-box {
            background: #02060a;
            border: 1px solid rgba(66, 244, 255, 0.28);
            border-radius: 12px;
            padding: 1rem;
            color: #b8fbff;
            font-family: "Consolas", "Courier New", monospace;
            font-size: 0.9rem;
            white-space: pre-wrap;
            overflow-x: auto;
            box-shadow: inset 0 0 28px rgba(66, 244, 255, 0.05);
        }

        .tag {
            display: inline-block;
            border: 1px solid rgba(66, 244, 255, 0.30);
            background: rgba(66, 244, 255, 0.07);
            border-radius: 999px;
            padding: 0.32rem 0.7rem;
            margin: 0.2rem 0.25rem 0.2rem 0;
            color: var(--text-main);
            font-size: 0.88rem;
        }

        .status-ok {
            color: #5dffb3;
            font-weight: 700;
        }

        .status-bad {
            color: #ff7b91;
            font-weight: 700;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: rgba(66, 244, 255, 0.18);
            background: rgba(12, 24, 36, 0.66);
            border-radius: 14px;
        }

        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, var(--cyan), var(--blue));
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(66, 244, 255, 0.15);
            border-radius: 12px;
        }

        a {
            color: var(--cyan) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, subtitle=None, description=None):
    """Reusable page header for consistent spacing."""
    subtitle_html = f"<div class='subtitle'>{html.escape(subtitle)}</div>" if subtitle else ""
    description_html = f"<p style='color:#8fb6c8; max-width: 850px;'>{html.escape(description)}</p>" if description else ""

    st.markdown(
        f"""
        <div class="main-header">
            <h1 class="main-title">{html.escape(title)}</h1>
            {subtitle_html}
            {description_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title):
    st.markdown(f"<div class='section-title'>{html.escape(title)}</div>", unsafe_allow_html=True)


def metric_card(label, value):
    """Small reusable dashboard metric card."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(label)}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def terminal_output(text):
    """Show command output in a terminal-like box."""
    safe_text = html.escape(text)
    st.markdown(f"<div class='terminal-box'>{safe_text}</div>", unsafe_allow_html=True)


def sidebar_navigation():
    """Create the fixed sidebar navigation."""
    with st.sidebar:
        logo_col, title_col = st.columns([1, 4], vertical_alignment="center")
        with logo_col:
            if LOGO_PATH.exists():
                st.image(str(LOGO_PATH), width=72)
        with title_col:
            st.markdown(
                """
                <h2 style="margin-bottom:0;">Network Toolkit</h2>
                <p style="margin-top:0; color:#42f4ff;">by mrachcore</p>
                """,
                unsafe_allow_html=True,
            )

        return st.radio(
            "Navigation",
            ["Dashboard", "Network Tools", "System Monitor", "Log Analyzer", "About"],
            label_visibility="collapsed",
        )


def dashboard_page():
    logo_col, header_col = st.columns([1, 6], vertical_alignment="center")
    with logo_col:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=120)
    with header_col:
        page_header(
            "Network Toolkit",
            "by mrachcore",
            "A local IT/network troubleshooting toolkit built with Python and Streamlit.",
        )

    st.markdown(
        """
        <div class="banner">
            <strong>Welcome.</strong> Use this local dashboard to run common network checks,
            inspect system health, and analyze log files without cloud services or paid APIs.
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_header("System Overview")
    overview = get_system_overview()

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Operating System", overview["operating_system"])
    with col2:
        metric_card("Hostname", overview["hostname"])
    with col3:
        metric_card("Local IP", overview["local_ip"])

    col4, col5 = st.columns(2)
    with col4:
        metric_card("Uptime", overview["uptime"])
    with col5:
        metric_card("Python Version", overview["python_version"])


def network_tools_page():
    page_header("Network Tools", "Local troubleshooting commands", "Run beginner-friendly network checks from one clean interface.")

    with st.container(border=True):
        section_header("Ping Tool")
        host = st.text_input("Host / Domain / IP", placeholder="example.com", key="ping_host")
        if st.button("Run Ping", key="run_ping"):
            terminal_output(run_ping(host))

    with st.container(border=True):
        section_header("DNS Lookup")
        domain = st.text_input("Domain", placeholder="github.com", key="dns_domain")
        if st.button("Resolve Domain", key="run_dns"):
            result = dns_lookup(domain)
            if result["success"]:
                st.success(f"{result['domain']} resolves to {result['ip']}")
            else:
                st.error(result["message"])

    with st.container(border=True):
        section_header("Traceroute / Tracert")
        trace_host = st.text_input("Trace target", placeholder="8.8.8.8", key="trace_host")
        if st.button("Run Traceroute", key="run_trace"):
            terminal_output(run_traceroute(trace_host))

    with st.container(border=True):
        section_header("Subnet Calculator")
        cidr = st.text_input("CIDR Network", placeholder="192.168.1.0/24", key="subnet_cidr")
        if st.button("Calculate Subnet", key="run_subnet"):
            result = calculate_subnet(cidr)
            if result["success"]:
                cols = st.columns(3)
                values = [
                    ("IP Version", result["version"]),
                    ("Network Address", result["network_address"]),
                    ("Netmask", result["netmask"]),
                    ("Broadcast", result["broadcast_address"]),
                    ("Total Addresses", result["total_addresses"]),
                    ("Usable Hosts", result["usable_hosts"]),
                    ("First Host", result["first_host"]),
                    ("Last Host", result["last_host"]),
                ]
                for index, (label, value) in enumerate(values):
                    with cols[index % 3]:
                        metric_card(label, value)
            else:
                st.error(result["message"])

    with st.container(border=True):
        section_header("TCP Port Checker")
        col1, col2 = st.columns([3, 1])
        with col1:
            port_host = st.text_input("Host", placeholder="scanme.nmap.org", key="port_host")
        with col2:
            port = st.number_input("Port", min_value=1, max_value=65535, value=80, key="port_number")

        if st.button("Check Port", key="run_port_check"):
            result = check_tcp_port(port_host, port)
            css_class = "status-ok" if result["open"] else "status-bad"
            st.markdown(f"<p class='{css_class}'>{html.escape(result['message'])}</p>", unsafe_allow_html=True)


def system_monitor_page():
    page_header("System Monitor", "Local laptop health", "Simple CPU, memory, disk, network, and process visibility using psutil.")

    usage = get_resource_usage()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CPU Usage", f"{usage['cpu_percent']}%")
        st.progress(int(usage["cpu_percent"]))
    with col2:
        st.metric("RAM Usage", f"{usage['memory_percent']}%")
        st.progress(int(usage["memory_percent"]))
        st.caption(f"{usage['memory_used']} GB / {usage['memory_total']} GB")
    with col3:
        st.metric("Disk Usage", f"{usage['disk_percent']}%")
        st.progress(int(usage["disk_percent"]))
        st.caption(f"{usage['disk_used']} GB / {usage['disk_total']} GB")

    section_header("Network Counters")
    col4, col5 = st.columns(2)
    with col4:
        metric_card("Data Sent", f"{usage['bytes_sent']} MB")
    with col5:
        metric_card("Data Received", f"{usage['bytes_received']} MB")

    section_header("Top Processes")
    process_data = pd.DataFrame(get_process_list())
    st.dataframe(process_data, use_container_width=True, hide_index=True)

    if st.button("Refresh System Data"):
        st.rerun()


def log_analyzer_page():
    page_header("Log Analyzer", "Upload .log or .txt files", "Find important lines, repeated IP addresses, and quick troubleshooting signals.")

    uploaded_file = st.file_uploader("Drag and drop a log or text file", type=["log", "txt"])

    if not uploaded_file:
        st.info("Upload a .log or .txt file to begin analysis.")
        return

    log_text = uploaded_file.read().decode("utf-8", errors="replace")
    analysis = analyze_log_text(log_text)
    keyword_counts = analysis["keyword_counts"]

    section_header("Log Statistics")
    cols = st.columns(5)
    metrics = [
        ("Total Lines", analysis["total_lines"]),
        ("ERROR", keyword_counts["ERROR"]),
        ("WARNING", keyword_counts["WARNING"]),
        ("FAILED", keyword_counts["FAILED"]),
        ("DENIED", keyword_counts["DENIED"]),
    ]
    for index, (label, value) in enumerate(metrics):
        with cols[index]:
            metric_card(label, value)

    section_header("Important Lines")
    if analysis["important_lines"]:
        for item in analysis["important_lines"][:80]:
            terminal_output(f"Line {item['line']}: {item['text']}")
        if len(analysis["important_lines"]) > 80:
            st.caption("Showing first 80 important lines to keep the app responsive.")
    else:
        st.success("No ERROR, WARNING, FAILED, or DENIED lines found.")

    col1, col2 = st.columns(2)
    with col1:
        section_header("Most Common IP Addresses")
        if analysis["common_ips"]:
            st.dataframe(pd.DataFrame(analysis["common_ips"], columns=["IP Address", "Count"]), hide_index=True, use_container_width=True)
        else:
            st.caption("No IPv4 addresses detected.")

    with col2:
        section_header("Most Common Words")
        if analysis["common_words"]:
            st.dataframe(pd.DataFrame(analysis["common_words"], columns=["Word", "Count"]), hide_index=True, use_container_width=True)
        else:
            st.caption("No common words detected.")

    summary_text = build_summary_text(analysis)
    st.download_button(
        "Download TXT Summary",
        data=summary_text,
        file_name="network_toolkit_log_summary.txt",
        mime="text/plain",
    )


def about_page():
    page_header("Network Toolkit", "by mrachcore", "A beginner-friendly local network operations dashboard with a professional finish.")

    st.markdown(
        """
        <div class="card">
            <p>
                Network Toolkit is a local web application written in Python with Streamlit.
                It is designed as a lightweight network operations dashboard for everyday
                IT troubleshooting on a normal laptop.
            </p>
            <p>
                The project combines common diagnostic tools in one interface: ping, DNS lookup,
                traceroute, subnet calculation, TCP port checking, system monitoring, process
                overview, and log analysis.
            </p>
            <p>
                It uses beginner-friendly Python modules such as socket, subprocess, ipaddress,
                platform, datetime, re, psutil, and pandas. No paid APIs, cloud services,
                databases, Docker, or external infrastructure are required.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_header("Skills")
    for tag in ["Python", "Streamlit", "Networking", "System Monitoring", "Log Analysis", "Automation", "Troubleshooting"]:
        st.markdown(f"<span class='tag'>{tag}</span>", unsafe_allow_html=True)

    section_header("GitHub")
    st.markdown(f"[View project repository]({GITHUB_URL})")


def main():
    apply_custom_css()
    selected_page = sidebar_navigation()

    if selected_page == "Dashboard":
        dashboard_page()
    elif selected_page == "Network Tools":
        network_tools_page()
    elif selected_page == "System Monitor":
        system_monitor_page()
    elif selected_page == "Log Analyzer":
        log_analyzer_page()
    elif selected_page == "About":
        about_page()


if __name__ == "__main__":
    main()
