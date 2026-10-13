from datetime import datetime


def gerar_numero_protocolo(atendimento_id: int) -> str:
    """Gera um protocolo determinÃ­stico associado ao ID Ãºnico do atendimento."""
    data = datetime.now().strftime("%Y%m%d")
    return f"SAAE-{data}-{atendimento_id:06d}"