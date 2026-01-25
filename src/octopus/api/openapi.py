from importlib import metadata

from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import OpenAPIRenderPlugin, ScalarRenderPlugin


class OpenAPIConfigBuilder:
    """Builder for OpenAPI configuration."""

    @property
    def title(self) -> str:
        """Title of the API."""
        return "octopus"

    @property
    def version(self) -> str:
        """Version of the API."""
        return metadata.version("octopus")

    @property
    def description(self) -> str:
        """Description of the API."""
        return "Broadcast streaming gate service 🚧"

    @property
    def path(self) -> str:
        """Path to OpenAPI docs endpoint."""
        return "/openapi"

    @property
    def renderer(self) -> OpenAPIRenderPlugin:
        """Renderer plugin."""
        return ScalarRenderPlugin(
            path=self.path,
            options={
                "hideClientButton": True,
            },
        )

    def build(self) -> OpenAPIConfig:
        """Build OpenAPI configuration."""
        return OpenAPIConfig(
            title=self.title,
            version=self.version,
            description=self.description,
            use_handler_docstrings=True,
            path=self.path,
            render_plugins=[self.renderer],
        )
