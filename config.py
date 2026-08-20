"""Central configuration for the incident analysis platform."""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
SRC_DIR = BASE_DIR / "src"
DASHBOARD_DIR = BASE_DIR / "dashboard"
SCRIPTS_DIR = BASE_DIR / "scripts"

RANDOM_SEED = 42
CORRELATION_WINDOW_MINUTES = 5
HAS_REAL_TIMESTAMPS = False

NSL_KDD_COLUMNS = [
    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
    "root_shell",
    "su_attempted",
    "num_root",
    "num_file_creations",
    "num_shells",
    "num_access_files",
    "num_outbound_cmds",
    "is_host_login",
    "is_guest_login",
    "count",
    "srv_count",
    "serror_rate",
    "srv_serror_rate",
    "rerror_rate",
    "srv_rerror_rate",
    "same_srv_rate",
    "diff_srv_rate",
    "srv_diff_host_rate",
    "dst_host_count",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
    "label",
    "difficulty",
]

ATTACK_CATEGORY_MAP = {
    "normal": "normal",
    "back": "DoS",
    "land": "DoS",
    "neptune": "DoS",
    "pod": "DoS",
    "smurf": "DoS",
    "teardrop": "DoS",
    "mailbomb": "DoS",
    "apache2": "DoS",
    "processtable": "DoS",
    "udpstorm": "DoS",
    "worm": "DoS",
    "ipsweep": "Probe",
    "nmap": "Probe",
    "portsweep": "Probe",
    "satan": "Probe",
    "mscan": "Probe",
    "saint": "Probe",
    "guess_passwd": "R2L",
    "ftp_write": "R2L",
    "imap": "R2L",
    "phf": "R2L",
    "multihop": "R2L",
    "warezmaster": "R2L",
    "warezclient": "R2L",
    "spy": "R2L",
    "xlock": "R2L",
    "xsnoop": "R2L",
    "snmpguess": "R2L",
    "snmpgetattack": "R2L",
    "httptunnel": "R2L",
    "sendmail": "R2L",
    "named": "R2L",
    "buffer_overflow": "U2R",
    "loadmodule": "U2R",
    "perl": "U2R",
    "rootkit": "U2R",
    "ps": "U2R",
    "sqlattack": "U2R",
    "xterm": "U2R",
}

HIGH_RISK_SERVICES = {
    "ftp",
    "ftp_data",
    "telnet",
    "rlogin",
    "rsh",
    "smtp",
    "imap",
    "pop3",
    "private",
    "http",
    "ssh",
    "finger",
}

PREPROCESSOR_ARTIFACT_PATH = MODELS_DIR / "preprocessor.joblib"
SCALER_PATH = MODELS_DIR / "scaler.joblib"
BINARY_MODEL_PATH = MODELS_DIR / "binary_rf.joblib"
MULTICLASS_MODEL_PATH = MODELS_DIR / "multiclass_rf.joblib"
ISOLATION_MODEL_PATH = MODELS_DIR / "isolation_forest.joblib"
MODEL_EVALUATION_PATH = REPORTS_DIR / "model_evaluation.json"
CONFUSION_MATRIX_PATH = REPORTS_DIR / "confusion_matrix.png"

for directory in [
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    MODELS_DIR,
    REPORTS_DIR,
    NOTEBOOKS_DIR,
    SRC_DIR,
    DASHBOARD_DIR,
    SCRIPTS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)
