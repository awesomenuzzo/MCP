import pytest
import logging
import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import get_menu, create_order, search_menu


# Set up logging to both console and file with more detailed formatting
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console handler
    ]
)
logger = logging.getLogger(__name__)

# Test data
TEST_ADDRESS = {
    "street": "1 Ferry Building",
    "city": "San Francisco",
    "state": "CA",
    "zip_code": "94111"
}

TEST_CUSTOMER = {
    "first_name": "John",
    "last_name": "Doe",
    "address": "123 Main St",
    "phone": "5551234567",
    "email": "john@example.com"
}

TEST_PAYMENT = {
    "card_number": "4111111111111111",
    "expiration": "12/25",
    "cvv": "123"
}

TEST_ITEMS = ["12SCPFEAST"]  # Medium Ultimate Pepperoni pizza

@pytest.mark.asyncio
async def test_get_menu():
    """Test menu retrieval functionality."""
    logger.info(f"Testing menu retrieval for address: {TEST_ADDRESS}")
    result = await get_menu(
        TEST_ADDRESS["street"],
        TEST_ADDRESS["city"],
        TEST_ADDRESS["state"],
        TEST_ADDRESS["zip_code"]
    )
    
    # Log the full menu data
    logger.info("\n=== Menu Data ===")
    if "error" in result:
        logger.error(f"Error: {result['error']}")
    else:
        for key, value in result.items():
            logger.info(f"\n{key}:")
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    logger.info(f"  {subkey}: {subvalue}")
            else:
                logger.info(f"  {value}")
    
    # Run assertions
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    
    # Check that we have the expected keys
    expected_keys = ['Flavors', 'Products', 'Sizes', 'Toppings']
    for key in expected_keys:
        assert key in result, f"Missing expected key: {key}. Available keys: {list(result.keys())}"
    
    # Check that we have some menu items
    assert len(result['Products']) > 0, "Menu should contain products"
    
    # Check that we have some sizes
    assert len(result['Sizes']) > 0, "Menu should contain sizes"
    
    # Check that we have some toppings
    assert len(result['Toppings']) > 0, "Menu should contain toppings"

@pytest.mark.asyncio
async def test_get_menu_invalid_address():
    """Test menu retrieval with invalid address."""
    logger.info("Testing menu retrieval with invalid address")
    result = await get_menu(
        "Invalid Street",
        "Invalid City",
        "XX",
        "00000"
    )
    
    # Log the result
    logger.info(f"Result: {result}")
    
    # Should return an error message
    assert "error" in result
    assert "Failed to get menu" in result["error"]

@pytest.mark.asyncio
async def test_create_order():
    """Test order creation functionality."""
    logger.info("Testing order creation")
    
    # First get a valid store ID
    menu_result = await get_menu(
        TEST_ADDRESS["street"],
        TEST_ADDRESS["city"],
        TEST_ADDRESS["state"],
        TEST_ADDRESS["zip_code"]
    )
    
    # Get the first store ID from the menu result
    store_id = menu_result.get('store_id')
    assert store_id is not None, "Could not get store ID from menu"
    
    # Create the order
    result = await create_order(
        store_id,
        TEST_CUSTOMER,
        TEST_PAYMENT,
        TEST_ITEMS
    )
    
    # Log the result
    logger.info(f"Order creation result: {result}")
    
    # Check that we got a response
    assert isinstance(result, str)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_create_order_invalid_store():
    """Test order creation with invalid store ID."""
    logger.info("Testing order creation with invalid store ID")
    result = await create_order(
        "invalid_store_id",
        TEST_CUSTOMER,
        TEST_PAYMENT,
        TEST_ITEMS
    )
    
    # Log the result
    logger.info(f"Result: {result}")
    
    # Should return an error message
    assert "Failed to place order" in result

@pytest.mark.asyncio
async def test_create_order_invalid_customer():
    """Test order creation with invalid customer info."""
    logger.info("Testing order creation with invalid customer info")
    invalid_customer = {
        "first_name": "John",
        # Missing required fields
    }
    
    result = await create_order(
        "any_store_id",
        invalid_customer,
        TEST_PAYMENT,
        TEST_ITEMS
    )
    
    # Log the result
    logger.info(f"Result: {result}")
    
    # Should return an error message
    assert "Failed to place order" in result

