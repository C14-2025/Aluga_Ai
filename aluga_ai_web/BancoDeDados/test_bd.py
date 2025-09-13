import types
import pytest
from BancoDeDados import Integracao as mod


@pytest.fixture
def fake_supabase(monkeypatch):
    """
    Substitui 'mod.supabase' por um client falso, sem rede.
    Retorna o client falso para permitir ajuste de respostas em cada teste.
    """
    class _FakeResp:
        def __init__(self, data):
            self.data = data

    class _FakeQuery:
        def __init__(self, data_seq):
            self._seq = data_seq
            self._i = 0

        def _next(self):
            if isinstance(self._seq, list):
                if self._i < len(self._seq):
                    v = self._seq[self._i]
                    self._i += 1
                    return v
                return []
            return self._seq

        def execute(self):
            return _FakeResp(self._next())

        def insert(self, _): return self
        def select(self, _="*"): return self
        def limit(self, _): return self
        def range(self, *_): return self

    class _FakeTable:
        def __init__(self, client):
            self.c = client

        def insert(self, rows):
            return _FakeQuery(self.c.insert_data)

        def select(self, cols="*"):
            return _FakeQuery(self.c.select_data)

        def limit(self, n):
            return _FakeQuery(self.c.select_data)

        def range(self, start, end):
            return _FakeQuery(self.c.range_sequence)

        def execute(self):
            return _FakeResp(self.c.select_data)

    class _FakeClient:
        def __init__(self):
            # defaults (cada teste pode sobrescrever)
            self.insert_data = [{"ok": True}]
            self.select_data = [{"id": 1}]
            self.range_sequence = [[{"id": 1}], []]

        def table(self, _name):
            return _FakeTable(self)

    client = _FakeClient()
    monkeypatch.setattr(mod, "supabase", client)
    return client


@pytest.fixture
def fake_psycopg2(monkeypatch):
    """
    Mock simples do psycopg2, sem tocar em banco real.
    """
    fake = types.ModuleType("psycopg2")

    class _Cur:
        def __init__(self):
            self.calls = 0
        def execute(self, *_a, **_kw):
            self.calls += 1
        def close(self): pass

    class _Conn:
        def __init__(self):
            self._cur = _Cur()
        def cursor(self):
            return self._cur
        def commit(self): pass
        def close(self): pass

    def connect(_conn_str):
        return _Conn()

    fake.connect = connect
    fake.extras = types.SimpleNamespace()

    monkeypatch.setitem(__import__("sys").modules, "psycopg2", fake)
    return fake


def test_inserir_em_lotes_ok(fake_supabase, capsys):
    fake_supabase.insert_data = [{"ok": True}]
    dados = [{"a": 1}, {"a": 2}, {"a": 3}]
    mod.inserir_em_lotes("tabela", dados, lote=2)
    out = capsys.readouterr().out
    assert "Lote 1 inserido (2 registros)." in out
    assert "Lote 2 inserido (1 registros)." in out


def test_inserir_em_lotes_falha(fake_supabase):
    fake_supabase.insert_data = []
    with pytest.raises(RuntimeError):
        mod.inserir_em_lotes("tabela", [{"a": 1}], lote=1)


def test_imprimir_exemplos_lista(capsys):
    mod.imprimir_exemplos_lista([{"x": 1}, {"y": 2}, {"z": 3}], n=2)
    out = capsys.readouterr().out
    assert "--- 2 exemplos do arquivo ---" in out
    assert "Exemplo 1:" in out and "Exemplo 2:" in out
    assert '"x": 1' in out and '"y": 2' in out


def test_imprimir_exemplos_bd_vazio(fake_supabase, capsys):
    fake_supabase.select_data = []
    mod.imprimir_exemplos_bd("tabela", n=3)
    out = capsys.readouterr().out
    assert "Tabela vazia para exemplos." in out

def test_inserir_via_postgres_sem_DATABASE_URL(capsys, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    mod.inserir_via_postgres("qualquer.json", "tabela")
    out = capsys.readouterr().out
    assert "DATABASE_URL não definida; pulando inserção direta." in out



