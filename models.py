"""
Modelos de banco de dados para sistema de apostas
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    saldo = Column(Float, default=0.0)
    status = Column(String(20), default='ativo')  # ativo, bloqueado, inativo
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    apostas = relationship("Aposta", back_populates="usuario")
    transacoes = relationship("Transacao", back_populates="usuario")

class Aposta(Base):
    __tablename__ = 'apostas'
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    numero = Column(String(4), nullable=False)  # Número apostado
    animal = Column(String(50), nullable=False)  # Animal apostado
    valor = Column(Float, nullable=False)  # Valor da aposta
    loteria = Column(String(100), nullable=False)  # Qual loteria
    horario = Column(String(10), nullable=False)  # Horário do sorteio (ex: "11:00")
    tipo_aposta = Column(String(20), default='grupo')  # grupo, dezena, centena, milhar
    status = Column(String(20), default='pendente')  # pendente, ganhou, perdeu, cancelada
    multiplicador = Column(Float, default=18.0)  # Multiplicador de ganho
    data_aposta = Column(DateTime, default=datetime.utcnow)
    data_liquidacao = Column(DateTime, nullable=True)
    
    usuario = relationship("Usuario", back_populates="apostas")
    liquidacao = relationship("Liquidacao", back_populates="aposta", uselist=False)

class Resultado(Base):
    __tablename__ = 'resultados'
    
    id = Column(Integer, primary_key=True)
    numero = Column(String(4), nullable=False)
    animal = Column(String(50), nullable=False)
    loteria = Column(String(100), nullable=False)
    horario = Column(String(10), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    processado = Column(Boolean, default=False)  # Se já foi usado para liquidar
    
    liquidacoes = relationship("Liquidacao", back_populates="resultado")

class Liquidacao(Base):
    __tablename__ = 'liquidacoes'
    
    id = Column(Integer, primary_key=True)
    aposta_id = Column(Integer, ForeignKey('apostas.id'), nullable=False)
    resultado_id = Column(Integer, ForeignKey('resultados.id'), nullable=False)
    valor_aposta = Column(Float, nullable=False)
    valor_ganho = Column(Float, default=0.0)
    status = Column(String(20), default='processando')  # processando, concluida, erro
    data_liquidacao = Column(DateTime, default=datetime.utcnow)
    
    aposta = relationship("Aposta", back_populates="liquidacao")
    resultado = relationship("Resultado", back_populates="liquidacoes")

class Transacao(Base):
    __tablename__ = 'transacoes'
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    tipo = Column(String(20), nullable=False)  # deposito, saque, ganho, aposta
    valor = Column(Float, nullable=False)
    descricao = Column(Text)
    status = Column(String(20), default='pendente')  # pendente, concluida, cancelada
    data_transacao = Column(DateTime, default=datetime.utcnow)
    
    usuario = relationship("Usuario", back_populates="transacoes")

