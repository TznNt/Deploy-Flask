import pytest
from flask import template_rendered
from index import app
from contextlib import contextmanager


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route_renders_template(client):
    with captured_templates(app) as templates:
        response = client.get('/')
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == "index.html"


def test_404_for_nonexistent_route(client):
    response = client.get('/rota-que-nao-existe')
    assert response.status_code == 404


def test_app_testing_config_is_true(client):
    assert app.config["TESTING"] is True
