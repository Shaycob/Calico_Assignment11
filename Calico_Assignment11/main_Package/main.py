# File Name : main.py
# Student Name: Jacob Farrell
# email:  farrelcj@mail.uc.edu
# Assignment Number: Assignment 11
# Due Date:   4/17/2025
# Course #/Section:   IS4010-001
# Semester/Year:   Spring 2025
#
# Brief Description of the assignment:  Clean a raw fuel‑purchase CSV by
#   deduplicating rows, removing Pepsi purchases, rounding Gross Price
#   to two‑decimal strings, and patching the first five missing ZIP codes;
#   then write cleanedData.csv and dataAnomalies.csv to data_Package.
#
# Brief Description of what this module does:  Serves as the entry point:
#   creates CZipService with our API key, instantiates CFuelDataCleaner,
#   and calls f_run() so all rubric‑required tasks execute in one click.
#
# Citations:  Zipcodebase API docs – https://zipcodebase.com/documentation  
#             chatgpt.com

# Anything else that's relevant:

# -*- coding: utf-8 -*-
"""
Entry point for data‑cleaning.
"""

from pathlib import Path
from cleaning_Package.zip_Service import CZipService
from cleaning_Package.data_Cleaner import CFuelDataCleaner


def f_main() -> None:
    """
    Instantiate classes and execute the cleaner.

    @param None
    @return None
    """
    # ---------- user configuration -----------------------------------
    str_api_key: str = "f81790d0-1a16-11f0-9f71-178f8b79bd98"
    p_src_csv: Path = Path("data_Package/fuelPurchaseData.csv")
    # -----------------------------------------------------------------

    o_zip_svc: CZipService = CZipService(str_api_key)
    o_cleaner: CFuelDataCleaner = CFuelDataCleaner(
        p_src_csv=p_src_csv,
        o_zip_svc=o_zip_svc,
        i_max_zip_lookups=5,
    )
    o_cleaner.f_run()


if __name__ == "__main__":
    f_main()
