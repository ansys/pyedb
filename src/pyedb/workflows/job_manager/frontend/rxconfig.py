import reflex as rx

config = rx.Config(
    app_name="frontend",
    app_module_import="frontend",
    frontend_port=3000,
    backend_port=8000,
    api_url="http://localhost:8000",
)
