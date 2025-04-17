# File Name : data_Cleaner.py
# Student Name: Daquan Daniels
# email:  danieldu@mail.uc.edu
# Assignment Number: Assignment 11
# Due Date:   04/17/2025
# Course #/Section:   IS4010-001
# Semester/Year:   Spring 2025
# Brief Description of the assignment: data?cleaning project that fixes missing ZIP codes in the first five addresses.

# Brief Description of what this module does: Cleans data by formatting prices, removing duplicates, filtering "Pepsi" rows, and patching missing ZIPs.
# Citations: chatgpt.com 
# Anything else that's relevant:

# -*- coding: utf-8 -*-
"""
Cleans the IS4010 fuel?purchase CSV according to Assignment 11.

@param None
@return None
"""

from __future__ import annotations
from pathlib import Path
import re
import pandas as pd
from cleaning_Package.zip_Service import CZipService


class CFuelDataCleaner:
    """
    End?to?end ETL: duplicates, Pepsi rows, price formatting, ZIP fixes.

    @param p_src_csv:          Path to raw CSV (in data_Package/).
    @param o_zip_svc:          CZipService instance.
    @param i_max_zip_lookups:  Only patch the first N missing ZIPs.
    @return CFuelDataCleaner
    """

    rgx_zip: re.Pattern[str] = re.compile(r"\b\d{5}\b")

    # ------------------------------------------------------------------ #
    def __init__(
        self,
        p_src_csv: Path,
        o_zip_svc: CZipService,
        i_max_zip_lookups: int = 5,
    ) -> None:
        """
        Constructor sets paths and config.

        @param p_src_csv:          Raw CSV path.
        @param o_zip_svc:          Zip?code service object.
        @param i_max_zip_lookups:  Number of ZIP rows to patch.
        @return None
        """
        self.p_src_csv: Path = p_src_csv
        self.o_zip_svc: CZipService = o_zip_svc
        self.i_max_zip_lookups: int = i_max_zip_lookups

        self.p_data_dir: Path = p_src_csv.parent   # data_Package/
        self.str_clean: str = "cleanedData.csv"
        self.str_anom: str = "dataAnomalies.csv"

    # ------------------------------------------------------------------ #
    def f_run(self) -> None:
        """
        Execute the entire cleaning workflow.

        @param None
        @return None
        """
        df_raw: pd.DataFrame = pd.read_csv(self.p_src_csv)

        df_work: pd.DataFrame = self._f_round_prices(df_raw)
        df_work = self._f_drop_duplicates(df_work)
        df_work, df_anom = self._f_split_pepsi(df_work)

        df_anom.to_csv(self.p_data_dir / self.str_anom, index=False)

        df_work = self._f_patch_missing_zips(df_work)
        df_work.to_csv(self.p_data_dir / self.str_clean, index=False)

        print("? Cleaning complete ?", self.p_data_dir.resolve())

    # --------------------- helper methods ----------------------------- #
    @staticmethod
    def _f_round_prices(df_in: pd.DataFrame) -> pd.DataFrame:
        """
        Force *Gross Price* to a fixed 2?decimal string.

        @param df_in: DataFrame
        @return DataFrame
        """
        df_in["Gross Price"] = (
            df_in["Gross Price"]
            .astype(float)
            .round(2)
            .apply(lambda f_val: f"{f_val:.2f}")
        )
        return df_in

    @staticmethod
    def _f_drop_duplicates(df_in: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate rows.

        @param df_in: DataFrame
        @return DataFrame
        """
        return df_in.drop_duplicates()

    @staticmethod
    def _f_split_pepsi(
        df_in: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Separate rows whose Fuel Type contains 'Pepsi'.

        @param df_in: DataFrame
        @return (df_without_pepsi, df_pepsi_rows)
        """
        b_mask = df_in["Fuel Type"].str.contains("Pepsi", case=False, na=False)
        return df_in.loc[~b_mask].copy(), df_in.loc[b_mask].copy()

    # -------------------- ZIP?code logic ------------------------------ #
    def _f_patch_missing_zips(self, df_in: pd.DataFrame) -> pd.DataFrame:
        """
        Patch the first N addresses missing ZIP codes.

        @param df_in: DataFrame
        @return DataFrame
        """
        df_missing = df_in[~df_in["Full Address"].str.contains(self.rgx_zip, na=False)]

        for i_idx, str_addr in df_missing.head(self.i_max_zip_lookups)["Full Address"].items():
            str_city, str_state = self._t_infer_city_state(str_addr)
            if not str_city or not str_state:
                continue
            str_zip = self.o_zip_svc.f_lookup_zip(str_city, str_state)
            if str_zip:
                df_in.at[i_idx, "Full Address"] = f"{str_addr.strip()} {str_zip}"

        return df_in

    # ------------------------------------------------------------------ #
    @staticmethod
    def _t_infer_city_state(str_addr: str) -> tuple[str | None, str | None]:
        """
        Extract (city, state) from an address like
        '123 Main St, Dayton, OH 45402'.

        @param str_addr: Address string
        @return (city, state) or (None, None)
        """
        v_parts = [p.strip() for p in str_addr.split(",")]
        if len(v_parts) >= 3:
            return v_parts[-2], v_parts[-1].split()[0]
        if len(v_parts) == 2:
            return v_parts[0], v_parts[1].split()[0]
        return None, None