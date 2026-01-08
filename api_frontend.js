/**
 * API Client para Frontend - Jogo do Bicho
 * Use este arquivo no seu frontend para conectar com a API
 */

const API_BASE_URL = 'http://seu-servidor:5001/api'; // Ajuste para sua URL

class ApostasAPI {
  /**
   * Criar uma nova aposta
   * @param {Object} aposta - Dados da aposta
   * @returns {Promise<Object>} Resultado da criação
   */
  static async criarAposta(aposta) {
    try {
      const response = await fetch(`${API_BASE_URL}/apostas`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': this.getAuthHeader()
        },
        body: JSON.stringify(aposta)
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.erro || 'Erro ao criar aposta');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao criar aposta:', error);
      throw error;
    }
  }

  /**
   * Consultar saldo do usuário
   * @param {number} usuarioId - ID do usuário
   * @returns {Promise<Object>} Dados do saldo
   */
  static async consultarSaldo(usuarioId) {
    try {
      const response = await fetch(`${API_BASE_URL}/usuarios/${usuarioId}/saldo`, {
        headers: {
          'Authorization': this.getAuthHeader()
        }
      });
      
      if (!response.ok) {
        throw new Error('Erro ao consultar saldo');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao consultar saldo:', error);
      throw error;
    }
  }

  /**
   * Listar apostas de um usuário
   * @param {number} usuarioId - ID do usuário
   * @returns {Promise<Array>} Lista de apostas
   */
  static async listarApostas(usuarioId) {
    try {
      const response = await fetch(`${API_BASE_URL}/apostas/usuario/${usuarioId}`, {
        headers: {
          'Authorization': this.getAuthHeader()
        }
      });
      
      if (!response.ok) {
        throw new Error('Erro ao listar apostas');
      }
      
      const data = await response.json();
      return data.apostas || [];
    } catch (error) {
      console.error('Erro ao listar apostas:', error);
      throw error;
    }
  }

  /**
   * Ver detalhes de uma aposta
   * @param {number} apostaId - ID da aposta
   * @returns {Promise<Object>} Dados da aposta
   */
  static async verAposta(apostaId) {
    try {
      const response = await fetch(`${API_BASE_URL}/apostas/${apostaId}`, {
        headers: {
          'Authorization': this.getAuthHeader()
        }
      });
      
      if (!response.ok) {
        throw new Error('Aposta não encontrada');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao ver aposta:', error);
      throw error;
    }
  }

  /**
   * Listar resultados
   * @returns {Promise<Array>} Lista de resultados
   */
  static async listarResultados() {
    try {
      const response = await fetch(`${API_BASE_URL}/resultados`);
      
      if (!response.ok) {
        throw new Error('Erro ao listar resultados');
      }
      
      const data = await response.json();
      return data.resultados || [];
    } catch (error) {
      console.error('Erro ao listar resultados:', error);
      throw error;
    }
  }

  /**
   * Forçar liquidação de resultados
   * @returns {Promise<Object>} Resultado da liquidação
   */
  static async liquidarResultados() {
    try {
      const response = await fetch(`${API_BASE_URL}/resultados/liquidar`, {
        method: 'POST',
        headers: {
          'Authorization': this.getAuthHeader()
        }
      });
      
      if (!response.ok) {
        throw new Error('Erro ao liquidar resultados');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao liquidar resultados:', error);
      throw error;
    }
  }

  /**
   * Status do monitor
   * @returns {Promise<Object>} Status do monitor
   */
  static async statusMonitor() {
    try {
      const response = await fetch(`${API_BASE_URL}/monitor/status`);
      return await response.json();
    } catch (error) {
      console.error('Erro ao verificar status:', error);
      throw error;
    }
  }

  /**
   * Obter header de autenticação
   * @returns {string} Header Authorization
   */
  static getAuthHeader() {
    // Implementar sua lógica de autenticação
    const token = localStorage.getItem('auth_token');
    return token ? `Bearer ${token}` : '';
  }

  /**
   * Configurar URL base da API
   * @param {string} url - URL base da API
   */
  static setBaseURL(url) {
    API_BASE_URL = url;
  }
}

// Exportar para uso
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ApostasAPI;
}

