import reflex as rx

config = rx.Config(
    app_name="frontend",
    stylesheets=["custom.css"],
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)