# File Name : zip_Service.py
# Student Name: Jacob Farrell
# email:  farrelcj@mail.uc.edu
# Assignment Number: Assignment 11
# Due Date:   4/17/2025
# Course #/Section:   4010-001
# Semester/Year:   Spring 2025
# Brief Description of the assignment:  Part of the same data‑cleaning
#   project that fixes missing ZIP codes in the first five addresses.
#
# Brief Description of the assignment:  Clean a raw fuel‑purchase CSV by
#   deduplicating rows, removing Pepsi purchases, rounding Gross Price
#   to two‑decimal strings, and patching the first five missing ZIP codes;
#   then write cleanedData.csv and dataAnomalies.csv to data_Package.
#
# Citations:  Zipcodebase API docs – https://zipcodebase.com/documentation  
#             Zippopotam.us API usage – http://www.zippopotam.us  
#             chatgpt.com

# Anything else that's relevant:

# -*- coding: utf-8 -*-
"""
Wraps the Zipcodebase REST API (and a free fallback) for ZIP look‑ups.

@param None
@return None
"""

from __future__ import annotations
import os
import requests


class CZipService:
    """
    Provide ZIP‑code look‑ups for U.S. cities.

    @param str_api_key:  Optional – Zipcodebase API key; reads ZIPBASE_KEY
                         from environment if omitted.
    @return CZipService
    """

    _STR_URL: str = "https://app.zipcodebase.com/api/v1/search"

    def __init__(self, str_api_key: str | None = None) -> None:
        """
        Store the API key.

        @param str_api_key: Key string or *None* to pull from env.
        @return None
        """
        self.str_api_key: str | None = str_api_key or os.getenv("ZIPBASE_KEY")

    # ------------------------------------------------------------------ #
    def f_lookup_zip(self, str_city: str, str_state: str) -> str | None:
        """
        Return the first ZIP code for (city, state) or None.

        @param str_city:  City name (e.g., 'Cincinnati')
        @param str_state: Two‑letter state code (e.g., 'OH')
        @return ZIP string (e.g., '45202') or None
        """
        # ---- 1) try Zipcodebase (needs key) ---------------------------
        if self.str_api_key:
            try:
                o_resp = requests.get(
                    self._STR_URL,
                    params={
                        "apikey": self.str_api_key,
                        "city": str_city,
                        "state": str_state,
                        "country": "US",
                    },
                    timeout=5,
                )
                o_resp.raise_for_status()
                v_results = o_resp.json().get("results") or []
                if v_results:
                    return v_results[0]["postal_code"]
            except Exception:
                pass  # silently fall through to fallback

        # ---- 2) fallback: zippopotam.us (no key) ----------------------
        try:
            o_resp = requests.get(
                f"https://api.zippopotam.us/us/{str_state}/{str_city}",
                timeout=5,
            )
            if o_resp.status_code == 200:
                return o_resp.json()["places"][0]["post code"]
        except Exception:
            pass
        return None
