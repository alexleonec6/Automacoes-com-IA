from src.ai_service import _fallback_analise

def test_classificacao_incidente():
    res = _fallback_analise("O servidor de banco de dados caiu e está fora do ar!")
    assert res["categoria"] == "INCIDENTE_URGENTE"
    assert res["urgencia"] == "CRITICA"
    assert res["acao_recomendada"] == "notificar_telegram"

def test_classificacao_lead():
    res = _fallback_analise("Gostaria de um orçamento para contratar o plano empresarial.")
    assert res["categoria"] == "QUALIFICACAO_LEAD"
    assert res["urgencia"] == "MEDIA"

def test_classificacao_suporte():
    res = _fallback_analise("Preciso de ajuda, não consigo fazer login com minha senha.")
    assert res["categoria"] == "SUPORTE_CLIENTE"
