"""
Run this script to populate the database with 
sample tickets for testing similarity search.

Usage: python seed_data.py
"""
import requests
import time

BASE_URL = "http://localhost:8000"

sample_tickets = [
    # Login issues
    {
        "title": "Cannot login to the application",
        "description": "I am unable to log into the system. When I enter my credentials and click login, nothing happens. The page just refreshes. I've tried clearing cache and using different browsers.",
        "priority": "high",
        "category": "authentication"
    },
    {
        "title": "Login page not working",
        "description": "The login button is not responding. I enter username and password but cannot get into the system. This started happening after the update yesterday.",
        "priority": "high",
        "category": "authentication"
    },
    {
        "title": "Forgot password link broken",
        "description": "When I click on forgot password, I receive an error 404 page. I cannot reset my password and am locked out of my account.",
        "priority": "medium",
        "category": "authentication"
    },
    # Performance issues
    {
        "title": "Application is very slow",
        "description": "The dashboard takes more than 30 seconds to load. All pages are extremely slow. This is affecting my productivity. The issue started this morning.",
        "priority": "high",
        "category": "performance"
    },
    {
        "title": "Dashboard loading extremely slow",
        "description": "It takes forever for the main dashboard to appear. Sometimes it times out completely. Other users in my team are also experiencing the same issue.",
        "priority": "high",
        "category": "performance"
    },
    # Data issues
    {
        "title": "Data not saving in the form",
        "description": "When I fill out the customer form and click save, the data disappears. I have to re-enter everything each time. Very frustrating issue.",
        "priority": "medium",
        "category": "data"
    },
    {
        "title": "Form submission not working",
        "description": "After filling all required fields and submitting the form, I get a success message but the data is not saved in the database.",
        "priority": "medium",
        "category": "data"
    },
    # API issues  
    {
        "title": "API returning 500 errors",
        "description": "Our integration is failing. The API endpoint /api/v1/orders is returning 500 Internal Server Error for all requests since 2 PM today.",
        "priority": "critical",
        "category": "api"
    },
    {
        "title": "REST API endpoint throwing errors",
        "description": "Getting 500 server errors from the orders API. All API calls are failing. This is blocking our entire production integration.",
        "priority": "critical",
        "category": "api"
    },
]

# Add resolved tickets with solutions
resolved_tickets = [
    {
        "title": "Users unable to authenticate",
        "description": "Multiple users reporting they cannot log in. Authentication system appears to be down.",
        "priority": "critical",
        "category": "authentication",
        "solution": "Root cause was expired SSL certificate on auth server. Renewed certificate and restarted auth service. All users can now log in successfully."
    },
    {
        "title": "System performance degraded",
        "description": "Application response times increased significantly. Users reporting timeouts.",
        "priority": "high",
        "category": "performance",
        "solution": "Identified missing database index on orders table. Added composite index on (user_id, created_at). Response times reduced from 30s to under 1s."
    },
    {
        "title": "API 500 errors on orders endpoint",
        "description": "Orders API returning internal server errors. Production integration blocked.",
        "priority": "critical",
        "category": "api",
        "solution": "Database connection pool was exhausted due to connection leak in order processing service. Fixed connection leak and increased pool size from 10 to 50. Deployed hotfix."
    },
]

def seed_database():
    print("🌱 Seeding database with sample tickets...")
    
    # Add open tickets
    for ticket_data in sample_tickets:
        response = requests.post(
            f"{BASE_URL}/tickets/",
            json=ticket_data
        )
        if response.status_code == 200:
            print(f"  ✓ Created: {ticket_data['title'][:50]}")
        else:
            print(f"  ✗ Failed: {response.text}")
        time.sleep(0.5)  # Rate limit embedding calls
    
    # Add resolved tickets with solutions
    for ticket_data in resolved_tickets:
        solution = ticket_data.pop("solution")
        
        # Create ticket
        response = requests.post(
            f"{BASE_URL}/tickets/",
            json=ticket_data
        )
        if response.status_code == 200:
            ticket_id = response.json()["id"]
            
            # Resolve it with solution
            requests.patch(
                f"{BASE_URL}/tickets/{ticket_id}",
                json={
                    "status": "resolved",
                    "solution": solution
                }
            )
            print(f"  ✓ Resolved: {ticket_data['title'][:50]}")
        
        time.sleep(0.5)
    
    print(f"\n✅ Seeding complete!")
    print(f"   Created {len(sample_tickets)} open tickets")
    print(f"   Created {len(resolved_tickets)} resolved tickets")
    print(f"\n🔍 Test search at: {BASE_URL}/docs")

if __name__ == "__main__":
    seed_database()