
import os
from supabase import create_client, Client
from supabase.client import ClientOptions
from dotenv import load_dotenv

load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

def get_supabase_client(org_id: str) -> Client:
    """
    Create a Supabase client with a dynamic schema name based on org_id.
    """
    schema_name = f"organization_{org_id}"
    return create_client(
        url,
        key,
        options=ClientOptions(
            postgrest_client_timeout=10,
            storage_client_timeout=10,
            schema=schema_name,
        )
    )

def get_supabase_client_for_operation_portal( ) -> Client:
  
    return create_client(
        url,
        key,
        options=ClientOptions(
            postgrest_client_timeout=10,
            storage_client_timeout=10,
            schema="operation_portal",
        )
    )

def get_supabase_public_client() -> Client:
    return create_client(url,key)