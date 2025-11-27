import asyncio
import logging
from typing import Any

import httpx

from src.config.settings import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_calls_per_minute: int):
        self.max_calls_per_minute = max_calls_per_minute
        self.calls: list[float] = []
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire permission to make an API call, respecting rate limits."""
        async with self.lock:
            now = asyncio.get_event_loop().time()
            # Remove calls older than 1 minute
            self.calls = [call_time for call_time in self.calls if now - call_time < 60]

            if len(self.calls) >= self.max_calls_per_minute:
                # Wait until the oldest call expires
                sleep_time = 60 - (now - self.calls[0])
                if sleep_time > 0:
                    logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                    await asyncio.sleep(sleep_time)
                    self.calls = self.calls[1:]

            self.calls.append(now)


class GitLabClient:
    """
    Wrapper client for GitLab API with rate limiting and error handling.
    """

    def __init__(self, api_url: str | None = None, access_token: str | None = None):
        self.api_url = api_url or settings.gitlab_api_url
        self.access_token = access_token or settings.gitlab_access_token
        self.rate_limiter = RateLimiter(settings.gitlab_api_rate_limit_per_minute)

        if not self.access_token:
            logger.warning("GitLab access token not configured")

    def _get_headers(self) -> dict[str, str]:
        """Get headers for GitLab API requests."""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["PRIVATE-TOKEN"] = self.access_token
        return headers

    async def _request(
        self, method: str, endpoint: str, params: dict[str, Any] | None = None, **kwargs: Any
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        Make a rate-limited request to GitLab API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            **kwargs: Additional arguments for httpx request
            
        Returns:
            JSON response from GitLab API
            
        Raises:
            httpx.HTTPError: If request fails
        """
        await self.rate_limiter.acquire()

        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()

        async with httpx.AsyncClient() as client:
            logger.debug(f"{method} {url}")
            response = await client.request(
                method, url, headers=headers, params=params, timeout=30.0, **kwargs
            )
            response.raise_for_status()
            return response.json()

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a GET request to GitLab API."""
        return await self._request("GET", endpoint, params=params)

    async def get_project(self, project_id: int) -> dict[str, Any]:
        """Get project details."""
        return await self.get(f"/projects/{project_id}")

    async def get_project_deployments(
        self, project_id: int, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Get project deployments."""
        result = await self.get(f"/projects/{project_id}/deployments", params=params)
        return result if isinstance(result, list) else []

    async def get_project_merge_requests(
        self, project_id: int, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Get project merge requests."""
        result = await self.get(f"/projects/{project_id}/merge_requests", params=params)
        return result if isinstance(result, list) else []

    async def get_merge_request_commits(
        self, project_id: int, merge_request_iid: int
    ) -> list[dict[str, Any]]:
        """Get commits for a merge request."""
        result = await self.get(
            f"/projects/{project_id}/merge_requests/{merge_request_iid}/commits"
        )
        return result if isinstance(result, list) else []

    async def get_project_issues(
        self, project_id: int, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Get project issues."""
        result = await self.get(f"/projects/{project_id}/issues", params=params)
        return result if isinstance(result, list) else []


# Global client instance
gitlab_client = GitLabClient()
