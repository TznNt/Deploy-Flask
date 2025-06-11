import pytest
from flask import template_rendered
from index import app
from contextlib import contextmanager


# Este context manager é utilizado para capturar os templates renderizados durante o teste.
# Ele se conecta ao sinal `template_rendered` do Flask, que é emitido sempre que um template é renderizado.
# Isso permite verificar qual template foi usado e qual contexto foi passado para ele — algo essencial para testes que avaliam a camada de apresentação.
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


# Este fixture do pytest prepara o ambiente de testes para a aplicação Flask.
# Ao ativar o modo TESTING, o Flask trabalha de maneira mais segura para testes:
# - Ele não executa erros de forma silenciosa (útil para detectar problemas);
# - Permite a utilização do test client, que simula requisições HTTP.
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# Primeiro teste: Verifica se a rota principal ('/') está funcionando corretamente e renderizando o template esperado.
# Aqui estamos usando o `captured_templates` para interceptar o template renderizado durante a requisição.
# O teste verifica três coisas:
# 1. Se a resposta da requisição foi bem-sucedida (código 200);
# 2. Se exatamente um template foi renderizado;
# 3. Se o nome do template renderizado é 'index.html', confirmando que a rota está vinculada ao template correto.
def test_index_route_renders_template(client):
    with captured_templates(app) as templates:
        response = client.get('/')
        assert response.status_code == 200  # Verifica se a resposta foi bem-sucedida.
        assert len(templates) == 1          # Garante que um único template foi renderizado.
        template, context = templates[0]
        assert template.name == "index.html"  # Confirma que o template usado é o correto.


# Segundo teste: Garante que o acesso a uma rota inexistente retorna um erro 404 (página não encontrada).
# Este teste é importante porque valida o comportamento padrão do Flask quando uma rota inválida é acessada,
# ajudando a garantir que o sistema lida corretamente com URLs desconhecidas ou mal digitadas.
def test_404_for_nonexistent_route(client):
    response = client.get('/rota-que-nao-existe')
    assert response.status_code == 404  # Espera-se um erro 404 para rotas inexistentes.


# Terceiro teste: Verifica se a configuração da aplicação está corretamente ajustada para modo de teste.
# Isso é fundamental para garantir que o ambiente de testes está devidamente isolado do ambiente de produção.
# Além disso, pode influenciar diretamente em como certas funcionalidades se comportam (por exemplo, desativando certos recursos como envio de e-mails, autenticação real, etc).
def test_app_testing_config_is_true(client):
    assert app.config["TESTING"] is True  # Confirma que o modo de testes está ativado.
