import unittest

from app.config import Settings
from app.services.llm.core_llm import (
    CoreLlmConfigurationError,
    resolve_core_llm_target,
)


class CoreLlmProviderTests(unittest.TestCase):
    @staticmethod
    def _settings(*, openrouter_key: str = "") -> Settings:
        return Settings(_env_file=None, openrouter_cybercase=openrouter_key)

    def test_target_uses_the_dedicated_secret_and_bearer_auth(self) -> None:
        target = resolve_core_llm_target(
            "luna",
            configured_settings=self._settings(openrouter_key="core-secret"),
        )

        self.assertEqual(target.model, "openai/gpt-5.6-luna")
        self.assertEqual(target.messages_url, "https://openrouter.ai/api/v1/messages")
        self.assertEqual(target.headers["Authorization"], "Bearer core-secret")
        self.assertNotIn("x-api-key", target.headers)

    def test_target_resolves_model_aliases(self) -> None:
        target = resolve_core_llm_target(
            "sonnet",
            configured_settings=self._settings(openrouter_key="core-secret"),
        )
        self.assertEqual(target.model, "anthropic/claude-3.5-sonnet")

    def test_a_missing_key_has_no_fallback(self) -> None:
        with self.assertRaisesRegex(CoreLlmConfigurationError, "OPENROUTER_CYBERCASE"):
            resolve_core_llm_target("luna", configured_settings=self._settings())

    def test_the_generic_openrouter_key_cannot_satisfy_the_target(self) -> None:
        configured = self._settings()
        self.assertFalse(hasattr(configured, "openrouter_api_key"))

        with self.assertRaises(CoreLlmConfigurationError):
            resolve_core_llm_target("luna", configured_settings=configured)


if __name__ == "__main__":
    unittest.main()
