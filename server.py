import os
import requests
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

mcp = FastMCP("KubeArchive")

KUBEARCHIVE_URL = os.getenv("KUBEARCHIVE_URL", "https://localhost:8081")
KUBEARCHIVE_TOKEN = os.getenv("KUBEARCHIVE_TOKEN", "")


def get_resources(resourceType: str, apiVersion: str, namespace: str, token: str, kubearchive_url: str) -> str:
    prefix = "api"
    if apiVersion != "v1":
        prefix = "apis"

    if namespace:
        url = f"{kubearchive_url}/{prefix}/{apiVersion}/namespaces/{namespace}/{resourceType}"
    else:
        url = f"{kubearchive_url}/{prefix}/{apiVersion}/{resourceType}"
    
    try:
        # Use environment token if available, otherwise fall back to passed token
        auth_token = KUBEARCHIVE_TOKEN if KUBEARCHIVE_TOKEN else token
        
        if not auth_token:
            return "Error: No authorization token available. Please set KUBEARCHIVE_TOKEN environment variable or pass token parameter."
        
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            verify=False,
            timeout=30
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.text
        elif response.status_code == 401:
            return f"Error: Authentication failed. Please check your authorization token."
        elif response.status_code == 404:
            return f"Error: Resource not found. URL: {url}"
        elif response.status_code == 403:
            return f"Error: Forbidden. Check permissions for accessing {resourceType} in namespace '{namespace}'"
        else:
            return f"Error: HTTP {response.status_code} - {response.text}"
    
    except requests.exceptions.ConnectionError:
        return f"Error: Cannot connect to KubeArchive server at {kubearchive_url}"
    except requests.exceptions.Timeout:
        return f"Error: Request timeout when connecting to KubeArchive server"
    except Exception as e:
        return f"Error: Unexpected error - {str(e)}"


@mcp.tool
def list_resources(resourceType: str, apiVersion: str, namespace: str, token: str = "") -> str:
    """List archived Kubernetes resources from KubeArchive
    
    Args:
        resourceType: Kubernetes resource resourceType
        apiVersion: Kubernetes resource apiVersion
        namespace: namespace where to query for resources if namespace is empty, resources for all namespaces will be returned
        token: Authorization token for KubeArchive API access (optional if KUBEARCHIVE_TOKEN env var is set)
    
    Returns:
        JSON string containing the list of archived resources
    """    
    
    return get_resources(resourceType, apiVersion, namespace, token, KUBEARCHIVE_URL)
