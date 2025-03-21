import pizzapi
from typing import Any, Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP
import logging
import os
import sys
from pizzapi.urls import Urls, COUNTRY_USA
from pizzapi.utils import request_json

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from topping_guide import TOPPINGS, SIZES

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

mcp = FastMCP("PizzAPI")

@mcp.tool()
async def get_menu(street: str, city: str, state: str, zip_code: str) -> Dict[str, Any]:
    """Get the menu from the store closest to the provided address. 
    Coupons are not yet available with this version of the MCP. 
    search_menu is preferred over get_menu in most cases as it is more succint.

    Args:
        street: str - The street address (e.g. "700 Pennsylvania Avenue NW")
        city: str - The city name (e.g. "Washington")
        state: str - The state abbreviation (e.g. "DC")
        zip_code: str - The ZIP code (e.g. "20408")

    Returns:
        Dict[str, Any]: A cleaned menu dictionary containing only the necessary menu details.
    """
    try:
        logger.debug(f"Creating address object for {street}, {city}, {state} {zip_code}")
        address = pizzapi.Address(street, city, state, zip_code)
        
        logger.debug("Finding closest store...")
        store = address.closest_store()
        logger.debug(f"Found store: {store}")
        
        logger.debug("Getting menu...")
        # Get the raw menu data directly from the API
        urls = Urls(COUNTRY_USA)
        menu_data = request_json(urls.menu_url(), store_id=store.id, lang='en')
        logger.debug(f"Raw menu keys: {menu_data.keys() if isinstance(menu_data, dict) else 'Not a dict'}")
        
        # Clean the menu: remove keys that contain coupons or superfluous information
        keys_to_keep = ['Flavors', 'Products', 'Sizes', 'Toppings']
        cleaned_menu = {}
        
        # First, get the raw data from the menu
        if isinstance(menu_data, dict):
            # Get the main menu data
            for key in keys_to_keep:
                if key in menu_data:
                    cleaned_menu[key] = menu_data[key]
                else:
                    logger.warning(f"Key {key} not found in menu data")
            
            # If we have variants, add their data
            if 'Variants' in menu_data:
                variants = menu_data['Variants']
                if 'Products' in variants:
                    cleaned_menu['Products'].update(variants['Products'])
                if 'Sizes' in variants:
                    cleaned_menu['Sizes'].update(variants['Sizes'])
                if 'Toppings' in variants:
                    cleaned_menu['Toppings'].update(variants['Toppings'])
        
        if not cleaned_menu:
            logger.error("No valid menu data found after cleaning")
            return {"error": "No valid menu data found"}
            
        logger.debug(f"Cleaned menu keys: {cleaned_menu.keys()}")
        return cleaned_menu
        
    except Exception as e:
        logger.error(f"Error in get_menu: {str(e)}", exc_info=True)
        return {"error": f"Failed to get menu: {str(e)}"}

@mcp.tool()
async def create_order(
    store_id: str,
    customer_info: Dict[str, str],
    payment_info: Dict[str, str],
    items: List[str]
) -> str:
    """Place an order at the given store.
    
    Args:
        store_id: str - The identifier for the pizza store
        customer_info: Dict[str, str] - Customer details including:
            - first_name: str
            - last_name: str
            - address: str
            - phone: str
            - email: str
        payment_info: Dict[str, str] - Payment details including:
            - card_number: str
            - expiration: str
            - cvv: str
        items: List[str] - List of item codes to order

    Returns:
        str: Order confirmation or error message
    """
    try:
        store = pizzapi.Store(store_id)
        
        # Create a customer object with the required fields
        customer = pizzapi.Customer(
            first_name=customer_info['first_name'],
            last_name=customer_info['last_name'],
            address=customer_info['address'],
            phone=customer_info['phone'],
            email=customer_info['email']
        )
        
        order = pizzapi.Order(store, customer)
        
        # Add each item to the order
        for item in items:
            order.add_item(item)
        
        # Attach payment details to the order
        order.payment_info = payment_info

        placement_result = order.place()
        return str(placement_result)
    except Exception as e:
        return f"Failed to place order: {str(e)}"

@mcp.tool()
async def search_menu(
    street: str,
    city: str,
    state: str,
    zip_code: str,
    max_results: int = 1000,  # Reasonable limit for Claude's 200k token context
    **conditions
) -> Dict[str, Any]:
    """Search the menu from the store closest to the provided address.
    Matches the style of the original pizzapi search function.
    
    Args:
        street: str - The street address (e.g. "700 Pennsylvania Avenue NW")
        city: str - The city name (e.g. "Washington")
        state: str - The state abbreviation (e.g. "DC")
        zip_code: str - The ZIP code (e.g. "20408")
        max_results: int - Maximum number of results to return (default: 1000)
        **conditions: Arbitrary keyword arguments for search conditions
                    (e.g., Name="Pizza", Price="10.99", SizeCode="L")

    Returns:
        Dict[str, Any]: A dictionary containing matching menu items with their details.
    """
    try:
        logger.debug(f"Creating address object for {street}, {city}, {state} {zip_code}")
        address = pizzapi.Address(street, city, state, zip_code)
        
        logger.debug("Finding closest store...")
        store = address.closest_store()
        logger.debug(f"Found store: {store}")
        
        logger.debug("Getting menu...")
        # Get the raw menu data directly from the API
        urls = Urls(COUNTRY_USA)
        menu_data = request_json(urls.menu_url(), store_id=store.id, lang='en')
        
        if not isinstance(menu_data, dict):
            return {"error": "Invalid menu data received"}
            
        # Initialize results
        results = []
        
        # Get variants which contain the actual product data
        variants = menu_data.get('Variants', {})
        
        # Search through variants
        for variant in variants.values():
            # Process toppings like the original API
            if 'Tags' in variant and 'DefaultToppings' in variant['Tags']:
                variant['Toppings'] = dict(x.split('=', 1) for x in variant['Tags']['DefaultToppings'].split(',') if x)
            
            # Check if all conditions match
            matches = True
            for key, value in conditions.items():
                if key not in variant or str(value).lower() not in str(variant[key]).lower():
                    matches = False
                    break
            
            if matches:
                results.append({
                    'Code': variant.get('Code', ''),
                    'Name': variant.get('Name', ''),
                    'Price': variant.get('Price', ''),
                    'SizeCode': variant.get('SizeCode', ''),
                    'ProductCode': variant.get('ProductCode', ''),
                    'Toppings': variant.get('Toppings', {})
                })
        
        # Check if search is too broad
        if len(results) > max_results:
            logger.warning(f"Search returned {len(results)} results. Consider adding more specific conditions.")
            results = results[:max_results]
        
        logger.debug(f"Found {len(results)} matching items")
        return {
            'store_id': store.id,
            'store_address': store.data.get('AddressDescription', ''),
            'results': results,
            'total_matches': len(results),
            'search_conditions': conditions,
            'guides': {
                'toppings': TOPPINGS,
                'sizes': SIZES
            }
        }
        
    except Exception as e:
        logger.error(f"Error in search_menu: {str(e)}", exc_info=True)
        return {"error": f"Failed to search menu: {str(e)}"}

if __name__ == "__main__":
    mcp.run(transport='stdio')