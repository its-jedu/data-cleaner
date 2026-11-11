import pandas as pd
import re

def load_file(path):
    if path.endswith('.csv'):
        return pd.read_csv(path)
    elif path.endswith(('.xlsx', '.xls')):
        return pd.read_excel(path)
    else:
        raise ValueError('Unsupported file type')

def _parse_mixed_date(val):
    if pd.isna(val):
        return pd.NaT
    # Excel serial number - handle int/float or numeric string
    try:
        # try numeric first
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            num = float(val)
        else:
            s_tmp = str(val).strip()
            # numeric string?
            if s_tmp.replace('.','',1).isdigit():
                num = float(s_tmp)
            else:
                raise ValueError
        return pd.to_datetime('1899-12-30') + pd.Timedelta(days=num)
    except Exception:
        pass
    s = str(val).strip()
    # common formats
    fmts = ['%d/%m/%Y','%d-%m-%Y','%d/%m/%y','%d-%m-%y','%d %m %Y','%d %m %y','%Y-%m-%d','%Y%m%d','%d%m%Y']
    for fmt in fmts:
        try:
            return pd.to_datetime(s, format=fmt, dayfirst=True)
        except Exception:
            continue
    # fallback
    try:
        return pd.to_datetime(s, errors='coerce', dayfirst=True)
    except Exception:
        return pd.NaT

def _normalize_phone(s):
    if pd.isna(s):
        return pd.NA
    s = re.sub(r'[\s\-()]+','', str(s))
    if not s.isdigit():
        return pd.NA
    # Pad leading zero for 10-digit Nigerian numbers
    if len(s) == 10:
        s = '0' + s
    # Convert +234... to 0...
    if s.startswith('234') and len(s) == 13:
        s = '0' + s[3:]
    return s

def clean_dataframe(df):
    df = df.copy()
    # Standardize column names
    df.columns = [re.sub(r'\s+', ' ', str(c)).strip().lower().replace(' ', '_') for c in df.columns]

    # Strip whitespace, keep original empties
    for col in df.select_dtypes(include='object').columns:
        # Use .str methods safely, skip NaN
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

    # Datetime normalization for likely date columns
    date_candidates = [c for c in df.columns if any(k in c for k in ['dob','date','birth','admitted','session'])]
    for col in date_candidates:
        # Only attempt if column is object or mixed
        if pd.api.types.is_string_dtype(df[col]) or df[col].dtype == 'object' or pd.api.types.is_numeric_dtype(df[col]):
            parsed = df[col].apply(_parse_mixed_date)
            # Keep parsed if at least 50% success
            if parsed.notna().sum() >= len(df) * 0.5:
                # For DOB-like columns store ISO date string for consistency
                if 'dob' in col or 'birth' in col:
                    df[col] = parsed.dt.strftime('%Y-%m-%d')
                else:
                    df[col] = parsed

    # Normalize phone-like columns
    phone_cols = [c for c in df.columns if 'telephone' in c or 'phone' in c or 'tel' in c]
    for col in phone_cols:
        df[col] = df[col].apply(_normalize_phone)

    # Standardize categorical case for specific columns
    cat_cols = [c for c in df.columns if c in ['sex','state','lga','entry_mode','marital_status','enrolment_status']]
    for col in cat_cols:
        df[col] = df[col].apply(lambda x: x.strip().upper() if isinstance(x, str) else x)

    # Normalize name columns to Title Case
    name_cols = [c for c in df.columns if c in ['next_of_kin','surname','first_name','middle_name']]
    for col in name_cols:
        df[col] = df[col].apply(lambda x: x.strip().title() if isinstance(x, str) else x)

    # Normalize enrolment_level - keep SPILL and numbers, store as string for consistency
    if 'enrolment_level' in df.columns:
        df['enrolment_level'] = df['enrolment_level'].apply(lambda x: str(x).strip() if pd.notna(x) else x)

    # No rows/columns are dropped - preserve full dataset
    return df

def save_file(df, out_path):
    if out_path.endswith('.csv'):
        df.to_csv(out_path, index=False)
    elif out_path.endswith(('.xlsx', '.xls')):
        df.to_excel(out_path, index=False)
    else:
        raise ValueError('Unsupported output type')
