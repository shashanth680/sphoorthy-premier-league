import io

import pandas as pd
from fastapi import HTTPException

from ..supabase_client import supabase


COLUMN_MAP = {
    "Player Name": "name",
    "Roll Number": "roll_number",
    "Department": "department",
    "Year": "year",
    "Role": "role",
    "Batting Style": "batting_style",
    "Bowling Style": "bowling_style",
    "Mobile Number": "mobile_number",
    "Player Photo": "photo_url"
}


def clean_value(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def import_players(file_bytes: bytes, filename: str):

    filename_lower = filename.lower()

    try:

        if filename_lower.endswith(".csv"):

            dataframe = pd.read_csv(
                io.BytesIO(file_bytes)
            )

        elif filename_lower.endswith(
            (".xlsx", ".xls")
        ):

            dataframe = pd.read_excel(
                io.BytesIO(file_bytes)
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Only CSV and Excel files are supported"
            )

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to read the uploaded file"
        )

    dataframe.columns = [
        str(column).strip()
        for column in dataframe.columns
    ]

    required_columns = [
        "Player Name",
        "Roll Number",
        "Department",
        "Year",
        "Role"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Required columns are missing",
                "missing_columns": missing_columns
            }
        )

    total_rows = len(dataframe)

    imported = 0
    skipped = 0
    errors = []

    for index, row in dataframe.iterrows():

        row_number = index + 2

        name = clean_value(
            row.get("Player Name")
        )

        roll_number = clean_value(
            row.get("Roll Number")
        )

        if not name or not roll_number:

            skipped += 1

            errors.append(
                f"Row {row_number}: Player Name and Roll Number are required"
            )

            continue

        # Check duplicate roll number
        existing = (
            supabase
            .table("players")
            .select("id")
            .eq("roll_number", roll_number)
            .execute()
        )

        if existing.data:

            skipped += 1

            errors.append(
                f"Row {row_number}: Roll Number "
                f"{roll_number} already exists"
            )

            continue

        player_data = {
            "name": name,
            "roll_number": roll_number,
            "department": clean_value(
                row.get("Department")
            ),
            "year": clean_value(
                row.get("Year")
            ),
            "role": clean_value(
                row.get("Role")
            ),
            "batting_style": clean_value(
                row.get("Batting Style")
            ),
            "bowling_style": clean_value(
                row.get("Bowling Style")
            ),
            "mobile_number": clean_value(
                row.get("Mobile Number")
            ),
            "photo_url": clean_value(
                row.get("Player Photo")
            ),
            "base_price": None,
            "status": "AVAILABLE"
        }

        try:

            response = (
                supabase
                .table("players")
                .insert(player_data)
                .execute()
            )

            if response.data:
                imported += 1
            else:
                skipped += 1

                errors.append(
                    f"Row {row_number}: Failed to insert player"
                )

        except Exception as error:

            skipped += 1

            errors.append(
                f"Row {row_number}: {str(error)}"
            )

    return {
        "success": True,
        "total_rows": total_rows,
        "imported": imported,
        "skipped": skipped,
        "errors": errors
    }
