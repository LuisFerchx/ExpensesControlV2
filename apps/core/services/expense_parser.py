import os
import re
from google import genai
from google.genai import types
from datetime import datetime
from django.conf import settings

def parse_expense_from_email_llm(email_body, email_date_str):
    """
    Uses Gemini LLM to parse the merchant, amount, and date from the email body.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY environment variable not found. Falling back to regex.")
        return parse_expense_from_email_regex(email_body, email_date_str)
        
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        Extract the following information from the bank transaction email below.
        Return ONLY a JSON object with strictly these keys:
        - "merchant": The name of the commerce or merchant where the purchase was made. If not found, use "Desconocido".
        - "amount": The transaction amount as a float number strictly (e.g. 15.50). Do not include currency symbols. If not found, use 0.0.
        
        If the email does not seem to contain an expense transaction, return empty values.
        
        Email text:
        {email_body}
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        
        # Parse the JSON response
        import json
        try:
            result = json.loads(response.text)
            
            # The date from headers is usually reliable enough, but needs parsing
            # Format: 'Tue, 24 Oct 2023 18:35:42 -0500'
            parsed_date = parse_email_date(email_date_str)
            
            return {
                "merchant": result.get("merchant", "Comercio Desconocido"),
                "amount": float(result.get("amount", 0.0)),
                "date": parsed_date
            }
        except json.JSONDecodeError:
             print(f"Failed to parse LLM JSON: {response.text}")
             return parse_expense_from_email_regex(email_body, email_date_str)
             
    except Exception as e:
        print(f"Error using Gemini API: {e}")
        return parse_expense_from_email_regex(email_body, email_date_str)


def parse_expense_from_email_regex(email_body, email_date_str):
    """
    Fallback regex-based parser. Banks have varied formats, so this is a simplified example.
    """
    # Try to find currency amounts like $15.50 or s/ 15.00 or USD 15
    amount = 0.0
    amount_match = re.search(r'(?:S/|\$|USD)\s*(\d+(?:\.\d{2})?)', email_body, re.IGNORECASE)
    if amount_match:
        try:
            amount = float(amount_match.group(1))
        except ValueError:
            pass
            
    # Try to find generic merchant phrases (very brittle)
    merchant = "Comercio Desconocido (Regex)"
    # Example for some latam banks
    merchant_match = re.search(r'(?:en el comercio|establecimiento)\s+([^.\n]+)', email_body, re.IGNORECASE)
    if merchant_match:
        merchant = merchant_match.group(1).strip()
        
    date_obj = parse_email_date(email_date_str)
    
    return {
        "merchant": merchant,
        "amount": amount,
        "date": date_obj
    }

def parse_email_date(date_str):
    """Parses standard email Date header into a Python date object."""
    from email.utils import parsedate_to_datetime
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.date()
    except Exception:
        return datetime.now().date()
