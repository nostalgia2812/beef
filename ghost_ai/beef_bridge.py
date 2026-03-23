#!/usr/bin/env python3
"""
Ghost AI — BeEF Integration Bridge
Bypass Supreme + Hail Mary browser exploitation module.
For authorized penetration testing ONLY.
NO wallet integration.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import httpx


@dataclass
class HookedBrowser:
    hook_id: str
    ip: str
    browser_name: str
    browser_version: str
    os: str
    platform: str
    hooked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "hook_id": self.hook_id,
            "ip": self.ip,
            "browser": f"{self.browser_name} {self.browser_version}",
            "os": self.os,
            "platform": self.platform,
            "hooked_at": self.hooked_at,
        }


class BeEFBridge:
    """
    Ghost AI bridge to BeEF REST API.
    Authorized pentest use only — requires BeEF server running locally.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 3000,
        api_token: str = "",
    ) -> None:
        self.base_url = f"http://{host}:{port}/api"
        self.token = api_token

    def _get(self, path: str) -> dict:
        url = f"{self.base_url}{path}"
        resp = httpx.get(url, params={"token": self.token}, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, data: dict) -> dict:
        url = f"{self.base_url}{path}"
        resp = httpx.post(
            url,
            params={"token": self.token},
            json=data,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def get_hooked_browsers(self) -> list[HookedBrowser]:
        """Return all currently hooked browsers."""
        try:
            data = self._get("/hooks")
            browsers = []
            for hb in data.get("hooked-browsers", {}).get("online", {}).values():
                browsers.append(HookedBrowser(
                    hook_id=str(hb.get("id", "")),
                    ip=hb.get("ip", ""),
                    browser_name=hb.get("BrowserName", ""),
                    browser_version=hb.get("BrowserVersion", ""),
                    os=hb.get("OsName", ""),
                    platform=hb.get("BrowserPlatform", ""),
                ))
            return browsers
        except Exception:
            return []

    def execute_module(
        self,
        hook_id: str,
        module_id: int,
        params: dict,
    ) -> dict:
        """Execute a BeEF module on a hooked browser."""
        return self._post(
            f"/modules/{hook_id}/{module_id}",
            params,
        )

    def get_module_results(self, hook_id: str, module_id: int) -> list[dict]:
        try:
            data = self._get(f"/modules/{hook_id}/{module_id}")
            return data.get("results", [])
        except Exception:
            return []

    def ghost_ai_status(self) -> dict:
        browsers = self.get_hooked_browsers()
        return {
            "beef_connected": True,
            "hooked_browsers": len(browsers),
            "browsers": [b.to_dict() for b in browsers],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


if __name__ == "__main__":
    import os
    bridge = BeEFBridge(
        host=os.environ.get("BEEF_HOST", "127.0.0.1"),
        port=int(os.environ.get("BEEF_PORT", "3000")),
        api_token=os.environ.get("BEEF_TOKEN", ""),
    )
    print(json.dumps(bridge.ghost_ai_status(), indent=2))