@pytest.mark.asyncio
async def test_create_order_invalid_items():
    """Test order creation with invalid items."""
    logger.info("Testing order creation with invalid items")
    result = await create_order(
        "any_store_id",
        TEST_CUSTOMER,
        TEST_PAYMENT,
        ["invalid_item_code"]
    )
    
    # Log the result
    logger.info(f"Result: {result}")
    
    # Should return an error message
    assert "Failed to place order" in result

@pytest.mark.asyncio
async def test_search_menu():
    """Test menu search functionality."""
    logger.info(f"Testing menu search for address: {TEST_ADDRESS}")
    
    # Test basic search with max results and search term
    result = await search_menu(
        TEST_ADDRESS["street"],
        TEST_ADDRESS["city"],
        TEST_ADDRESS["state"],
        TEST_ADDRESS["zip_code"],
        Name="Pizza",  # Add search term for pizza
        max_results=1000  # Use the new default limit
    )
    
    # Print search results in a readable format
    print("\n=== Search Results ===")
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"\nStore: {result['store_address']}")
        print(f"Found {result['total_matches']} items")
        print(f"Search conditions: {result['search_conditions']}")
        
        print("\n=== Available Toppings ===")
        for code, topping in result['guides']['toppings'].items():
            print(f"\n{code}: {topping[0]}")  # topping[0] is the name
            print(f"  Category: {topping[1]}")  # topping[1] is the category
            if topping[2]:  # topping[2] is the tags list
                print(f"  Tags: {', '.join(topping[2])}")
        
        print("\n=== Available Sizes ===")
        for code, size in result['guides']['sizes'].items():
            print(f"\n{code}: {size}")
        
        print("\n=== Search Results ===")
        for item in result['results']:
            print(f"\nItem: {item['Name']}")
            print(f"  Code: {item['Code']}")
            print(f"  Price: ${item['Price']}")
            print(f"  Size: {item['SizeCode']}")
            print(f"  Product Code: {item['ProductCode']}")
            if item['Toppings']:
                print("  Toppings:")
                for topping, amount in item['Toppings'].items():
                    print(f"    - {topping}: {amount}")
    
    # Run assertions
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert "store_id" in result, "Result should contain store_id"
    assert "store_address" in result, "Result should contain store_address"
    assert "results" in result, "Result should contain results"
    assert "total_matches" in result, "Result should contain total_matches"
    assert "search_conditions" in result, "Result should contain search_conditions"
    assert "guides" in result, "Result should contain guides"
    assert "toppings" in result["guides"], "Result should contain topping guide"
    assert "sizes" in result["guides"], "Result should contain size guide"
    assert isinstance(result["results"], list), "Results should be a list"
    assert len(result["results"]) <= 1000, "Results should be limited to max_results"
    
    # Verify that all results contain "Pizza" in the name
    for item in result["results"]:
        assert "Pizza" in item["Name"], "All items should contain 'Pizza' in name"
    
    # Test search with multiple conditions (matching original API style)
    print("\n=== Testing search with multiple conditions ===")
    filtered_result = await search_menu(
        TEST_ADDRESS["street"],
        TEST_ADDRESS["city"],
        TEST_ADDRESS["state"],
        TEST_ADDRESS["zip_code"],
        Name="Pizza",
        SizeCode="L",
        max_results=1000  # Use the new default limit
    )
    
    # Print filtered results
    print(f"\nFound {len(filtered_result['results'])} filtered items")
    for item in filtered_result['results']:
        print(f"\nFiltered Item: {item['Name']}")
        print(f"  Size: {item['SizeCode']}")
        print(f"  Price: ${item['Price']}")
        if item['Toppings']:
            print("  Toppings:")
            for topping, amount in item['Toppings'].items():
                print(f"    - {topping}: {amount}")
    
    assert isinstance(filtered_result, dict), f"Expected dict, got {type(filtered_result)}"
    assert "results" in filtered_result, "Result should contain results"
    assert len(filtered_result["results"]) <= 1000, "Filtered results should be limited to max_results"
    
    # Verify filters worked
    for item in filtered_result["results"]:
        assert "Pizza" in item["Name"], "Item should contain 'Pizza' in name"
        assert "L" in item["SizeCode"], "Size should contain 'L'" 