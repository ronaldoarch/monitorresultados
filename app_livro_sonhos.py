#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicação Flask para Painel do Livro dos Sonhos
Sistema onde usuários podem informar sonhos e receber palpites para apostas
Design inspirado no Barão do Bicho
"""

import os
import json
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
from livro_sonhos import LivroSonhos

app = Flask(__name__)
# Configurar CORS para permitir baraodobicho.com.br e localhost para desenvolvimento
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://baraodobicho.com.br",
            "https://www.baraodobicho.com.br",
            "http://baraodobicho.com.br",
            "http://www.baraodobicho.com.br",
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:5000",
            "http://localhost:8000",
            "http://127.0.0.1",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5000",
            "http://127.0.0.1:8000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Inicializar sistema de interpretação de sonhos
livro_sonhos = LivroSonhos()

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Painel principal do Livro dos Sonhos com design Barão do Bicho"""
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📖 Livro dos Sonhos - Barão do Bicho</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #0d4f1c;
                min-height: 100vh;
                padding: 20px;
                color: white;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .header {
                background: rgba(13, 79, 28, 0.9);
                padding: 30px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                text-align: center;
                border: 2px solid #4ade80;
            }
            
            .logo-container {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 20px;
                margin-bottom: 20px;
            }
            
            .logo-crown {
                font-size: 3em;
                color: #fbbf24;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
            
            .header h1 {
                color: #4ade80;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                font-weight: bold;
            }
            
            .header .subtitle {
                color: #ffffff;
                font-size: 1.2em;
                margin-top: 10px;
            }
            
            .header p {
                color: #d1d5db;
                font-size: 1.1em;
            }
            
            .main-card {
                background: rgba(13, 79, 28, 0.95);
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                margin-bottom: 30px;
                border: 2px solid #4ade80;
            }
            
            .input-group {
                margin-bottom: 25px;
            }
            
            .input-group label {
                display: block;
                margin-bottom: 8px;
                color: #4ade80;
                font-weight: 600;
                font-size: 1.1em;
            }
            
            .input-group input,
            .input-group textarea {
                width: 100%;
                padding: 15px;
                border: 2px solid #4ade80;
                border-radius: 10px;
                font-size: 1em;
                transition: all 0.3s;
                background: rgba(255, 255, 255, 0.1);
                color: white;
            }
            
            .input-group input::placeholder,
            .input-group textarea::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
            
            .input-group input:focus,
            .input-group textarea:focus {
                outline: none;
                border-color: #fbbf24;
                box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.2);
                background: rgba(255, 255, 255, 0.15);
            }
            
            .input-group textarea {
                min-height: 120px;
                resize: vertical;
            }
            
            .btn {
                background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
                color: #0d4f1c;
                padding: 15px 40px;
                border: none;
                border-radius: 10px;
                font-size: 1.1em;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(74, 222, 128, 0.3);
                text-transform: uppercase;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(74, 222, 128, 0.5);
                background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            }
            
            .btn:active {
                transform: translateY(0);
            }
            
            .resultado-container {
                margin-top: 30px;
                display: none;
            }
            
            .resultado-container.show {
                display: block;
                animation: fadeIn 0.5s;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .resultado-card {
                background: rgba(13, 79, 28, 0.9);
                padding: 30px;
                border-radius: 15px;
                margin-bottom: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                border: 2px solid #4ade80;
            }
            
            .resultado-header {
                text-align: center;
                margin-bottom: 25px;
                padding-bottom: 20px;
                border-bottom: 2px solid rgba(74, 222, 128, 0.3);
            }
            
            .resultado-header h2 {
                color: #4ade80;
                font-size: 2em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
            
            .animal-info {
                background: rgba(0, 0, 0, 0.3);
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
                border: 2px solid #fbbf24;
            }
            
            .animal-nome {
                font-size: 2.5em;
                color: #fbbf24;
                font-weight: bold;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
            
            .animal-grupo {
                font-size: 1.5em;
                color: #4ade80;
                margin-bottom: 10px;
                font-weight: bold;
            }
            
            .animal-significado {
                color: #d1d5db;
                font-style: italic;
                margin-top: 10px;
            }
            
            .numeros-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            
            .numero-card {
                background: rgba(0, 0, 0, 0.3);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                border: 2px solid #4ade80;
                transition: all 0.3s;
            }
            
            .numero-card:hover {
                border-color: #fbbf24;
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(251, 191, 36, 0.3);
            }
            
            .numero-tipo {
                font-size: 0.9em;
                color: #9ca3af;
                margin-bottom: 5px;
                text-transform: uppercase;
            }
            
            .numero-valor {
                font-size: 2em;
                font-weight: bold;
                color: #fbbf24;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
            
            .dias-sugeridos {
                margin-top: 30px;
            }
            
            .dias-sugeridos h3 {
                color: #4ade80;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            
            .dias-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }
            
            .dia-card {
                background: rgba(0, 0, 0, 0.3);
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid #4ade80;
                transition: all 0.3s;
            }
            
            .dia-card:hover {
                border-left-color: #fbbf24;
                background: rgba(0, 0, 0, 0.5);
            }
            
            .dia-data {
                font-weight: bold;
                color: #4ade80;
                margin-bottom: 5px;
            }
            
            .dia-semana {
                color: #d1d5db;
                font-size: 0.9em;
            }
            
            .prioridade {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 0.8em;
                margin-top: 5px;
                font-weight: bold;
            }
            
            .prioridade.alta {
                background: #4ade80;
                color: #0d4f1c;
            }
            
            .prioridade.media {
                background: #fbbf24;
                color: #0d4f1c;
            }
            
            .horarios-sugeridos {
                margin-top: 30px;
            }
            
            .horarios-sugeridos h3 {
                color: #4ade80;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            
            .horarios-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 10px;
            }
            
            .horario-card {
                background: rgba(0, 0, 0, 0.3);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                border: 2px solid #4ade80;
                transition: all 0.3s;
            }
            
            .horario-card:hover {
                border-color: #fbbf24;
            }
            
            .horario-valor {
                font-size: 1.5em;
                font-weight: bold;
                color: #fbbf24;
            }
            
            .erro {
                background: rgba(239, 68, 68, 0.2);
                color: #fca5a5;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                border: 2px solid #ef4444;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #d1d5db;
            }
            
            .spinner {
                border: 4px solid rgba(74, 222, 128, 0.2);
                border-top: 4px solid #4ade80;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .sonhos-populares {
                margin-top: 30px;
            }
            
            .sonhos-populares h3 {
                color: #4ade80;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            
            .sonhos-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 10px;
            }
            
            .sonho-tag {
                background: rgba(0, 0, 0, 0.3);
                padding: 10px 15px;
                border-radius: 20px;
                cursor: pointer;
                transition: all 0.3s;
                border: 2px solid #4ade80;
                text-align: center;
                color: white;
            }
            
            .sonho-tag:hover {
                border-color: #fbbf24;
                background: rgba(251, 191, 36, 0.2);
                transform: translateY(-2px);
                color: #fbbf24;
            }
            
            .btn-microfone {
                position: absolute;
                right: 15px;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(74, 222, 128, 0.2);
                border: 2px solid #4ade80;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                font-size: 1.5em;
                cursor: pointer;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .btn-microfone:hover {
                background: rgba(74, 222, 128, 0.4);
                transform: translateY(-50%) scale(1.1);
            }
            
            .btn-microfone.gravando {
                background: rgba(239, 68, 68, 0.3);
                border-color: #ef4444;
                animation: pulse 1.5s infinite;
            }
            
            @keyframes pulse {
                0%, 100% {
                    transform: translateY(-50%) scale(1);
                    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
                }
                50% {
                    transform: translateY(-50%) scale(1.1);
                    box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
                }
            }
            
            .pulse-animation {
                width: 12px;
                height: 12px;
                background: #ef4444;
                border-radius: 50%;
                animation: pulse-dot 1s infinite;
            }
            
            @keyframes pulse-dot {
                0%, 100% {
                    opacity: 1;
                    transform: scale(1);
                }
                50% {
                    opacity: 0.5;
                    transform: scale(1.2);
                }
            }
            
            .texto-transcrito {
                background: rgba(74, 222, 128, 0.1);
                border: 1px solid #4ade80;
                border-radius: 5px;
                padding: 10px;
                margin-top: 10px;
                color: #4ade80;
                font-style: italic;
            }
            
            @media (max-width: 768px) {
                .header h1 {
                    font-size: 1.8em;
                }
                
                .main-card {
                    padding: 20px;
                }
                
                .numeros-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-container">
                    <div class="logo-crown">👑</div>
                    <div>
                        <h1>LIVRO DOS SONHOS</h1>
                        <div class="subtitle">BARÃO DO BICHO</div>
                    </div>
                </div>
                <p>Informe seu sonho e receba palpites para apostas</p>
            </div>
            
            <div class="main-card">
                <form id="formSonho" onsubmit="interpretarSonho(event)">
                    <div class="input-group">
                        <label for="sonho">Descreva seu sonho:</label>
                        <div style="position: relative;">
                            <textarea 
                                id="sonho" 
                                name="sonho" 
                                placeholder="Ex: Sonhei com um leão, Sonhei com dinheiro, Sonhei com água... Ou clique no microfone para falar!"
                                required
                            ></textarea>
                            <button 
                                type="button" 
                                id="btnGravar" 
                                class="btn-microfone"
                                title="Clique para gravar áudio"
                            >
                                🎤
                            </button>
                        </div>
                        <div id="statusGravacao" style="margin-top: 10px; display: none;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div class="pulse-animation"></div>
                                <span style="color: #4ade80; font-weight: bold;">Gravando... Fale seu sonho!</span>
                            </div>
                        </div>
                        <div id="infoPermissao" style="margin-top: 10px; padding: 10px; background: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; border-radius: 5px; font-size: 0.9em; color: #9ca3af; display: none;">
                            <strong style="color: #4ade80;">💡 Dica:</strong> Ao clicar no microfone, o navegador solicitará permissão para acessar seu microfone. Clique em <strong>"Permitir"</strong> para usar a gravação de voz.
                        </div>
                    </div>
                    
                    <button type="submit" class="btn">
                        🔮 Interpretar Sonho e Gerar Palpites
                    </button>
                </form>
                
                <div id="resultado" class="resultado-container">
                    <!-- Resultado será inserido aqui via JavaScript -->
                </div>
            </div>
            
            <div class="main-card sonhos-populares">
                <h3>💭 Sonhos Populares</h3>
                <div class="sonhos-grid" id="sonhosPopulares">
                    <!-- Será preenchido via JavaScript -->
                </div>
            </div>
        </div>
        
        <script>
            // ============================================
            // FUNCIONALIDADE DE GRAVAÇÃO DE ÁUDIO
            // ============================================
            let recognition = null;
            let gravando = false;
            
            // Verificar se Web Speech API está disponível
            function verificarSuporteSpeech() {
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    recognition = new SpeechRecognition();
                    
                    recognition.lang = 'pt-BR';
                    recognition.continuous = false;
                    recognition.interimResults = false;
                    
                    recognition.onstart = function() {
                        gravando = true;
                        document.getElementById('btnGravar').classList.add('gravando');
                        document.getElementById('statusGravacao').style.display = 'block';
                        document.getElementById('btnGravar').innerHTML = '⏹️';
                    };
                    
                    recognition.onresult = function(event) {
                        const texto = event.results[0][0].transcript;
                        document.getElementById('sonho').value = texto;
                        
                        // Mostrar texto transcrito
                        mostrarTextoTranscrito(texto);
                        
                        // Parar gravação
                        pararGravacao();
                        
                        // Opcional: interpretar automaticamente
                        // interpretarSonho(new Event('submit'));
                    };
                    
                    recognition.onerror = function(event) {
                        console.error('Erro no reconhecimento:', event.error);
                        let mensagem = 'Erro ao gravar áudio. ';
                        
                        switch(event.error) {
                            case 'no-speech':
                                mensagem += 'Nenhuma fala detectada. Tente novamente.';
                                break;
                            case 'audio-capture':
                                mensagem += 'Não foi possível acessar o microfone.\\n\\nVerifique:\\n1. Se o microfone está conectado\\n2. Se outras aplicações não estão usando o microfone\\n3. Permita o acesso nas configurações do navegador';
                                break;
                            case 'not-allowed':
                            case 'service-not-allowed':
                                mensagem += 'Permissão de microfone negada.\\n\\nPara permitir:\\n1. Clique no ícone de cadeado na barra de endereços\\n2. Vá em Configurações do site ou Site settings\\n3. Permita o acesso ao Microfone\\n4. Recarregue a página e tente novamente';
                                break;
                            case 'aborted':
                                mensagem += 'Gravação interrompida.';
                                break;
                            case 'network':
                                mensagem += 'Erro de conexão. Verifique sua internet.';
                                break;
                            default:
                                mensagem += 'Erro: ' + event.error + '\\n\\nTente permitir o microfone nas configurações do navegador.';
                        }
                        
                        alert(mensagem);
                        pararGravacao();
                    };
                    
                    recognition.onend = function() {
                        pararGravacao();
                    };
                    
                    return true;
                } else {
                    return false;
                }
            }
            
            async function solicitarPermissaoMicrofone() {
                try {
                    // Verificar se a API está disponível
                    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                        // Usar API moderna
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        // Parar o stream imediatamente, só precisamos da permissão
                        stream.getTracks().forEach(track => track.stop());
                        return true;
                    }
                    
                    // Tentar fallback para versões antigas
                    const getUserMedia = navigator.getUserMedia || 
                                      navigator.webkitGetUserMedia || 
                                      navigator.mozGetUserMedia || 
                                      navigator.msGetUserMedia;
                    
                    if (getUserMedia) {
                        // Usar Promise wrapper para API antiga
                        return new Promise((resolve, reject) => {
                            getUserMedia.call(navigator, { audio: true }, 
                                (stream) => {
                                    stream.getTracks().forEach(track => track.stop());
                                    resolve(true);
                                },
                                (error) => {
                                    reject(error);
                                }
                            );
                        });
                    }
                    
                    // Se não tem getUserMedia, mas tem SpeechRecognition, pode funcionar direto
                    // A Web Speech API pode solicitar permissão automaticamente
                    return true; // Retornar true para tentar usar SpeechRecognition direto
                    
                } catch (error) {
                    console.error('Erro ao solicitar permissão:', error);
                    // Mesmo com erro, tentar usar SpeechRecognition que pode solicitar permissão
                    return true;
                }
            }
            
            async function toggleGravacao() {
                if (!recognition) {
                    if (!verificarSuporteSpeech()) {
                        alert('Seu navegador não suporta gravação de áudio. Use Chrome, Edge ou Safari.');
                        return;
                    }
                }
                
                if (gravando) {
                    recognition.stop();
                } else {
                    // Esconder dica de permissão
                    const infoPermissao = document.getElementById('infoPermissao');
                    if (infoPermissao) {
                        infoPermissao.style.display = 'none';
                    }
                    
                    // Tentar iniciar gravação diretamente
                    // A Web Speech API solicita permissão automaticamente quando necessário
                    try {
                        recognition.start();
                    } catch (e) {
                        console.error('Erro ao iniciar gravação:', e);
                        
                        // Se falhar, tentar solicitar permissão primeiro
                        try {
                            await solicitarPermissaoMicrofone();
                            // Tentar novamente
                            recognition.start();
                        } catch (e2) {
                            // Mostrar erro na interface
                            if (infoPermissao) {
                                let mensagemErro = 'Não foi possível acessar o microfone. ';
                                
                                if (e2.message && e2.message.includes('HTTPS')) {
                                    mensagemErro = '⚠️ Acesso ao microfone requer HTTPS.\\n\\nO site precisa estar em HTTPS para acessar o microfone (exceto localhost).\\n\\nSoluções:\\n1. Use localhost ao invés do IP\\n2. Configure HTTPS no servidor\\n3. Use Chrome e permita acesso inseguro (não recomendado)';
                                } else if (e2.name === 'NotAllowedError' || e2.name === 'PermissionDeniedError') {
                                    mensagemErro += 'Permissão negada. Clique no ícone de cadeado na barra de endereços e permita o acesso ao microfone.';
                                } else {
                                    mensagemErro += 'Verifique as configurações do navegador.';
                                }
                                
                                infoPermissao.innerHTML = '<strong style="color: #ef4444;">⚠️ Erro:</strong> ' + mensagemErro;
                                infoPermissao.style.borderColor = '#ef4444';
                                infoPermissao.style.background = 'rgba(239, 68, 68, 0.1)';
                                infoPermissao.style.display = 'block';
                            }
                            
                            alert('Erro ao acessar microfone.\\n\\nSe estiver usando IP (não localhost), o navegador pode bloquear o acesso.\\n\\nTente:\\n1. Acessar via localhost:8082 ao invés do IP\\n2. Ou permita o acesso no ícone de cadeado na barra de endereços');
                        }
                    }
                }
            }
            
            function pararGravacao() {
                if (recognition && gravando) {
                    recognition.stop();
                }
                gravando = false;
                document.getElementById('btnGravar').classList.remove('gravando');
                document.getElementById('statusGravacao').style.display = 'none';
                document.getElementById('btnGravar').innerHTML = '🎤';
            }
            
            function mostrarTextoTranscrito(texto) {
                let divTranscrito = document.getElementById('textoTranscrito');
                if (!divTranscrito) {
                    divTranscrito = document.createElement('div');
                    divTranscrito.id = 'textoTranscrito';
                    divTranscrito.className = 'texto-transcrito';
                    document.getElementById('sonho').parentElement.appendChild(divTranscrito);
                }
                divTranscrito.innerHTML = '✅ <strong>Texto transcrito:</strong> ' + texto;
                divTranscrito.style.display = 'block';
                
                // Remover após 5 segundos
                setTimeout(() => {
                    divTranscrito.style.display = 'none';
                }, 5000);
            }
            
            // Configurar evento do botão de gravação
            document.addEventListener('DOMContentLoaded', function() {
                const btnGravar = document.getElementById('btnGravar');
                if (btnGravar) {
                    btnGravar.addEventListener('click', toggleGravacao);
                }
            });
            
            // Verificar suporte e permissões ao carregar a página
            window.addEventListener('load', async function() {
                if (!verificarSuporteSpeech()) {
                    // Desabilitar botão se não houver suporte
                    const btnGravar = document.getElementById('btnGravar');
                    if (btnGravar) {
                        btnGravar.style.opacity = '0.5';
                        btnGravar.style.cursor = 'not-allowed';
                        btnGravar.title = 'Gravação de áudio não disponível neste navegador';
                    }
                } else {
                    // Mostrar dica de permissão na primeira vez
                    const infoPermissao = document.getElementById('infoPermissao');
                    if (infoPermissao) {
                        // Verificar se já tem permissão
                        try {
                            // Verificar se navigator.permissions está disponível
                            if (navigator.permissions && navigator.permissions.query) {
                                const permissao = await navigator.permissions.query({ name: 'microphone' });
                                if (permissao.state === 'granted') {
                                    if (infoPermissao) {
                                        infoPermissao.style.display = 'none';
                                    }
                                } else {
                                    if (infoPermissao) {
                                        infoPermissao.style.display = 'block';
                                    }
                                }
                                
                                // Ouvir mudanças na permissão
                                permissao.onchange = function() {
                                    atualizarEstadoPermissao(this.state);
                                    if (this.state === 'granted' && infoPermissao) {
                                        infoPermissao.style.display = 'none';
                                    }
                                };
                            } else {
                                // Navigator.permissions não disponível, mostrar dica
                                if (infoPermissao) {
                                    infoPermissao.style.display = 'block';
                                }
                            }
                        } catch (e) {
                            // Alguns navegadores não suportam navigator.permissions
                            // Mostrar dica por padrão
                            if (infoPermissao) {
                                infoPermissao.style.display = 'block';
                            }
                        }
                    }
                    
                    // Verificar estado da permissão
                    try {
                        if (navigator.permissions && navigator.permissions.query) {
                            const permissao = await navigator.permissions.query({ name: 'microphone' });
                            atualizarEstadoPermissao(permissao.state);
                        }
                    } catch (e) {
                        // Ignorar se não suportado
                    }
                }
            });
            
            function atualizarEstadoPermissao(estado) {
                const btnGravar = document.getElementById('btnGravar');
                if (!btnGravar) return;
                
                if (estado === 'denied') {
                    btnGravar.title = 'Permissão de microfone negada. Clique para ver instruções.';
                    btnGravar.style.borderColor = '#ef4444';
                } else if (estado === 'granted') {
                    btnGravar.title = 'Clique para gravar áudio';
                    btnGravar.style.borderColor = '#4ade80';
                } else {
                    btnGravar.title = 'Clique para gravar áudio (solicitará permissão)';
                    btnGravar.style.borderColor = '#4ade80';
                }
            }
            
            // Carregar sonhos populares ao iniciar
            async function carregarSonhosPopulares() {
                try {
                    const response = await fetch('/api/sonhos-populares');
                    const data = await response.json();
                    
                    const container = document.getElementById('sonhosPopulares');
                    container.innerHTML = '';
                    
                    data.sonhos.forEach(sonho => {
                        const tag = document.createElement('div');
                        tag.className = 'sonho-tag';
                        tag.textContent = sonho.sonho;
                        tag.onclick = () => {
                            document.getElementById('sonho').value = sonho.sonho;
                            interpretarSonho(new Event('submit'));
                        };
                        container.appendChild(tag);
                    });
                } catch (error) {
                    console.error('Erro ao carregar sonhos populares:', error);
                }
            }
            
            // Interpretar sonho
            async function interpretarSonho(event) {
                event.preventDefault();
                
                const sonho = document.getElementById('sonho').value.trim();
                if (!sonho) {
                    alert('Por favor, descreva seu sonho!');
                    return;
                }
                
                const resultadoDiv = document.getElementById('resultado');
                resultadoDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Interpretando seu sonho...</div>';
                resultadoDiv.classList.add('show');
                
                try {
                    const response = await fetch('/api/interpretar', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ sonho: sonho })
                    });
                    
                    const data = await response.json();
                    
                    if (data.encontrado) {
                        exibirResultado(data);
                    } else {
                        exibirErro(data.mensagem || 'Sonho não encontrado. Tente descrever de forma mais específica.');
                    }
                } catch (error) {
                    console.error('Erro:', error);
                    exibirErro('Erro ao interpretar sonho. Tente novamente.');
                }
            }
            
            function exibirResultado(data) {
                const resultadoDiv = document.getElementById('resultado');
                
                let html = `
                    <div class="resultado-card">
                        <div class="resultado-header">
                            <h2>🎯 Seu Palpite</h2>
                            <p>Sonho: <strong>${data.sonho_original}</strong></p>
                        </div>
                        
                        <div class="animal-info">
                            <div class="animal-nome">${data.animal}</div>
                            <div class="animal-grupo">Grupo ${data.grupo}</div>
                            <div class="animal-significado">${data.significado}</div>
                        </div>
                        
                        <div class="numeros-grid">
                            <div class="numero-card">
                                <div class="numero-tipo">Grupo</div>
                                <div class="numero-valor">${data.grupo}</div>
                            </div>
                            <div class="numero-card">
                                <div class="numero-tipo">Dezena</div>
                                <div class="numero-valor">${data.dezena}</div>
                            </div>
                            <div class="numero-card">
                                <div class="numero-tipo">Centena</div>
                                <div class="numero-valor">${data.centena}</div>
                            </div>
                            <div class="numero-card">
                                <div class="numero-tipo">Milhar</div>
                                <div class="numero-valor">${data.milhar}</div>
                            </div>
                        </div>
                        
                        <div class="dias-sugeridos">
                            <h3>📅 Dias Sugeridos para Apostar</h3>
                            <div class="dias-grid">
                `;
                
                data.dias_sugeridos.forEach(dia => {
                    const diaSemanaPt = {
                        'Monday': 'Segunda-feira',
                        'Tuesday': 'Terça-feira',
                        'Wednesday': 'Quarta-feira',
                        'Thursday': 'Quinta-feira',
                        'Friday': 'Sexta-feira',
                        'Saturday': 'Sábado',
                        'Sunday': 'Domingo'
                    }[dia.dia_semana] || dia.dia_semana;
                    
                    html += `
                        <div class="dia-card">
                            <div class="dia-data">${dia.data}</div>
                            <div class="dia-semana">${diaSemanaPt}</div>
                            <span class="prioridade ${dia.prioridade}">Prioridade ${dia.prioridade}</span>
                        </div>
                    `;
                });
                
                html += `
                            </div>
                        </div>
                        
                        <div class="horarios-sugeridos">
                            <h3>⏰ Horários Sugeridos</h3>
                            <div class="horarios-grid">
                `;
                
                data.horarios_sugeridos.forEach(horario => {
                    html += `
                        <div class="horario-card">
                            <div class="horario-valor">${horario.horario}</div>
                            <span class="prioridade ${horario.prioridade}">${horario.prioridade}</span>
                        </div>
                    `;
                });
                
                html += `
                            </div>
                        </div>
                    </div>
                `;
                
                resultadoDiv.innerHTML = html;
            }
            
            function exibirErro(mensagem) {
                const resultadoDiv = document.getElementById('resultado');
                resultadoDiv.innerHTML = `
                    <div class="erro">
                        <h3>⚠️ ${mensagem}</h3>
                        <p>Tente descrever seu sonho de forma mais específica ou use uma das opções populares abaixo.</p>
                    </div>
                `;
            }
            
            // Carregar sonhos populares ao iniciar
            carregarSonhosPopulares();
        </script>
    </body>
    </html>
    ''')

# ============================================
# ENDPOINTS API PARA INTEGRAÇÃO
# ============================================

@app.route('/api/v1/interpretar', methods=['POST'])
def api_interpretar_v1():
    """
    API v1 para interpretar um sonho
    Retorna informações completas sobre o sonho e palpites
    """
    try:
        dados = request.get_json()
        sonho = dados.get('sonho', '').strip()
        
        if not sonho:
            return jsonify({
                'sucesso': False,
                'erro': 'Sonho não fornecido',
                'encontrado': False
            }), 400
        
        logger.info(f"Interpretando sonho: {sonho}")
        resultado = livro_sonhos.interpretar_sonho(sonho)
        
        # Formato padronizado para integração
        if resultado.get('encontrado'):
            return jsonify({
                'sucesso': True,
                'encontrado': True,
                'dados': {
                    'sonho': resultado.get('sonho_original'),
                    'animal': resultado.get('animal'),
                    'grupo': resultado.get('grupo'),
                    'significado': resultado.get('significado'),
                    'numeros': {
                        'grupo': resultado.get('grupo'),
                        'dezena': resultado.get('dezena'),
                        'centena': resultado.get('centena'),
                        'milhar': resultado.get('milhar')
                    },
                    'sugestoes': {
                        'dias': resultado.get('dias_sugeridos', []),
                        'horarios': resultado.get('horarios_sugeridos', [])
                    }
                }
            })
        else:
            return jsonify({
                'sucesso': False,
                'encontrado': False,
                'mensagem': resultado.get('mensagem', 'Sonho não encontrado'),
                'sugestao': resultado.get('sugestao', '')
            })
        
    except Exception as e:
        logger.error(f"Erro ao interpretar sonho: {e}", exc_info=True)
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'encontrado': False
        }), 500

@app.route('/api/interpretar', methods=['POST'])
def api_interpretar():
    """API para interpretar um sonho (compatibilidade)"""
    try:
        dados = request.get_json()
        sonho = dados.get('sonho', '').strip()
        
        if not sonho:
            return jsonify({
                'erro': 'Sonho não fornecido',
                'encontrado': False
            }), 400
        
        logger.info(f"Interpretando sonho: {sonho}")
        resultado = livro_sonhos.interpretar_sonho(sonho)
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro ao interpretar sonho: {e}", exc_info=True)
        return jsonify({
            'erro': str(e),
            'encontrado': False
        }), 500

@app.route('/api/v1/sonhos/populares', methods=['GET'])
def api_sonhos_populares_v1():
    """
    API v1 para listar sonhos populares
    Retorna lista formatada para integração
    """
    try:
        limite = request.args.get('limite', 50, type=int)
        sonhos = livro_sonhos.listar_sonhos_populares(limite)
        
        return jsonify({
            'sucesso': True,
            'total': len(sonhos),
            'sonhos': sonhos
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar sonhos populares: {e}", exc_info=True)
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'sonhos': []
        }), 500

@app.route('/api/sonhos-populares', methods=['GET'])
def api_sonhos_populares():
    """API para listar sonhos populares (compatibilidade)"""
    try:
        limite = request.args.get('limite', 50, type=int)
        sonhos = livro_sonhos.listar_sonhos_populares(limite)
        
        return jsonify({
            'sonhos': sonhos,
            'total': len(sonhos)
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar sonhos populares: {e}", exc_info=True)
        return jsonify({
            'erro': str(e),
            'sonhos': []
        }), 500

@app.route('/api/v1/sonhos/buscar', methods=['GET'])
def api_buscar_v1():
    """
    API v1 para buscar um sonho específico
    """
    try:
        sonho = request.args.get('sonho', '').strip()
        
        if not sonho:
            return jsonify({
                'sucesso': False,
                'erro': 'Sonho não fornecido',
                'encontrado': False
            }), 400
        
        resultado = livro_sonhos.buscar_sonho(sonho)
        
        if resultado:
            return jsonify({
                'sucesso': True,
                'encontrado': True,
                'dados': resultado
            })
        else:
            return jsonify({
                'sucesso': False,
                'encontrado': False,
                'mensagem': 'Sonho não encontrado'
            })
        
    except Exception as e:
        logger.error(f"Erro ao buscar sonho: {e}", exc_info=True)
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'encontrado': False
        }), 500

@app.route('/api/buscar', methods=['GET'])
def api_buscar():
    """API para buscar um sonho específico (compatibilidade)"""
    try:
        sonho = request.args.get('sonho', '').strip()
        
        if not sonho:
            return jsonify({
                'erro': 'Sonho não fornecido',
                'encontrado': False
            }), 400
        
        resultado = livro_sonhos.buscar_sonho(sonho)
        
        if resultado:
            return jsonify({
                'encontrado': True,
                'resultado': resultado
            })
        else:
            return jsonify({
                'encontrado': False,
                'mensagem': 'Sonho não encontrado'
            })
        
    except Exception as e:
        logger.error(f"Erro ao buscar sonho: {e}", exc_info=True)
        return jsonify({
            'erro': str(e),
            'encontrado': False
        }), 500

@app.route('/api/v1/audio/transcrever', methods=['POST'])
def api_transcrever_audio():
    """
    API para transcrever áudio para texto
    Requer: arquivo de áudio no formato multipart/form-data
    """
    try:
        # Verificar se há arquivo de áudio
        if 'audio' not in request.files:
            return jsonify({
                'sucesso': False,
                'erro': 'Arquivo de áudio não fornecido'
            }), 400
        
        arquivo_audio = request.files['audio']
        
        if arquivo_audio.filename == '':
            return jsonify({
                'sucesso': False,
                'erro': 'Nenhum arquivo selecionado'
            }), 400
        
        # Verificar extensão do arquivo
        extensoes_permitidas = ['.wav', '.mp3', '.ogg', '.webm', '.m4a']
        nome_arquivo = arquivo_audio.filename.lower()
        
        if not any(nome_arquivo.endswith(ext) for ext in extensoes_permitidas):
            return jsonify({
                'sucesso': False,
                'erro': f'Formato não suportado. Use: {", ".join(extensoes_permitidas)}'
            }), 400
        
        # Tentar usar biblioteca de speech recognition (opcional)
        try:
            import speech_recognition as sr
            import tempfile
            import os
            
            # Salvar arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                arquivo_audio.save(tmp_file.name)
                caminho_temp = tmp_file.name
            
            try:
                # Inicializar reconhecedor
                r = sr.Recognizer()
                
                # Carregar áudio
                with sr.AudioFile(caminho_temp) as source:
                    audio_data = r.record(source)
                
                # Reconhecer fala (usando Google Speech Recognition)
                try:
                    texto = r.recognize_google(audio_data, language='pt-BR')
                    
                    return jsonify({
                        'sucesso': True,
                        'texto': texto,
                        'idioma': 'pt-BR'
                    })
                except sr.UnknownValueError:
                    return jsonify({
                        'sucesso': False,
                        'erro': 'Não foi possível entender o áudio'
                    }), 400
                except sr.RequestError as e:
                    return jsonify({
                        'sucesso': False,
                        'erro': f'Erro no serviço de reconhecimento: {str(e)}'
                    }), 500
                    
            finally:
                # Remover arquivo temporário
                if os.path.exists(caminho_temp):
                    os.remove(caminho_temp)
                    
        except ImportError:
            # Se biblioteca não estiver instalada, retornar erro informativo
            return jsonify({
                'sucesso': False,
                'erro': 'Reconhecimento de voz não disponível no servidor',
                'instrucoes': 'Para habilitar, instale: pip install SpeechRecognition pydub',
                'alternativa': 'Use a funcionalidade de gravação do navegador (Web Speech API)'
            }), 503
        
    except Exception as e:
        logger.error(f"Erro ao transcrever áudio: {e}", exc_info=True)
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/v1/status', methods=['GET'])
def api_status():
    """Status da API"""
    # Verificar se speech recognition está disponível
    speech_available = False
    try:
        import speech_recognition as sr
        speech_available = True
    except ImportError:
        pass
    
    return jsonify({
        'sucesso': True,
        'status': 'online',
        'versao': '1.0.0',
        'recursos': {
            'speech_recognition_backend': speech_available,
            'web_speech_api': 'Recomendado (navegador)'
        },
        'endpoints': {
            'interpretar': '/api/v1/interpretar',
            'sonhos_populares': '/api/v1/sonhos/populares',
            'buscar': '/api/v1/sonhos/buscar',
            'transcrever_audio': '/api/v1/audio/transcrever',
            'status': '/api/v1/status'
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8082, help='Porta do servidor (padrão: 8082)')
    parser.add_argument('--host', default='0.0.0.0', help='Host (0.0.0.0 para VPS)')
    args = parser.parse_args()
    
    logger.info(f"🚀 Servidor Livro dos Sonhos iniciando em http://{args.host}:{args.port}")
    logger.info(f"📖 Painel: http://{args.host}:{args.port}/")
    logger.info(f"🔌 API v1: http://{args.host}:{args.port}/api/v1/interpretar")
    logger.info(f"📊 Status: http://{args.host}:{args.port}/api/v1/status")
    
    app.run(host=args.host, port=args.port, debug=False)
