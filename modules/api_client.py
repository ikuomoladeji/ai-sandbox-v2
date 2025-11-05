"""
Production-grade API client for Ollama with retry logic and error handling
Provides reliable connection management and graceful degradation
"""
import time
import requests
from typing import Optional, Dict, Any
from config import Config
from modules.logger import get_logger, TPRMLogger

logger = get_logger(__name__)

class APIError(Exception):
    """Raised when API call fails"""
    pass

class ConnectionError(APIError):
    """Raised when connection to Ollama fails"""
    pass

class OllamaClient:
    """Production-grade Ollama API client with retry logic"""

    def __init__(self, url: str = None, timeout: int = None):
        """
        Initialize Ollama client

        Args:
            url: Ollama API URL (defaults to config)
            timeout: Request timeout in seconds (defaults to config)
        """
        self.url = url or Config.OLLAMA_URL
        self.timeout = timeout or Config.OLLAMA_TIMEOUT
        self._connection_verified = False

    def verify_connection(self) -> bool:
        """
        Verify connection to Ollama server

        Returns:
            True if connection successful

        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Try to connect to Ollama's tags endpoint
            test_url = self.url.replace('/api/generate', '/api/tags')
            response = requests.get(test_url, timeout=5)
            response.raise_for_status()

            self._connection_verified = True
            logger.info(f"Successfully connected to Ollama at {self.url}")
            return True

        except requests.exceptions.ConnectionError:
            error_msg = (
                f"Cannot connect to Ollama at {self.url}. "
                "Please ensure Ollama is running (try 'ollama serve')."
            )
            logger.error(error_msg)
            raise ConnectionError(error_msg)

        except requests.exceptions.Timeout:
            error_msg = f"Connection to Ollama timed out at {self.url}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)

        except Exception as e:
            error_msg = f"Failed to connect to Ollama: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)

    def generate(
        self,
        model: str,
        prompt: str,
        max_retries: int = 3,
        retry_delay: int = 2
    ) -> str:
        """
        Generate response from Ollama model with retry logic

        Args:
            model: Model name to use
            prompt: Prompt to send to model
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            Generated response text

        Raises:
            APIError: If generation fails after retries
            ConnectionError: If connection cannot be established
        """
        # Verify connection if not already done
        if not self._connection_verified:
            self.verify_connection()

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        last_error = None
        start_time = time.time()

        for attempt in range(1, max_retries + 1):
            try:
                logger.debug(f"API call attempt {attempt}/{max_retries} to model {model}")

                response = requests.post(
                    self.url,
                    json=payload,
                    timeout=self.timeout
                )

                response.raise_for_status()
                data = response.json()

                result = data.get("response", "").strip()

                if not result:
                    logger.warning("Model returned empty response")
                    raise APIError("Model returned empty response")

                duration = time.time() - start_time
                TPRMLogger.log_api_call(logger, f"Ollama/{model}", "success", duration)

                return result

            except requests.exceptions.Timeout:
                last_error = f"Request timed out after {self.timeout} seconds"
                logger.warning(f"Attempt {attempt} failed: {last_error}")

            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection failed: {str(e)}"
                logger.warning(f"Attempt {attempt} failed: {last_error}")

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response else 'unknown'
                last_error = f"HTTP {status_code}: {str(e)}"
                logger.warning(f"Attempt {attempt} failed: {last_error}")

                # Don't retry on 4xx errors (client errors)
                if e.response and 400 <= e.response.status_code < 500:
                    break

            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.warning(f"Attempt {attempt} failed: {last_error}")

            # Wait before retry (except on last attempt)
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

        # All attempts failed
        duration = time.time() - start_time
        TPRMLogger.log_api_call(logger, f"Ollama/{model}", "failure", duration)

        error_msg = f"Failed to generate response after {max_retries} attempts. Last error: {last_error}"
        logger.error(error_msg)
        raise APIError(error_msg)

    def check_model_available(self, model: str) -> bool:
        """
        Check if a model is available in Ollama

        Args:
            model: Model name to check

        Returns:
            True if model is available
        """
        try:
            tags_url = self.url.replace('/api/generate', '/api/tags')
            response = requests.get(tags_url, timeout=5)
            response.raise_for_status()

            data = response.json()
            models = data.get('models', [])

            available = any(m.get('name') == model for m in models)

            if not available:
                logger.warning(f"Model '{model}' not found in Ollama. Available models: {[m.get('name') for m in models]}")

            return available

        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False

# Global client instance
_client = None

def get_client() -> OllamaClient:
    """Get or create global Ollama client instance"""
    global _client
    if _client is None:
        _client = OllamaClient()
    return _client

def ask_model(model_name: str, prompt: str) -> str:
    """
    Convenience function for generating responses

    Args:
        model_name: Model to use
        prompt: Prompt to send

    Returns:
        Generated response

    Raises:
        APIError: If generation fails
        ConnectionError: If connection fails
    """
    client = get_client()
    return client.generate(model_name, prompt)
