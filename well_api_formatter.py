import streamlit as st
import re

st.set_page_config(page_title="Select by Attributes Generator", page_icon="🗺️", layout="centered")

st.title("🗺️ Select by Attributes Generator")
st.caption("Generate SQL IN clauses for API numbers and/or abstracts.")

# --- Helpers ---
def parse_values(raw: str) -> list[str]:
    tokens = re.split(r"[\n,\s]+", raw.strip())
    return [t.strip() for t in tokens if t.strip()]

def parse_apis(raw: str) -> list[str]:
    tokens = re.split(r"[\n,\s]+", raw.strip())
    return [re.sub(r"\D", "", t) for t in tokens if re.sub(r"\D", "", t)]

def strip_dashes(raw: str) -> str:
    return raw.replace("-", "")

def build_clause(field: str, values: list[str]) -> str:
    lines = ",\n".join(f"'{v}'" for v in values)
    return f"{field} IN (\n{lines}\n)"

# --- Session state init ---
if "api_input" not in st.session_state:
    st.session_state.api_input = ""
if "abstract_input" not in st.session_state:
    st.session_state.abstract_input = ""

# ── Section 1: API Numbers ───────────────────────────────────────────────────
col_title, col_btn = st.columns([6, 1])
col_title.subheader("API Numbers")
if col_btn.button("Clear", key="clear_api"):
    st.session_state.api_input = ""

raw_api = st.text_area(
    "API Numbers",
    placeholder="Paste API numbers here — one per line, or comma/space separated",
    height=180,
    label_visibility="collapsed",
    key="api_input",
)

field_override = st.text_input(
    "Field name override (optional)",
    placeholder="Leave blank to auto-detect (API10 or API14)",
)

if raw_api.strip():
    dashes_found = "-" in raw_api
    cleaned_api = strip_dashes(raw_api) if dashes_found else raw_api
    if dashes_found:
        st.info("Dashes detected and removed from API numbers.")
    apis = parse_apis(cleaned_api)

    if not apis:
        st.warning("No valid numbers found in the input.")
    else:
        is10 = [a for a in apis if len(a) == 10]
        is14 = [a for a in apis if len(a) == 14]
        other = [a for a in apis if len(a) not in (10, 14)]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total valid", len(is10) + len(is14))
        if is10:
            col2.metric("API10", len(is10))
        if is14:
            col3.metric("API14", len(is14))
        if other:
            col4.metric("Skipped", len(other))

        if other:
            st.warning(
                f"⚠️ {len(other)} entr{'y' if len(other) == 1 else 'ies'} skipped "
                f"(digit count not 10 or 14): {', '.join(other)}"
            )

        valid = [a for a in apis if len(a) in (10, 14)]

        if field_override.strip():
            api_output = build_clause(field_override.strip(), valid)
            detected = f"Field override: `{field_override.strip()}`"
        elif is10 and is14:
            api_output = build_clause("API10", is10) + "\n\n" + build_clause("API14", is14)
            detected = "Mixed — generated separate clauses for **API10** and **API14**"
        elif is10:
            api_output = build_clause("API10", is10)
            detected = "Detected: **API10**"
        elif is14:
            api_output = build_clause("API14", is14)
            detected = "Detected: **API14**"
        else:
            api_output = ""
            detected = ""

        if api_output:
            st.markdown(detected)
            st.code(api_output, language="sql")

st.divider()

# ── Section 2: Abstracts ─────────────────────────────────────────────────────
col_title2, col_btn2 = st.columns([6, 1])
col_title2.subheader("Abstracts")
if col_btn2.button("Clear", key="clear_abstract"):
    st.session_state.abstract_input = ""

raw_abstracts = st.text_area(
    "Abstract values",
    placeholder="Paste ABSTRACT_L values here — one per line, or comma/space separated",
    height=180,
    label_visibility="collapsed",
    key="abstract_input",
)

if raw_abstracts.strip():
    abstracts = parse_values(raw_abstracts)

    if not abstracts:
        st.warning("No values found in the input.")
    else:
        st.metric("Total", len(abstracts))
        abstract_output = build_clause("ABSTRACT_L", abstracts)
        st.code(abstract_output, language="sql")
