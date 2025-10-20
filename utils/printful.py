"""
Printful API integration for calendar product creation
"""
import requests
import os
from pathlib import Path
from typing import List, Dict

class PrintfulAPI:
    def __init__(self, api_key=None):
        """Initialize Printful API client"""
        self.api_key = api_key or os.getenv('PRINTFUL_API_KEY')
        if not self.api_key:
            raise ValueError("Printful API key is required")

        self.base_url = "https://api.printful.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_store_info(self):
        """Get store information to verify API connection"""
        response = requests.get(
            f"{self.base_url}/store",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_products(self, category_id=None):
        """
        Get available products from Printful catalog

        Args:
            category_id: Optional category ID to filter products
        """
        params = {}
        if category_id:
            params['category_id'] = category_id

        response = requests.get(
            f"{self.base_url}/products",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_calendar_products(self):
        """Get calendar-specific products"""
        # Printful product IDs for calendars
        # Note: These IDs may need to be updated based on Printful's current catalog
        calendar_product_ids = [
            296,  # Wall Calendar (12x12)
            520,  # Desk Calendar
        ]

        products = []
        for product_id in calendar_product_ids:
            try:
                response = requests.get(
                    f"{self.base_url}/products/{product_id}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    products.append(response.json())
            except:
                continue

        return products

    def upload_image(self, image_path):
        """
        Upload image to Printful file library

        Args:
            image_path: Path to image file

        Returns:
            File ID from Printful
        """
        url = f"{self.base_url}/files"

        with open(image_path, 'rb') as f:
            files = {'file': f}
            # Remove Content-Type header for multipart upload
            headers = {"Authorization": f"Bearer {self.api_key}"}

            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()

            data = response.json()
            return data['result']['id']

    def create_calendar_product(
        self,
        image_paths: List[str],
        product_id: int = 296,  # Default: 12x12 Wall Calendar
        variant_id: int = None
    ):
        """
        Create a calendar product with uploaded images

        Args:
            image_paths: List of 12 calendar image paths (one per month)
            product_id: Printful product ID for calendar
            variant_id: Specific variant ID if known

        Returns:
            Created product information
        """
        if len(image_paths) != 12:
            raise ValueError("Calendar requires exactly 12 images (one per month)")

        # Upload all images first
        print("Uploading images to Printful...")
        file_ids = []
        for i, image_path in enumerate(image_paths, 1):
            print(f"  Uploading image {i}/12...")
            file_id = self.upload_image(image_path)
            file_ids.append(file_id)

        # Create product
        print("Creating calendar product...")

        # Get product variants to find the right one
        product_info = requests.get(
            f"{self.base_url}/products/{product_id}",
            headers=self.headers
        ).json()

        # Use first variant if not specified
        if not variant_id and product_info['result']['variants']:
            variant_id = product_info['result']['variants'][0]['id']

        # Create mockup generator request
        # This creates a visual mockup of the calendar
        mockup_data = {
            "variant_ids": [variant_id],
            "format": "jpg",
            "files": [{"id": file_id} for file_id in file_ids]
        }

        response = requests.post(
            f"{self.base_url}/mockup-generator/create-task/{product_id}",
            headers=self.headers,
            json=mockup_data
        )
        response.raise_for_status()

        return response.json()

    def create_draft_order(self, calendar_images: List[str], recipient_info: Dict = None):
        """
        Create a draft order for a calendar

        Args:
            calendar_images: List of 12 calendar image paths
            recipient_info: Optional recipient information for order
        """
        # This is a simplified version - you'd need to implement full order creation
        # based on Printful's order API documentation

        file_ids = [self.upload_image(img) for img in calendar_images]

        order_data = {
            "recipient": recipient_info or {
                "name": "Customer Name",
                "address1": "123 Main St",
                "city": "City",
                "state_code": "CA",
                "country_code": "US",
                "zip": "12345"
            },
            "items": [
                {
                    "variant_id": 8379,  # Example calendar variant
                    "quantity": 1,
                    "files": [{"id": file_id} for file_id in file_ids]
                }
            ]
        }

        response = requests.post(
            f"{self.base_url}/orders",
            headers=self.headers,
            json=order_data
        )

        response.raise_for_status()
        return response.json()

    def get_shipping_rates(self, recipient_info: Dict, items: List[Dict]):
        """
        Get shipping rates for an order

        Args:
            recipient_info: Recipient address information
            items: List of items with variant_id and quantity
        """
        data = {
            "recipient": recipient_info,
            "items": items
        }

        response = requests.post(
            f"{self.base_url}/shipping/rates",
            headers=self.headers,
            json=data
        )

        response.raise_for_status()
        return response.json()

    def verify_connection(self):
        """Verify API connection is working"""
        try:
            info = self.get_store_info()
            return True, "Connected successfully"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return False, "Invalid API key"
            return False, f"API error: {e}"
        except Exception as e:
            return False, f"Connection error: {e}"
