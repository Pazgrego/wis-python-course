"""
uniprot_client.py
-----------------
Handles all network communication with the UniProt REST API.
Business logic lives in analyzer.py — this module only fetches raw data.
"""

import requests

BASE_URL = "https://rest.uniprot.org/uniprotkb"


def fetch_protein(protein_id: str) -> dict:
    """
    Fetch protein data from the UniProt REST API.

    Args:
        protein_id: A valid UniProt accession ID (e.g. 'P69905').

    Returns:
        The raw JSON response as a Python dictionary.

    Raises:
        ValueError: If the protein ID is not found (HTTP 400/404).
        ConnectionError: If the network request fails entirely.
    """
    protein_id = protein_id.strip().upper()
    url = f"{BASE_URL}/{protein_id}.json"

    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Could not reach the UniProt API. "
            "Please check your internet connection."
        )
    except requests.exceptions.Timeout:
        raise ConnectionError(
            "The UniProt API request timed out. Please try again."
        )

    if response.status_code == 404:
        raise ValueError(
            f"Protein ID '{protein_id}' was not found in UniProt. "
            "Double-check the accession number and try again."
        )

    if response.status_code != 200:
        raise ValueError(
            f"UniProt returned an unexpected status code: {response.status_code}. "
            f"Response: {response.text[:200]}"
        )

    return response.json()
