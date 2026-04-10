import streamlit as st
import re

st.set_page_config(page_title="Well API Formatter", page_icon="🛢️", layout="centered")

st.title("🛢️ Well API SQL Formatter")
st.caption("Paste API numbers and generate a SQL IN clause. Auto-detects API10 vs API14 based on digit count.")

# --- Inputs ---
raw_input = st.text_area(
    "API Numbers",
    placeholder="Paste API numbers here — one per line, or comma/space separated",
    height=200,
)

field_override = st.text_input(
    "Field name override (optional)",
    placeholder="Leave blank to auto-detect (API10 or API14)",
)

# --- Logic ---
def parse_apis(raw: str) -> list[str]:
    tokens = re.split(r"[\n,\s]+", raw.strip())
    return [re.sub(r"\D", "", t) for t in tokens if re.sub(r"\D", "", t)]

def build_clause(field: str, apis: list[str]) -> str:
    lines = ",\n".join(f"'{a}'" for a in apis)
    return f"{field} IN (\n{lines}\n)"

if raw_input.strip():
    apis = parse_apis(raw_input)

    if not apis:
        st.warning("No valid numbers found in the input.")
    else:
        is10 = [a for a in apis if len(a) == 10]
        is14 = [a for a in apis if len(a) == 14]
        other = [a for a in apis if len(a) not in (10, 14)]

        # Stats row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total valid", len(is10) + len(is14))
        if is10:
            col2.metric("API10", len(is10))
        if is14:
            col3.metric("API14", len(is14))
        if other:
            col4.metric("Skipped", len(other))

        # Warnings
        if other:
            st.warning(
                f"⚠️ {len(other)} entr{'y' if len(other) == 1 else 'ies'} skipped "
                f"(digit count not 10 or 14): {', '.join(other)}"
            )

        valid = [a for a in apis if len(a) in (10, 14)]

        # Build output
        if field_override.strip():
            output = build_clause(field_override.strip(), valid)
            detected = f"Field override: `{field_override.strip()}`"
        elif is10 and is14:
            output = build_clause("API10", is10) + "\n\n" + build_clause("API14", is14)
            detected = "Mixed — generated separate clauses for **API10** and **API14**"
        elif is10:
            output = build_clause("API10", is10)
            detected = "Detected: **API10**"
        elif is14:
            output = build_clause("API14", is14)
            detected = "Detected: **API14**"
        else:
            output = ""
            detected = ""

        if output:
            st.markdown(detected)
            st.code(output, language="sql")
